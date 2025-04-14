"""
Amazon Advertising API Integration
Provides endpoints for authentication, profile management, and report generation.
"""

# Import views from modules
from based.amazonapis.modules.auth import get_auth_url, exchange_auth_code, refresh_access_token
from based.amazonapis.modules.profiles import get_profiles
from based.amazonapis.modules.reports import request_report, check_report_status, request_keyword_report

# Export all views
__all__ = [
    'get_auth_url',
    'exchange_auth_code', 
    'refresh_access_token',
    'get_profiles',
    'request_report',
    'request_keyword_report',
    'check_report_status',
]


# # [2025-03-30]
# # Author: Shivam and Rajesh
# # Description: Added Logic to authenticate amzon seller account and to fetch profiles from it.
# # Added only for Campaign data

# import requests
# import json
# from django.http import JsonResponse
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.permissions import AllowAny

# # Amazon Ads API Credentials
# CLIENT_ID = settings.AMAZON_ADS_CLIENT_ID
# CLIENT_SECRET = settings.AMAZON_ADS_CLIENT_SECRET
# REDIRECT_URI = settings.AMAZON_ADS_REDIRECT_URI
# TOKEN_URL = "https://api.amazon.com/auth/o2/token"
# REPORT_API_BASE = "https://advertising-api-eu.amazon.com/reporting/reports"

# # In-memory storage for tokens (use a database in production)
# ACCESS_TOKEN = None
# REFRESH_TOKEN = None

# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def get_auth_url(request):
#     """Generate Amazon Ads Authorization URL"""
#     auth_url = (
#         f"https://www.amazon.com/ap/oa?scope=advertising::campaign_management"
#         f"&response_type=code&client_id={CLIENT_ID}&state=State&redirect_uri={REDIRECT_URI}"
#     )
#     return JsonResponse({"auth_url": auth_url})

# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def exchange_auth_code(request):
#     """Exchange Authorization Code for Access Token"""
#     global ACCESS_TOKEN, REFRESH_TOKEN
#     code = request.GET.get("code")
#     if not code:
#         return JsonResponse({"error": "Authorization code is required"}, status=400)
    
#     payload = {
#         "grant_type": "authorization_code",
#         "code": code,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "redirect_uri": REDIRECT_URI,
#     }
#     response = requests.post(TOKEN_URL, data=payload)
#     data = response.json()

#     if "access_token" in data:
#         ACCESS_TOKEN = data["access_token"]
#         REFRESH_TOKEN = data.get("refresh_token")
#         return JsonResponse({"access_token": ACCESS_TOKEN, "refresh_token": REFRESH_TOKEN})
#     else:
#         return JsonResponse({"error": "Failed to fetch access token", "details": data}, status=400)

# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def refresh_access_token(request):
#     """Refresh Access Token"""
#     global ACCESS_TOKEN, REFRESH_TOKEN
#     if not REFRESH_TOKEN:
#         return JsonResponse({"error": "No refresh token available"}, status=400)
    
#     payload = {
#         "grant_type": "refresh_token",
#         "refresh_token": REFRESH_TOKEN,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#     }
#     response = requests.post(TOKEN_URL, data=payload)
#     data = response.json()

#     if "access_token" in data:
#         ACCESS_TOKEN = data["access_token"]
#         return JsonResponse({"access_token": ACCESS_TOKEN})
#     else:
#         return JsonResponse({"error": "Failed to refresh token", "details": data}, status=400)

# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def get_profiles(request):
#     """Retrieve available profiles from Amazon Ads API"""

#     if "Authorization" not in request.headers:
#         return JsonResponse({"error": "Missing Authorization header"}, status=401)

#     if "Amazon-Advertising-API-ClientId" not in request.headers:
#         return JsonResponse({"error": "Missing Amazon-Advertising-API-ClientId header"}, status=401)

#     headers = {
#         "Authorization": request.headers.get("Authorization"),
#         "Amazon-Advertising-API-ClientId": request.headers.get("Amazon-Advertising-API-ClientId")
#     }

#     print("Headers Sent from Postman:", headers)  # Debugging

#     response = requests.get("https://advertising-api-eu.amazon.com/v2/profiles", headers=headers)

#     print("Profiles Response:", response.status_code, response.text)  # Debugging

#     if response.status_code == 200:
#         return JsonResponse(response.json(), safe=False)
#     else:
#         return JsonResponse({"error": "Failed to fetch profiles", "details": response.json()}, status=response.status_code)

# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def request_report(request):
#     """Request an Amazon Ads Report"""

#     # Ensure Authorization & ClientId headers are provided
#     if "Authorization" not in request.headers:
#         return JsonResponse({"error": "Missing Authorization header"}, status=401)

#     if "Amazon-Advertising-API-ClientId" not in request.headers:
#         return JsonResponse({"error": "Missing Amazon-Advertising-API-ClientId header"}, status=401)

#     if "Amazon-Advertising-API-Scope" not in request.headers:
#         return JsonResponse({"error": "Missing Amazon-Advertising-API-Scope header (profileId)"}, status=401)

#     headers = {
#         "Authorization": request.headers.get("Authorization"),
#         "Amazon-Advertising-API-ClientId": request.headers.get("Amazon-Advertising-API-ClientId"),
#         "Amazon-Advertising-API-Scope": request.headers.get("Amazon-Advertising-API-Scope"),
#         "Content-Type": "application/json"
#     }

#     try:
#         payload = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     # Debugging print statements
#     print("Headers Sent:", headers)
#     print("Payload Sent:", payload)

#     response = requests.post(REPORT_API_BASE, headers=headers, json=payload)

#     print("Report Request Response:", response.status_code, response.text)  # Debugging

#     if response.status_code in [200, 202]:
#         return JsonResponse(response.json())
#     else:
#         return JsonResponse({"error": "Failed to request report", "details": response.json()}, status=response.status_code)

# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def check_report_status(request, report_id):
#     """Check Report Status from Amazon Ads API"""

#     # Ensure required headers are provided
#     if "Authorization" not in request.headers:
#         return JsonResponse({"error": "Missing Authorization header"}, status=401)

#     if "Amazon-Advertising-API-ClientId" not in request.headers:
#         return JsonResponse({"error": "Missing Amazon-Advertising-API-ClientId header"}, status=401)

#     if "Amazon-Advertising-API-Scope" not in request.headers:
#         return JsonResponse({"error": "Missing Amazon-Advertising-API-Scope header (profileId)"}, status=401)

#     headers = {
#         "Authorization": request.headers.get("Authorization"),
#         "Content-Type": "application/json",
#         "Amazon-Advertising-API-ClientId": request.headers.get("Amazon-Advertising-API-ClientId"),
#         "Amazon-Advertising-API-Scope": request.headers.get("Amazon-Advertising-API-Scope"),
#     }

#     report_status_url = f"{REPORT_API_BASE}/{report_id}"

#     # Debugging print statements
#     print("Headers Sent:", headers)
#     print("Requesting Report Status from:", report_status_url)

#     response = requests.get(report_status_url, headers=headers)

#     print("Report Status Response:", response.status_code, response.text)  # Debugging

#     if response.status_code == 200:
#         return JsonResponse(response.json())
#     else:
#         return JsonResponse(
#             {"error": "Failed to get report status", "details": response.json()},
#             status=response.status_code,
#         )

# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def download_report(request, report_id):
#     """Download Report File"""
#     global ACCESS_TOKEN
#     if not ACCESS_TOKEN:
#         return JsonResponse({"error": "Access token is missing"}, status=401)

#     headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
#     response = requests.get(f"{REPORT_API_BASE}/{report_id}/download", headers=headers)

#     if response.status_code == 200:
#         return JsonResponse(response.json())
#     else:
#         return JsonResponse({"error": "Failed to download report", "details": response.json()}, status=response.status_code)
    





# import requests
# import json
# from django.http import JsonResponse
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.permissions import AllowAny

# # Amazon API Endpoints
# TOKEN_URL = "https://api.amazon.com/auth/o2/token"
# REPORT_API_BASE = "https://advertising-api-eu.amazon.com/reporting/reports"

# # Token Storage (Consider using a database instead)
# ACCESS_TOKEN = None
# REFRESH_TOKEN = settings.AMAZON_ADS_REFRESH_TOKEN

# def get_access_token():
#     """Refresh the Amazon Ads API Access Token"""
#     global ACCESS_TOKEN, REFRESH_TOKEN

#     if not REFRESH_TOKEN:
#         return None

#     payload = {
#         "grant_type": "refresh_token",
#         "refresh_token": REFRESH_TOKEN,
#         "client_id": settings.AMAZON_ADS_CLIENT_ID,
#         "client_secret": settings.AMAZON_ADS_CLIENT_SECRET,
#     }

#     response = requests.post(TOKEN_URL, data=payload)
#     data = response.json()

#     if "access_token" in data:
#         ACCESS_TOKEN = data["access_token"]
#         return ACCESS_TOKEN
#     return None

# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def request_report(request):
#     """Request an Amazon Ads Report via Django"""

#     global ACCESS_TOKEN
#     if not ACCESS_TOKEN:
#         ACCESS_TOKEN = get_access_token()
#         if not ACCESS_TOKEN:
#             return JsonResponse({"error": "Failed to retrieve access token"}, status=401)

#     # Extract headers
#     profile_id = request.headers.get("Amazon-Advertising-API-Scope")
#     client_id = settings.AMAZON_ADS_CLIENT_ID

#     if not profile_id:
#         return JsonResponse({"error": "Missing Amazon-Advertising-API-Scope (profileId) in headers"}, status=400)

#     headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Amazon-Advertising-API-ClientId": client_id,
#         "Amazon-Advertising-API-Scope": profile_id,
#         "Content-Type": "application/json"
#     }

#     try:
#         payload = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     # Debugging Output
#     print("Headers Sent:", headers)
#     print("Payload Sent:", payload)

#     # Forward request to Amazon API
#     response = requests.post(REPORT_API_BASE, headers=headers, json=payload)

#     print("Report Request Response:", response.status_code, response.text)

#     if response.status_code in [200, 202]:
#         return JsonResponse(response.json())
#     else:
#         return JsonResponse({"error": "Failed to request report", "details": response.json()}, status=response.status_code)

# import requests
# from django.http import JsonResponse
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.permissions import AllowAny

# REPORT_API_BASE = "https://advertising-api.amazon.com/v2/reports"

# @api_view(['GET'])
# @authentication_classes([])
# @permission_classes([AllowAny])
# def check_report_status(request, report_id):
#     """Check Report Status from Amazon Ads API"""

#     # Extract headers
#     auth_token = request.headers.get("Authorization")
#     client_id = request.headers.get("Amazon-Advertising-API-ClientId")
#     profile_id = request.headers.get("Amazon-Advertising-API-Scope")

#     # Validate headers
#     missing_headers = []
#     if not auth_token:
#         missing_headers.append("Authorization")
#     if not client_id:
#         missing_headers.append("Amazon-Advertising-API-ClientId")
#     if not profile_id:
#         missing_headers.append("Amazon-Advertising-API-Scope")

#     if missing_headers:
#         return JsonResponse({"error": f"Missing headers: {', '.join(missing_headers)}"}, status=401)

#     # Construct request headers
#     headers = {
#         "Authorization": auth_token,
#         "Content-Type": "application/json",
#         "Amazon-Advertising-API-ClientId": client_id,
#         "Amazon-Advertising-API-Scope": profile_id,
#     }

#     # Build report status URL
#     report_status_url = f"{REPORT_API_BASE}/{report_id}"

#     try:
#         response = requests.get(report_status_url, headers=headers)
#         response_data = response.json()  # Convert response to JSON

#         if response.status_code == 200:
#             return JsonResponse(response_data)
#         elif response.status_code == 401:
#             return JsonResponse({"error": "Unauthorized access", "details": response_data}, status=401)
#         else:
#             return JsonResponse({"error": "Failed to get report status", "details": response_data}, status=response.status_code)

#     except requests.RequestException as e:
#         return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
