import mimetypes
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, unquote

@xframe_options_exempt
def folke_kontext_api(request):
    """
    Returns the content from the isof-sitevision-path that is specified
    in the params "path" with an appropriate MIME type.
    """
    path = request.GET.get("path")
    
    def guess_mime_type(url):
        # Använder urlparse för att dela upp URL:en i komponenter
        parsed_url = urlparse(url)
        # Hämtar vägen till filen och avkodar eventuell URL-kodning
        path = unquote(parsed_url.path)
        # Använder endast filnamnet efter den sista slashen för MIME-typgissning
        mime_type, _ = mimetypes.guess_type(path)
        if path.endswith('.woff'):
            mime_type = 'font/woff'
        elif path.endswith('.woff2'):
            mime_type = 'font/woff2'
        return mime_type

    if not path:
        return JsonResponse({"error": "Missing path parameter"}, status=400)

    try:
        base_url = "https://www.isof.se/"
        full_url = f"{base_url}{path}"

        # Set a timeout for the request
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()  # This will raise an HTTPError for bad responses

        # Guess the MIME type based on the file extension
        mime_type = guess_mime_type(full_url)
        if mime_type is None:
            # Default to 'text/html' if MIME type could not be guessed
            mime_type = "text/html"

        # Handle HTML content
        if mime_type == 'text/html':
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all <a> and <img> tags to update their 'href' and 'src' attributes
            for a in soup.find_all('a', href=True):
                if not a['href'].startswith(('http://', 'https://', '//')):
                    a['href'] = "/folke_kontext_api?path=" + a['href'].lstrip('/')
                else:
                    a['href'] = "/folke_kontext_api?path=" + a['href'].removeprefix('https://www.isof.se/')
                    
            for img in soup.find_all('img', src=True):
                # Kontrollera om src-attributet är en data-URI
                if img['src'].startswith('data:image'):
                    continue  # Hoppa över dessa eftersom de inte behöver ändras

                if not img['src'].startswith(('http://', 'https://', '//')):
                    img['src'] = base_url + img['src'].lstrip('/')

                # Kontrollera och uppdatera srcset-attributet om det finns
                if img.has_attr('srcset'):
                    new_srcset = []
                    # Dela upp srcset-värdet i en lista baserat på kommatecken
                    srcset_values = img['srcset'].split(',')
                    for value in srcset_values:
                        # Dela upp varje värde vid mellanslag för att separera URL:en från storleksangivelsen
                        parts = value.strip().split(' ')
                        # Kontrollera och uppdatera URL:en om nödvändigt
                        if not parts[0].startswith(('http://', 'https://', '//', 'data:image')):
                            parts[0] = base_url + parts[0].lstrip('/')
                        # Lägg till den uppdaterade URL:en och storleksangivelsen till new_srcset
                        new_srcset.append(' '.join(parts))
                    # Uppdatera srcset-attributet med de modifierade värdena
                    img['srcset'] = ', '.join(new_srcset)

            for script in soup.find_all('script', src=True):
                if not script['src'].startswith(('http://', 'https://', '//')):
                    script['src'] = "/folke_kontext_api?path=" + script['src'].lstrip('/')
                else:
                    script['src'] = "/folke_kontext_api?path=" + script['src'].removeprefix('https://www.isof.se/')

            for link in soup.find_all('link', href=True):
                if not link['href'].startswith(('http://', 'https://', '//')):
                    link['href'] = "/folke_kontext_api?path=" + link['href'].lstrip('/')
                else:
                    link['href'] = "/folke_kontext_api?path=" + link['href'].removeprefix('https://www.isof.se/')

            for use in soup.find_all('use', {'xlink:href': True}):
                xlink_href = use['xlink:href']
                if not xlink_href.startswith(('http://', 'https://', '//')):
                    use['xlink:href'] = "/folke_kontext_api?path=" + xlink_href.lstrip('/')
                else:
                    use['xlink:href'] = "/folke_kontext_api?path=" + xlink_href.removeprefix('https://www.isof.se/')

            # Kontrollera om det finns en <head> tagg, annars skapa en
            head_tag = soup.head
            if head_tag is None:
                head_tag = soup.new_tag("head")
                soup.html.insert(0, head_tag)

            # Skapa och lägg till <script> taggen för iframe-postMessage i <head>
            script_tag = soup.new_tag("script")
            script_tag.string = """
            window.parent.postMessage({ newSrc: window.location.href }, '*');
            """
            head_tag.append(script_tag)

            # Return modified HTML content
            return HttpResponse(str(soup), content_type=mime_type)

        # Handle CSS content
        elif mime_type == 'text/css':
            # Läs in CSS-innehållet som en sträng
            css_content = response.content.decode('utf-8')

            # Använd reguljära uttryck för att hitta och ersätta alla URL-vägar
            import re
            url_pattern = re.compile(r'url\(([^)]+)\)')
            
            def replace_url(match):
                url = match.group(1).strip('\'"')  # Ta bort eventuella citationstecken runt URL:en
                if url.startswith('data:image'):
                    return f'url("{url}")'  # Returnera data-URI oförändrad
                if not url.startswith(('http://', 'https://', '//')):
                    new_url = "/folke_kontext_api?path=" + url.lstrip('/')
                else:
                    new_url = "/folke_kontext_api?path=" + url.removeprefix('https://www.isof.se/')
                return f'url("{new_url}")'

            # Ersätt alla förekomster av URL:er i CSS-innehållet
            modified_css = url_pattern.sub(replace_url, css_content)

            # Returnera det modifierade CSS-innehållet
            return HttpResponse(modified_css, content_type='text/css')
        
        # Handle SVG directly
        elif mime_type == 'image/svg+xml':
            return HttpResponse(response.content, content_type=mime_type)

        else:
            # Return the response content for other types
            return HttpResponse(response.content, content_type=mime_type)

    except requests.exceptions.Timeout:
        return JsonResponse({"error": "The request timed out"}, status=504)
    except requests.exceptions.HTTPError as e:
        return JsonResponse(
            {"error": f"HTTP Error: {e}"}, status=e.response.status_code
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Request exception: {e}"}, status=500)
    
def modify_css_urls(css_content):
    url_pattern = re.compile(r'url\(([^)]+)\)')

    def url_replacer(match):
        url = match.group(1).strip('\'"')  # Ta bort eventuella citationstecken runt URL:en

        # Hantera data-URI och andra scheman som inte bör modifieras
        if url.startswith(('data:', 'about:', '#')):
            return f'url({url})'

        # Modifiera URL för absoluta och relativa länkar
        if not url.startswith(('http://', 'https://', '//')):
            # Hantera relativa URL:er
            return f'url(/folke_kontext_api?path={url.lstrip("/")})'
        else:
            # Hantera absoluta URL:er men ta bort en specifik bas-URL om den finns
            new_url = url.removeprefix('https://www.isof.se/')
            return f'url(/folke_kontext_api?path={new_url})'

    # Använd re.sub för att ersätta alla instanser effektivt
    return url_pattern.sub(url_replacer, css_content)
