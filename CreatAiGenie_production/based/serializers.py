from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)
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

# Custom Djoser-based user serializers
class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ('id', 'username', 'email', 'password')


class CustomUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


# Alias the custom serializers to the names Djoser expects
UserCreateSerializer = CustomUserCreateSerializer
UserSerializer = CustomUserSerializer


# UserAuthentication serializer
class UserAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuthentication
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')


# UserProfile serializer
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user',)


# SubscriptionPlan serializer
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


# UserSubscription serializer
class UserSubscriptionSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(read_only=True)
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = '__all__'
        read_only_fields = ('start_date',)


# Seller serializer
class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Seller
        fields = '__all__'
        read_only_fields = ('created_at',)


# ProductCategory serializer
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


# Product serializer
class ProductSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    category = ProductCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Campaign serializer
class CampaignSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ('created_at',)


# Dayparting serializer
class DaypartingSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)

    class Meta:
        model = Dayparting
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# CampaignPerformanceReport serializer
class CampaignPerformanceReportSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)

    class Meta:
        model = CampaignPerformanceReport
        fields = '__all__'


# AdGroup serializer
class AdGroupSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)

    class Meta:
        model = AdGroup
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Keyword serializer
class KeywordSerializer(serializers.ModelSerializer):
    ad_group = AdGroupSerializer(read_only=True)

    class Meta:
        model = Keyword
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# KeywordPerformance serializer
class KeywordPerformanceSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(read_only=True)

    class Meta:
        model = KeywordPerformance
        fields = '__all__'


# KeywordRecommendation serializer
class KeywordRecommendationSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(read_only=True)

    class Meta:
        model = KeywordRecommendation
        fields = '__all__'


# BiddingStrategy serializer
class BiddingStrategySerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)

    class Meta:
        model = BiddingStrategy
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# PerformanceReport serializer
class PerformanceReportSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = PerformanceReport
        fields = '__all__'


# CompetitorAd serializer
class CompetitorAdSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = CompetitorAd
        fields = '__all__'
        read_only_fields = ('observed_at',)




# [2025-03-30]
# Author: Shivam and Rajesh
# Description: Adding Serializers to our models in order to convert models into API to communicate with frontend
# Added only for Campaign data

from rest_framework import serializers
from .models import CampaignData

class CampaignDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignData
        fields = '_all_'
