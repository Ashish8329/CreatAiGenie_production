# reports/report_factory.py

from .overview_report import OverviewReport
from .campaign_report import CampaignReport
from .ad_group_report import AdGroupReport
from .audience_report import AudienceReport
from .geo_report import GeoReport
from .inventory_report import InventoryReport
from .product_report import ProductReport
from .audio_video_report import AudioVideoReport
from .tech_report import TechReport
from .placement_report import PlacementReport
from .targeting_report import TargetingReport
from .search_term_report import SearchTermReport
from .advertised_product_report import AdvertisedProductReport
from .purchased_product_report import PurchasedProductReport
from .gross_invalid_traffic_report import GrossInvalidTrafficReport
from .reach_frequency_report import ReachFrequencyReport

class ReportFactory:
    """
    Factory class for creating report instances based on the requested report type.
    """
    def __init__(self, api_client, email_service):
        self.api_client = api_client
        self.email_service = email_service

    def create_report(self, report_type):
        """
        Create and return the corresponding report object based on the provided report type.
        
        Args:
            report_type (str): The type of report to generate.
            
        Returns:
            A report object (e.g., OverviewReport, CampaignReport, etc.)
        """
        if report_type == "overview":
            return OverviewReport(self.api_client, self.email_service)
        elif report_type == "campaign":
            return CampaignReport(self.api_client, self.email_service)
        elif report_type == "ad_group":
            return AdGroupReport(self.api_client, self.email_service)
        elif report_type == "audience":
            return AudienceReport(self.api_client, self.email_service)
        elif report_type == "geo":
            return GeoReport(self.api_client, self.email_service)
        elif report_type == "inventory":
            return InventoryReport(self.api_client, self.email_service)
        elif report_type == "product":
            return ProductReport(self.api_client, self.email_service)
        elif report_type == "audio_video":
            return AudioVideoReport(self.api_client, self.email_service)
        elif report_type == "tech":
            return TechReport(self.api_client, self.email_service)
        elif report_type == "placement":
            return PlacementReport(self.api_client, self.email_service)
        elif report_type == "targeting":
            return TargetingReport(self.api_client, self.email_service)
        elif report_type == "search_term":
            return SearchTermReport(self.api_client, self.email_service)
        elif report_type == "advertised_product":
            return AdvertisedProductReport(self.api_client, self.email_service)
        elif report_type == "purchased_product":
            return PurchasedProductReport(self.api_client, self.email_service)
        elif report_type == "gross_invalid_traffic":
            return GrossInvalidTrafficReport(self.api_client, self.email_service)
        elif report_type == "reach_frequency":
            return ReachFrequencyReport(self.api_client, self.email_service)
        else:
            raise ValueError(f"Report type '{report_type}' is not supported.")
