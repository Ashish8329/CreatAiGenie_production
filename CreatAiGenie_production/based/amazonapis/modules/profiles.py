import logging
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .client import AmazonAdsAPIClient

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profiles(request):
    """
    Retrieve available profiles from Amazon Ads API.
    
    Headers:
        Amazon-Advertising-API-Scope (optional): Profile ID
    
    Returns:
        JsonResponse: List of profiles or error details
    """
    try:
        # Get the user's tokens from the database
        from based.models import AmazonAdsToken
        try:
            token_obj = AmazonAdsToken.objects.get(user=request.user)
            # Create client with the tokens from the database
            client = AmazonAdsAPIClient(
                access_token=token_obj.access_token,
                refresh_token=token_obj.refresh_token
            )
        except AmazonAdsToken.DoesNotExist:
            logger.error(f"No Amazon Ads tokens found for user {request.user.id}")
            return JsonResponse({"error": "No Amazon Ads tokens found. Please authenticate first."}, status=400)
        
        headers = client.get_request_headers()
        
        response = client._make_request(
            "GET", 
            f"{client.API_BASE_URL}/v2/profiles", 
            headers=headers
        )
        
        logger.info(f"Successfully retrieved profiles for user {request.user.id}")
        return JsonResponse(response, safe=False)
    except ValueError as e:
        logger.error(f"Error retrieving profiles: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error retrieving profiles: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
