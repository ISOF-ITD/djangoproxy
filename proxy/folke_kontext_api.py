import mimetypes
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
from bs4 import BeautifulSoup

@xframe_options_exempt
def folke_kontext_api(request):
    """
    Returns the content from the isof-sitevision-path that is specified
    in the params "path" with an appropriate MIME type.
    """
    path = request.GET.get("path")

    if not path:
        return JsonResponse({"error": "Missing path parameter"}, status=400)

    try:
        base_url = "https://www.isof.se/"
        full_url = f"{base_url}{path}"

        # Set a timeout for the request
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()  # This will raise an HTTPError for bad responses

        # Parse the response content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> and <img> tags to update their 'href' and 'src' attributes
        for a in soup.find_all('a', href=True):
            if not a['href'].startswith(('http://', 'https://', '//')):
                a['href'] = "/folke_kontext_api?path=" + a['href'].lstrip('/')
            else:
                a['href'] = "/folke_kontext_api?path=" + a['href'].removeprefix('https://www.isof.se/')
                
        for img in soup.find_all('img', src=True):
            # Uppdatera src-attributet
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
                    if not parts[0].startswith(('http://', 'https://', '//')):
                        parts[0] = base_url + parts[0].lstrip('/')
                    # Lägg till den uppdaterade URL:en och storleksangivelsen till new_srcset
                    new_srcset.append(' '.join(parts))
                # Uppdatera srcset-attributet med de modifierade värdena
                img['srcset'] = ', '.join(new_srcset)

        for script in soup.find_all('script', src=True):
            if not script['src'].startswith(('http://', 'https://', '//')):
                script['src'] = base_url + script['src'].lstrip('/')

        for link in soup.find_all('link', href=True):
            if not link['href'].startswith(('http://', 'https://', '//')):
                link['href'] = base_url + link['href'].lstrip('/')

        for use in soup.find_all('use', {'xlink:href': True}):
            xlink_href = use['xlink:href']
            if not xlink_href.startswith(('http://', 'https://', '//')):
                use['xlink:href'] = "/folke_kontext_api?path=" + xlink_href.lstrip('/')
            else:
                use['xlink:href'] = "/folke_kontext_api?path=" + xlink_href.removeprefix('https://www.isof.se/')

        # Guess the MIME type based on the file extension
        mime_type, _ = mimetypes.guess_type(full_url)
        if mime_type is None:
            # Default to 'text/html' if MIME type could not be guessed
            mime_type = "text/html"

        # Return modified HTML content
        return HttpResponse(str(soup), content_type=mime_type)

    except requests.exceptions.Timeout:
        return JsonResponse({"error": "The request timed out"}, status=504)
    except requests.exceptions.HTTPError as e:
        return JsonResponse(
            {"error": f"HTTP Error: {e}"}, status=e.response.status_code
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Request exception: {e}"}, status=500)
