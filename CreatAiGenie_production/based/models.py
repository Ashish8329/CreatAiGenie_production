from datetime import timedelta
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# Custom Manager for Seller model
class SellerManager(models.Manager):
    def active(self):
        return self.filter(user__is_active=True)

    def get_active_sellers(self):
        return self.active()


# UserAuthentication model to store Amazon authentication information
class UserAuthentication(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='amazon_auth'
    )
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_expiration = models.DateTimeField()
    amazon_user_id = models.CharField(max_length=255, unique=True)
    client_id = models.CharField(max_length=255)
    redirect_uri = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserAuthentication for {self.user.username}"

    def is_token_expired(self):
        return timezone.now() >= self.token_expiration

    def refresh_access_token(self, new_access_token, new_token_expiration):
        self.access_token = new_access_token
        self.token_expiration = new_token_expiration
        self.save()


# Dynamic upload path function for user profile pictures
def user_profile_pic_path(instance, filename):
    return f"profile_pics/{instance.user.id}/{filename}"


# UserProfile model to store additional information about the user
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='based_profile'
    )
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# SubscriptionPlan model for different subscription options
class SubscriptionPlan(models.Model):
    TIER_CHOICES = [
        ('Stellar', 'Stellar'),
        ('Stellar Plus', 'Stellar Plus'),
        ('Stellar Prime', 'Stellar Prime'),
        ('Stellar Business', 'Stellar Business'),
    ]
    name = models.CharField(max_length=100, unique=True)
    tier = models.CharField(max_length=50, choices=TIER_CHOICES, default='Stellar')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    duration_days = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} - {self.tier}'

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"


# UserSubscription model to manage subscriptions for users
class UserSubscription(models.Model):
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='subscriptions'
    )
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions'
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.plan.name}"
    
    def is_active(self):
        return self.start_date <= timezone.now() <= self.end_date

    def renew_subscription(self):
        self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        self.save()
    
    class Meta:
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"


# Seller model for an Amazon seller's account, linked to the user
class Seller(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    marketplace = models.CharField(max_length=255)  # e.g., Amazon US, Amazon UK
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SellerManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"
        indexes = [
            models.Index(fields=['user', 'marketplace']),
        ]


# Consolidated ProductCategory model (replacing separate Category model)
class ProductCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"


# Product model to represent products in your system
class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        default=0
    )
    ad_asin = models.CharField(max_length=255, unique=True, blank=True, null=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_price_after_discount(self):
        if self.discount:
            return self.price * (1 - self.discount / 100)
        return self.price

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=['name', 'category']),
            models.Index(fields=['sku']),
        ]


# Campaign model to represent individual ad campaigns
class Campaign(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('ended', 'Ended'),
        ('archived', 'Archived'),
    ]
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='campaigns', blank=True)
    campaign_name = models.CharField(max_length=255)
    daily_budget = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True
    )
    current_spend = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active', db_index=True)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dayparting_enabled = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['seller', 'status', 'start_date']),
            models.Index(fields=['end_date']),
        ]
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"

    def __str__(self):
        return f"Campaign: {self.campaign_name} for {self.seller.name}"

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

    def apply_dayparting(self):
        if not self.dayparting_enabled:
            return

        current_time = timezone.now().time()
        for dayparting in self.daypartings.all():
            if dayparting.day_type == 'all' or (
                dayparting.day_type == 'specific' and self._is_today_in_specific_days(dayparting)
            ):
                if dayparting.time_slot_start <= current_time <= dayparting.time_slot_end:
                    if dayparting.part_type == 'bid' and dayparting.bid_adjustment_value:
                        self.adjust_bid(dayparting.bid_adjustment_value)
                    elif dayparting.part_type == 'budget' and dayparting.budget_adjustment_method:
                        self.adjust_budget(dayparting)

    def _is_today_in_specific_days(self, dayparting):
        import datetime
        today = datetime.datetime.today().strftime("%A")  # e.g., 'Monday'
        if isinstance(dayparting.specific_days, list):
            return today in dayparting.specific_days
        return False

    def adjust_bid(self, adjustment_value):
        # Implement bid adjustment logic
        print(f"Adjusting bid by {adjustment_value}")

    def adjust_budget(self, dayparting):
        if dayparting.budget_adjustment_method == 'fixed':
            print(f"Setting fixed budget of {dayparting.budget_adjustment_value}")
        elif dayparting.budget_adjustment_method == 'amount':
            print(f"Adjusting budget by {dayparting.budget_adjustment_value} amount")
        elif dayparting.budget_adjustment_method == 'percentage':
            print(f"Adjusting budget by {dayparting.budget_adjustment_value}%")


# Dayparting model to adjust bids or budgets at specific times
class Dayparting(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="daypartings")
    PART_TYPE_CHOICES = [
        ('bid', 'Bid Dayparting'),
        ('budget', 'Budget Dayparting'),
    ]
    part_type = models.CharField(max_length=10, choices=PART_TYPE_CHOICES, default='bid')
    time_slot_start = models.TimeField()
    time_slot_end = models.TimeField()
    BUDGET_ADJUSTMENT_CHOICES = [
        ('fixed', 'Set Fixed Budget'),
        ('amount', 'Adjust by Amount'),
        ('percentage', 'Adjust by Percentage'),
    ]
    budget_adjustment_method = models.CharField(
        max_length=10, choices=BUDGET_ADJUSTMENT_CHOICES, null=True, blank=True
    )
    budget_adjustment_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bid_adjustment_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    DAY_TYPE_CHOICES = [
        ('all', 'All Days'),
        ('specific', 'Specific Days'),
    ]
    day_type = models.CharField(max_length=10, choices=DAY_TYPE_CHOICES, default='all')
    # Store specific days as a JSON list (e.g., ["Monday", "Tuesday"])
    specific_days = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dayparting"
        verbose_name_plural = "Daypartings"
        unique_together = ('campaign', 'time_slot_start', 'time_slot_end')

    def __str__(self):
        return f"Dayparting for {self.campaign.campaign_name} from {self.time_slot_start} to {self.time_slot_end}"

    def clean(self):
        if self.time_slot_start >= self.time_slot_end:
            raise ValidationError("Start time must be earlier than end time.")
        if self.day_type == 'specific' and not self.specific_days:
            raise ValidationError("Specific days must be provided when day type is 'specific'.")


# CampaignPerformanceReport model with multiple performance metrics
class CampaignPerformanceReport(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    roas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Return on Ad Spend
    acos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Advertising Cost of Sales
    report_date = models.DateField()

    def __str__(self):
        return f"{self.campaign.campaign_name} Performance Report ({self.report_date})"

    class Meta:
        verbose_name = "Campaign Performance Report"
        verbose_name_plural = "Campaign Performance Reports"


# AdGroup model to represent ad groups within each campaign
class AdGroup(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    ad_group_name = models.CharField(max_length=100)
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('paused', 'Paused')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ad_group_name


# Keyword model to store keywords for which bids are placed
class Keyword(models.Model):
    ad_group = models.ForeignKey(AdGroup, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    match_type = models.CharField(
        max_length=50, choices=[('broad', 'Broad'), ('phrase', 'Phrase'), ('exact', 'Exact')]
    )
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('paused', 'Paused')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keyword


# KeywordPerformance model storing core metrics;
# ACOS and ROAS are computed dynamically as properties.
class KeywordPerformance(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField()

    def __str__(self):
        return f"Performance for {self.keyword.keyword} on {self.date}"

    @property
    def acos(self):
        return (self.spend / self.sales * 100) if self.sales else 0

    @property
    def roas(self):
        return (self.sales / self.spend) if self.spend else 0


# KeywordRecommendation model to suggest adjustments or opportunities for keywords
class KeywordRecommendation(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    recommendation_text = models.TextField()
    recommendation_type = models.CharField(
        max_length=100, choices=[
            ('bid_adjustment', 'Bid Adjustment'),
            ('visibility', 'Visibility Opportunity'),
            ('pause', 'Pause Keyword')
        ]
    )
    recommendation_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Keyword Recommendation"
        verbose_name_plural = "Keyword Recommendations"

    def __str__(self):
        return f"Recommendation for Keyword: {self.keyword.keyword}"


# BiddingStrategy model captures the bidding strategy used by campaigns
class BiddingStrategy(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    strategy_type = models.CharField(
        max_length=50, choices=[('manual', 'Manual'), ('enhanced_cpc', 'Enhanced CPC')]
    )
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('paused', 'Paused')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.strategy_type} for {self.campaign}"


# PerformanceReport model for periodic seller reports (weekly, monthly, quarterly)
class PerformanceReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100, choices=REPORT_TYPE_CHOICES)
    report_data = models.JSONField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Performance Report"
        verbose_name_plural = "Performance Reports"

    def __str__(self):
        return f"Performance Report for {self.seller.name} - {self.report_type}"


# CompetitorAd model to track competitor ads in real-time
class CompetitorAd(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    competitor_name = models.CharField(max_length=255)
    competitor_product = models.CharField(max_length=255)
    ad_url = models.URLField()
    competitor_bid = models.DecimalField(max_digits=10, decimal_places=2)
    observed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Competitor Ad"
        verbose_name_plural = "Competitor Ads"

    def __str__(self):
        return f"Competitor Ad for {self.competitor_name}"



# # [2025-03-30]
# # Author: Shivam and Rajesh
# # Description: Adding Models to integrate Amazons api data into our models and store to process then in future
# from django.db import models

# class CampaignData(models.Model):
#     campaign_id = models.CharField(max_length=100)
#     product = models.CharField(max_length=255, null=True, blank=True)
#     bid = models.FloatField(null=True, blank=True)
#     impressions = models.IntegerField(null=True, blank=True)
#     clicks = models.IntegerField(null=True, blank=True)
#     daily_budget = models.FloatField(null=True, blank=True)
#     cpc = models.FloatField(null=True, blank=True)
#     roas = models.FloatField(null=True, blank=True)
#     spend = models.FloatField(null=True, blank=True)
#     orders = models.IntegerField(null=True, blank=True)
#     conversion_rate = models.FloatField(null=True, blank=True)
#     acos = models.FloatField(null=True, blank=True)
#     start_date = models.DateField(null=True, blank=True)
#     end_date = models.DateField(null=True, blank=True)
#     protected = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Campaign {self.campaign_id}"

from django.conf import settings
from django.db import models

class CampaignData(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaign_reports'
    )
    campaign_id = models.CharField(max_length=100)
    product = models.CharField(max_length=255, null=True, blank=True)
    bid = models.FloatField(null=True, blank=True)
    impressions = models.IntegerField(null=True, blank=True)
    clicks = models.IntegerField(null=True, blank=True)
    daily_budget = models.FloatField(null=True, blank=True)
    cpc = models.FloatField(null=True, blank=True)
    roas = models.FloatField(null=True, blank=True)
    spend = models.FloatField(null=True, blank=True)
    orders = models.IntegerField(null=True, blank=True)
    conversion_rate = models.FloatField(null=True, blank=True)
    acos = models.FloatField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    protected = models.BooleanField(default=False)

    def __str__(self):
        return f"Campaign {self.campaign_id} for User {self.user}"

class AmazonAdsToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)