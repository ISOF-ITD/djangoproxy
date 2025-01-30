import json
import logging
from django.http import JsonResponse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from secrets_env import folke_sok  # Importerar din JSON-nyckel
from datetime import timedelta
from django.utils import timezone  # Importera Django's timezone-modul

# Konfigurera logger
logger = logging.getLogger(__name__)

def contains_excluded_substring(keys, excluded_substrings):
    """
    Kontrollera om någon av nyckelorden innehåller någon av de exkluderade substrängarna.
    """
    for key in keys:
        key_lower = key.lower()
        for excluded in excluded_substrings:
            if excluded in key_lower:
                return True
    return False

def get_search_keywords_api(request):
    try:
        # Skapa autentisering
        credentials = service_account.Credentials.from_service_account_info(
            folke_sok,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )

        # Anslut till API
        service = build("webmasters", "v3", credentials=credentials)

        # Webbplats-URL (se till att den stämmer exakt!)
        site_url = "https://sok.folke.isof.se/"

        # Dynamisk datumhantering
        # Sätt end_date till igår
        yesterday = (timezone.now() - timedelta(days=1)).date()
        end_date = yesterday.strftime('%Y-%m-%d')

        # Sätt start_date till 90 dagar före end_date
        start_date = (yesterday - timedelta(days=90)).strftime('%Y-%m-%d')

        # Skapa förfrågan
        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 100  # Justerat rowLimit efter behov
        }

        # Skicka API-anropet
        response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()

        # 🔍 Logga hela svaret i terminalen
        logger.info("Full API Response: %s", json.dumps(response, indent=2))

        # Hämta rader från svaret
        rows = response.get("rows", [])

        # Filtrera rader där 'clicks' > 0
        filtered_rows = [row for row in rows if row.get("clicks", 0) > 0]

        return JsonResponse({"data": filtered_rows}, safe=False)

        # # Definiera substrängar som ska exkluderas (i lowercase för case-insensitive jämförelse)
        # excluded_substrings = ["folke", "isof"]

        # # Filtrera bort rader där någon av nyckelorden innehåller exkluderade substrängar
        # final_filtered_rows = [
        #     row for row in filtered_rows
        #     if not contains_excluded_substring(row.get("keys", []), excluded_substrings)
        # ]
        #
        # return JsonResponse({"data": final_filtered_rows}, safe=False)

    except HttpError as http_err:
        # Logga HTTP-fel
        logger.error("HTTP error occurred: %s", http_err)
        return JsonResponse({"error": "HTTP error occurred: {}".format(http_err)}, status=500)
    except Exception as e:
        # Logga andra fel
        logger.error("An unexpected error occurred: %s", e)
        return JsonResponse({"error": "An unexpected error occurred: {}".format(e)}, status=500)
