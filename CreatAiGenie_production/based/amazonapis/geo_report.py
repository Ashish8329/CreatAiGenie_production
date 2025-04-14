# reports/geo_report.py

import logging
import json
from .report_base import ReportBase

class GeoReport(ReportBase):
    """
    Geo Report class for generating the Geo report.
    Inherits from ReportBase to share common behavior for report generation.
    """
    
    def __init__(self, api_client, email_service):
        super().__init__(api_client, email_service)
        self.report_type = "geo"
        self.report_data = None
    
    def generate_report(self, start_date, end_date):
        """
        Generate the Geo report from the API.
        
        Args:
            start_date (str): The start date for the report.
            end_date (str): The end date for the report.
        """
        logging.info(f"Generating {self.report_type} report from {start_date} to {end_date}.")

        # Construct API request parameters for the Geo report
        request_params = {
            "name": f"{self.report_type}_report_{start_date}_{end_date}",
            "startDate": start_date,
            "endDate": end_date,
            "configuration": {
                "adProduct": "SPONSORED_PRODUCTS",  # Example: Customize as per your report type
                "columns": ["region", "country", "impressions", "clicks", "cost", "sales", "campaignId"],
                "reportTypeId": "geoReport",  # Adjust based on your report type
                "timeUnit": "SUMMARY",
                "format": "GZIP_JSON"
            }
        }

        # API call to generate the report
        response = self.api_client.create_report(request_params)
        
        if response.status_code == 200:
            self.report_data = response.json()  # Assuming JSON response
            logging.info("Report generated successfully.")
        else:
            logging.error(f"Failed to generate report: {response.status_code} - {response.text}")
            raise Exception(f"API call failed with status {response.status_code}")

    def save_to_db(self):
        """
        Save the generated report data to the database.
        """
        if not self.report_data:
            logging.error("No report data to save. Please generate the report first.")
            return
        
        # Example: Convert report_data into a format suitable for the database
        report_json = json.dumps(self.report_data)
        
        # Save to your database (Example using Django ORM, adjust as needed)
        try:
            # Example: Assuming there's a `Report` model in Django
            from reporting.models import Report
            new_report = Report(
                report_type=self.report_type,
                data=report_json,
                created_at=self.get_timestamp(),
            )
            new_report.save()
            logging.info("Report saved to database.")
        except Exception as e:
            logging.error(f"Error saving report to database: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def send_email(self, recipient_email):
        """
        Send the generated report via email.
        
        Args:
            recipient_email (str): The recipient's email address.
        """
        if not self.report_data:
            logging.error("No report data to send. Please generate the report first.")
            return
        
        # Example: Convert the report data into a CSV or PDF attachment
        report_attachment = self.convert_to_csv(self.report_data)  # Convert data to CSV for email attachment

        # Send the email with the report attached
        subject = f"{self.report_type.capitalize()} Report"
        body = f"Please find attached the {self.report_type} report for the selected period."
        
        try:
            self.email_service.send_email(
                recipient_email,
                subject,
                body,
                attachment=report_attachment
            )
            logging.info(f"Report sent to {recipient_email}.")
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            raise Exception(f"Email sending error: {str(e)}")
    
    def convert_to_csv(self, data):
        """
        Convert report data to CSV format for email attachment.
        
        Args:
            data (dict): The report data.
        
        Returns:
            str: The CSV formatted report data.
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
