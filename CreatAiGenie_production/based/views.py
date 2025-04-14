import os
import logging
from django.views.generic import TemplateView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status,viewsets, status, filters, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from requests.exceptions import RequestException, Timeout, ConnectionError
from django.utils import timezone
from based.amazonapis.modules.client import AmazonAdsAPIClient
# from .amazonapis import ad_group_report
# from amazonapis.
logger = logging.getLogger(__name__)


from .models import (
    UserAuthentication,
    UserProfile,
    SubscriptionPlan,
    UserSubscription,
    Seller,
    ProductCategory,
    Product,
    Campaign,
    Dayparting,
    CampaignPerformanceReport,
    AdGroup,
    Keyword,
    KeywordPerformance,
    KeywordRecommendation,
    BiddingStrategy,
    PerformanceReport,
    CompetitorAd,
)
from .serializers import (
    UserAuthenticationSerializer,
    UserProfileSerializer,
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    SellerSerializer,
    ProductCategorySerializer,
    ProductSerializer,
    CampaignSerializer,
    DaypartingSerializer,
    CampaignPerformanceReportSerializer,
    AdGroupSerializer,
    KeywordSerializer,
    KeywordPerformanceSerializer,
    KeywordRecommendationSerializer,
    BiddingStrategySerializer,
    PerformanceReportSerializer,
    CompetitorAdSerializer,
)


# Seller ViewSet
class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'marketplace']
    ordering_fields = ['created_at', 'name']


# ProductCategory ViewSet
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']


# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['price', 'stock_quantity', 'created_at']


# Campaign ViewSet with a custom action to apply dayparting logic
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['campaign_name', 'seller__name']
    ordering_fields = ['start_date', 'campaign_name']

    @action(detail=True, methods=['post'])
    def apply_dayparting(self, request, pk=None):
        campaign = self.get_object()
        campaign.apply_dayparting()  # Call the business logic method
        return Response({'status': 'Dayparting applied'}, status=status.HTTP_200_OK)


# Dayparting ViewSet
class DaypartingViewSet(viewsets.ModelViewSet):
    queryset = Dayparting.objects.all()
    serializer_class = DaypartingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['campaign__campaign_name']
    ordering_fields = ['time_slot_start', 'time_slot_end']


# CampaignPerformanceReport ViewSet
class CampaignPerformanceReportViewSet(viewsets.ModelViewSet):
    queryset = CampaignPerformanceReport.objects.all()
    serializer_class = CampaignPerformanceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['campaign__campaign_name']
    ordering_fields = ['report_date']


# AdGroup ViewSet
class AdGroupViewSet(viewsets.ModelViewSet):
    queryset = AdGroup.objects.all()
    serializer_class = AdGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ad_group_name', 'campaign__campaign_name']
    ordering_fields = ['created_at', 'bid']


# Keyword ViewSet
class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['keyword', 'ad_group__ad_group_name']
    ordering_fields = ['created_at', 'bid']


# KeywordPerformance ViewSet
class KeywordPerformanceViewSet(viewsets.ModelViewSet):
    queryset = KeywordPerformance.objects.all()
    serializer_class = KeywordPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['keyword__keyword']
    ordering_fields = ['date']


# KeywordRecommendation ViewSet
class KeywordRecommendationViewSet(viewsets.ModelViewSet):
    queryset = KeywordRecommendation.objects.all()
    serializer_class = KeywordRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['keyword__keyword', 'recommendation_text']
    ordering_fields = ['created_at']


# BiddingStrategy ViewSet
class BiddingStrategyViewSet(viewsets.ModelViewSet):
    queryset = BiddingStrategy.objects.all()
    serializer_class = BiddingStrategySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['campaign__campaign_name', 'strategy_type']
    ordering_fields = ['created_at']


# PerformanceReport ViewSet
class PerformanceReportViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReport.objects.all()
    serializer_class = PerformanceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['seller__name', 'report_type']
    ordering_fields = ['generated_at']


# CompetitorAd ViewSet
class CompetitorAdViewSet(viewsets.ModelViewSet):
    queryset = CompetitorAd.objects.all()
    serializer_class = CompetitorAdSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['seller__name', 'competitor_name', 'competitor_product']
    ordering_fields = ['observed_at']


# UserAuthentication ViewSet
class UserAuthenticationViewSet(viewsets.ModelViewSet):
    queryset = UserAuthentication.objects.all()
    serializer_class = UserAuthenticationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'amazon_user_id']
    ordering_fields = ['token_expiration', 'created_at']


# UserProfile ViewSet
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'location']
    ordering_fields = ['birth_date']


# SubscriptionPlan ViewSet
class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'tier']
    ordering_fields = ['price']


# UserSubscription ViewSet with a custom action to renew a subscription
class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user_profile__user__username', 'plan__name']
    ordering_fields = ['start_date', 'end_date']

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        subscription = self.get_object()
        subscription.renew_subscription()
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exchange_auth_code(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "Authorization code is required"}, status=400)
    
    try:
        client = AmazonAdsAPIClient()
        response = client.exchange_auth_code(code)
        
        # Save tokens to database
        from based.models import AmazonAdsToken
        AmazonAdsToken.objects.update_or_create(
            user=request.user,
            defaults={
                'access_token': response['access_token'],
                'refresh_token': response['refresh_token']
            }
        )
        
        return JsonResponse({"success": True, "message": "Authentication successful"})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
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
        # Get the user's refresh token from the database
        from based.models import AmazonAdsToken
        try:
            token_obj = AmazonAdsToken.objects.get(user=request.user)
            # Create client with the refresh token from the database
            client = AmazonAdsAPIClient(refresh_token=token_obj.refresh_token)
            new_access_token = client.refresh_access_token()
            
            # Update the access token in the database
            token_obj.access_token = new_access_token
            token_obj.save(update_fields=['access_token', 'updated_at'])
            
            logger.info(f"Successfully refreshed token for user {request.user.id}")
            return JsonResponse({"success": True, "message": "Token refreshed successfully"})
        except AmazonAdsToken.DoesNotExist:
            logger.error(f"No Amazon Ads tokens found for user {request.user.id}")
            return JsonResponse({"error": "No Amazon Ads tokens found. Please authenticate first."}, status=400)
    except ValueError as e:
        logger.error(f"Token refresh error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
