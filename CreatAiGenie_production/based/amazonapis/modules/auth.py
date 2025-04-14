import logging
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .client import AmazonAdsAPIClient

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auth_url(request):
    """
    Generate Amazon Ads Authorization URL.
    
    Returns:
        JsonResponse: Authorization URL for Amazon Ads OAuth flow
    """
    try:
        client = AmazonAdsAPIClient()
        auth_url = client.get_auth_url()
        logger.info(f"Generated auth URL for user {request.user.id}")
        return JsonResponse({"auth_url": auth_url})
    except Exception as e:
        logger.error(f"Error generating auth URL: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exchange_auth_code(request):
    """
    Exchange Authorization Code for Access Token.
    
    Query Parameters:
        code (str): Authorization code from OAuth redirect
    
    Returns:
        JsonResponse: Success message or error details
    """
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code is required"}, status=400)
    
    try:
        client = AmazonAdsAPIClient()
        token_data = client.exchange_auth_code(code)
        
        # Store tokens securely - in a real app, save to database associated with user
        # For this example, we're just returning a success message
        logger.info(f"Successfully exchanged auth code for user {request.user.id}")
        
        return JsonResponse({
            "success": True,
            "message": "Authentication successful"
        })
    except ValueError as e:
        logger.error(f"Auth code exchange error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during auth code exchange: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_access_token(request):
    """
    Refresh Access Token.
    
    Returns:
        JsonResponse: Success message or error details
    """
    try:
        client = AmazonAdsAPIClient()
        client.refresh_access_token()
        logger.info(f"Successfully refreshed token for user {request.user.id}")
        return JsonResponse({"success": True, "message": "Token refreshed successfully"})
    except ValueError as e:
        logger.error(f"Token refresh error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
