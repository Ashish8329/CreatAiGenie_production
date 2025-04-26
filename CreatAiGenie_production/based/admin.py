from django.contrib import admin
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
    CampaignData
)

# Seller Admin
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'marketplace', 'created_at')
    list_filter = ('marketplace', 'created_at')
    search_fields = ('name', 'email')

admin.site.register(Seller, SellerAdmin)


# ProductCategory Admin
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(ProductCategory, ProductCategoryAdmin)


# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock_quantity', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'category')
    search_fields = ('name', 'sku', 'description')

admin.site.register(Product, ProductAdmin)


# Campaign Admin
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign_name', 'seller', 'status', 'start_date', 'end_date', 'dayparting_enabled')
    list_filter = ('status', 'dayparting_enabled', 'start_date', 'end_date', 'seller')
    search_fields = ('campaign_name', 'seller__name')

admin.site.register(Campaign, CampaignAdmin)


# Dayparting Admin
class DaypartingAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'time_slot_start', 'time_slot_end', 'day_type', 'part_type')
    list_filter = ('day_type', 'part_type')
    search_fields = ('campaign__campaign_name',)

admin.site.register(Dayparting, DaypartingAdmin)


# CampaignPerformanceReport Admin
class CampaignPerformanceReportAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'report_date', 'impressions', 'clicks', 'sales', 'spend', 'roas', 'acos'
    )
    list_filter = ('report_date', 'campaign')
    search_fields = ('campaign__campaign_name',)

admin.site.register(CampaignPerformanceReport, CampaignPerformanceReportAdmin)


# AdGroup Admin
class AdGroupAdmin(admin.ModelAdmin):
    list_display = ('ad_group_name', 'campaign', 'bid', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'campaign')
    search_fields = ('ad_group_name', 'campaign__campaign_name')

admin.site.register(AdGroup, AdGroupAdmin)


# Keyword Admin
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'ad_group', 'match_type', 'bid', 'status', 'created_at')
    list_filter = ('match_type', 'status', 'created_at', 'ad_group')
    search_fields = ('keyword', 'ad_group__ad_group_name')

admin.site.register(Keyword, KeywordAdmin)


# KeywordPerformance Admin
class KeywordPerformanceAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'date', 'impressions', 'clicks', 'sales', 'spend', 'acos', 'roas')
    list_filter = ('date', 'keyword')
    search_fields = ('keyword__keyword',)

admin.site.register(KeywordPerformance, KeywordPerformanceAdmin)


# KeywordRecommendation Admin
class KeywordRecommendationAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'recommendation_type', 'recommendation_value', 'created_at')
    list_filter = ('recommendation_type', 'created_at')
    search_fields = ('keyword__keyword', 'recommendation_text')

admin.site.register(KeywordRecommendation, KeywordRecommendationAdmin)


# BiddingStrategy Admin
class BiddingStrategyAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'strategy_type', 'bid_amount', 'status', 'created_at')
    list_filter = ('strategy_type', 'status', 'created_at', 'campaign')
    search_fields = ('campaign__campaign_name',)

admin.site.register(BiddingStrategy, BiddingStrategyAdmin)


# PerformanceReport Admin
class PerformanceReportAdmin(admin.ModelAdmin):
    list_display = ('seller', 'report_type', 'generated_at')
    list_filter = ('report_type', 'generated_at', 'seller')
    search_fields = ('seller__name',)

admin.site.register(PerformanceReport, PerformanceReportAdmin)


# CompetitorAd Admin
class CompetitorAdAdmin(admin.ModelAdmin):
    list_display = ('seller', 'competitor_name', 'competitor_product', 'observed_at')
    list_filter = ('observed_at', 'seller', 'competitor_name')
    search_fields = ('seller__name', 'competitor_name', 'competitor_product')

admin.site.register(CompetitorAd, CompetitorAdAdmin)


# UserAuthentication Admin
class UserAuthenticationAdmin(admin.ModelAdmin):
    list_display = ('user', 'amazon_user_id', 'token_expiration')
    list_filter = ('token_expiration',)
    search_fields = ('user__username', 'amazon_user_id')

admin.site.register(UserAuthentication, UserAuthenticationAdmin)


# UserProfile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date')
    list_filter = ('location',)
    search_fields = ('user', 'bio')

admin.site.register(UserProfile, UserProfileAdmin)


# SubscriptionPlan Admin
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'price', 'duration_days')
    list_filter = ('tier',)
    search_fields = ('name',)

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)


# UserSubscription Admin
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'plan', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'plan')
    search_fields = ('user_profile__user__username', 'plan__name')

admin.site.register(UserSubscription, UserSubscriptionAdmin)

class CampaignDataAdmin(admin.ModelAdmin):
    list_display = ('campaign_id', 'product', 'impressions', 'clicks', 'spend', 'orders', 'roas', 'acos')
    search_fields = ('campaign_id', 'product')
    list_filter = ('user',)

admin.site.register(CampaignData, CampaignDataAdmin)