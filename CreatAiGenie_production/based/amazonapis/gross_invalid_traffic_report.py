import logging
from datetime import datetime
from report_base import ReportBase
from utils.api_client import ApiClient
from utils.email_service import EmailService
from utils.database import Database

class GrossInvalidTrafficReport(ReportBase):
    def __init__(self, start_date, end_date, client_id, api_key):
        super().__init__(start_date, end_date)
        self.client_id = client_id
        self.api_key = api_key
        self.api_client = ApiClient(client_id, api_key)
        self.database = Database()
        self.email_service = EmailService()

    def fetch_report_data(self):
        """
        Fetches the gross and invalid traffic report data from the API.
        """
        logging.info("Fetching Gross and Invalid Traffic Report data from the API.")
        
        # Assuming the report data is retrieved from an API call.
        # Replace with the actual API call logic.
        endpoint = f"/gross-invalid-traffic-report?start_date={self.start_date}&end_date={self.end_date}"
        response = self.api_client.make_get_request(endpoint)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Successfully fetched {len(data)} records from the Gross and Invalid Traffic Report API.")
            return data
        else:
            logging.error(f"Failed to fetch data. API responded with status code {response.status_code}")
            return None

    def save_report_to_db(self, report_data):
        """
        Saves the fetched gross and invalid traffic report data to the database.
        """
        logging.info("Saving Gross and Invalid Traffic Report data to the database.")
        if report_data:
            self.database.save('gross_invalid_traffic_reports', report_data)
            logging.info("Gross and Invalid Traffic Report data saved successfully.")
        else:
            logging.error("No data to save to the database.")

    def send_report_via_email(self, report_data, recipient_email):
        """
        Sends the fetched gross and invalid traffic report data via email.
        """
        logging.info("Sending Gross and Invalid Traffic Report via email.")
        
        # Assuming the report is being sent as a CSV file, replace with your actual report format logic.
        email_subject = f"Gross and Invalid Traffic Report: {self.start_date} to {self.end_date}"
        email_body = f"Please find the Gross and Invalid Traffic Report attached for the period {self.start_date} to {self.end_date}."
        
        # Assuming the data is converted into CSV format before sending
        report_file = self.convert_data_to_csv(report_data)
        
        # Send the email
        self.email_service.send_email(recipient_email, email_subject, email_body, attachments=[report_file])
        logging.info(f"Gross and Invalid Traffic Report successfully sent to {recipient_email}.")

    def convert_data_to_csv(self, report_data):
        """
        Converts report data to CSV format.
        """
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report_data[0].keys())
        
        writer.writeheader()
        writer.writerows(report_data)
        
        # Move the cursor to the beginning of the file
        output.seek(0)
        return output.getvalue()

    def generate_report(self, recipient_email):
        """
        Main method to generate the gross and invalid traffic report.
        It fetches data, saves it to the database, and sends it via email.
        """
        report_data = self.fetch_report_data()
        self.save_report_to_db(report_data)
        self.send_report_via_email(report_data, recipient_email)
        logging.info("Gross and Invalid Traffic Report generation complete.")
