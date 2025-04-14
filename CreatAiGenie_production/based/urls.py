from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SellerViewSet,
    ProductCategoryViewSet,
    ProductViewSet,
    CampaignViewSet,
    DaypartingViewSet,
    CampaignPerformanceReportViewSet,
    AdGroupViewSet,
    KeywordViewSet,
    KeywordPerformanceViewSet,
    KeywordRecommendationViewSet,
    BiddingStrategyViewSet,
    PerformanceReportViewSet,
    CompetitorAdViewSet,
    UserAuthenticationViewSet,
    UserProfileViewSet,
    SubscriptionPlanViewSet,
    UserSubscriptionViewSet,
)
from based.amazonapis import request_report
from based.amazonapis import query_system

router = DefaultRouter()
router.register(r'sellers', SellerViewSet, basename='seller')
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'daypartings', DaypartingViewSet, basename='dayparting')
router.register(r'campaign-reports', CampaignPerformanceReportViewSet, basename='campaignreport')
router.register(r'adgroups', AdGroupViewSet, basename='adgroup')
router.register(r'keywords', KeywordViewSet, basename='keyword')
router.register(r'keyword-performance', KeywordPerformanceViewSet, basename='keywordperformance')
router.register(r'keyword-recommendations', KeywordRecommendationViewSet, basename='keywordrecommendation')
router.register(r'bidding-strategies', BiddingStrategyViewSet, basename='biddingstrategy')
router.register(r'performance-reports', PerformanceReportViewSet, basename='performancereport')
router.register(r'competitor-ads', CompetitorAdViewSet, basename='competitorad')
router.register(r'user-authentications', UserAuthenticationViewSet, basename='userauthentication')
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscriptionplan')
router.register(r'user-subscriptions', UserSubscriptionViewSet, basename='usersubscription')

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from based.views import (
    refresh_access_token,
    exchange_auth_code,
)

urlpatterns = [
    path('api/', include(router.urls)),
    # Djoser endpoints for authentication
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),  # if you're using JWT tokens

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Authentication endpoints
    path('amazon/auth/url/', request_report.get_auth_url, name='amazon_auth_url'),
    path('amazon/auth/exchange/', exchange_auth_code, name='amazon_auth_exchange'),
    path('amazon/auth/refresh/', refresh_access_token, name='amazon_auth_refresh'),
    
    # Profile endpoints
    path('amazon/profiles/', request_report.get_profiles, name='amazon_profiles'),
    
    # Report endpoints
    path('amazon/reports/request/', request_report.request_report, name='amazon_report_request'),
    path('amazon/reports/request/keywords/', request_report.request_keyword_report, name='amazon_report_request_keywords'),
    path('amazon/reports/status/<str:report_id>/', request_report.check_report_status, name='amazon_report_status'),

    #Filter endpoints
    path('api/filter-campaigns/', query_system.filter_campaigns, name='filter-campaigns'),
]






# # [2025-03-30]
# # Author: Shivam and Rajesh
# # Description: Adding urls to integrate Amazons api authentication and fetching profiles and reports from Amazon api

# from django.urls import path
# from based.amazonapis.request_report import (
#     get_auth_url,
#     exchange_auth_code,
#     refresh_access_token,
#     request_report,
#     check_report_status,
#     download_report,
#     get_profiles,
# )
# from based.amazonapis.query_system import filter_campaigns

# urlpatterns = [
#     path('auth/url/', get_auth_url, name='get_auth_url'),
#     path('auth/token/', exchange_auth_code, name='exchange_auth_code'),
#     path('auth/refresh/', refresh_access_token, name='refresh_access_token'),
#     path('report/request/', request_report, name='request_report'),
#     path('report/status/<str:report_id>/', check_report_status, name='check_report_status'),
#     path('report/download/<str:report_id>/', download_report, name='download_report'),
#     path('profiles/', get_profiles, name='get_profiles'),
# # [2025-04-01]
# # Author: Shivam and Rajesh
# # Description: Adding urls to to filter campaings based on Conditions in terminal
#     path('filter_campaigns/', filter_campaigns, name='filter_campaigns'),

# ]

