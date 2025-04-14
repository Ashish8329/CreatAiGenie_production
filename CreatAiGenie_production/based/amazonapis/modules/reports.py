import logging
import json
import requests
import pandas as pd
import io
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .client import AmazonAdsAPIClient
from based.models import CampaignData

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_report(request):
    """
    Request an Amazon Ads Report.
    
    Headers:
        Amazon-Advertising-API-Scope: Profile ID (required)
        Content-Type: application/json
    
    Body:
        JSON payload with report configuration
    
    Returns:
        JsonResponse: Report request details or error
    """
    # Check for required profile ID header
    profile_id = request.headers.get("Amazon-Advertising-API-Scope")
    if not profile_id:
        return JsonResponse({"error": "Missing Amazon-Advertising-API-Scope header (profileId)"}, status=400)
    
    try:
        # Parse request body
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        # Get the user's tokens from the database
        from based.models import AmazonAdsToken
        try:
            token_obj = AmazonAdsToken.objects.get(user=request.user)
            
            # Create client with the tokens from the database
            client = AmazonAdsAPIClient(
                access_token=token_obj.access_token,
                refresh_token=token_obj.refresh_token
            )
            
            # Get the base URL from the client
            api_base_url = client.API_BASE_URL
            
        except AmazonAdsToken.DoesNotExist:
            logger.error(f"No Amazon Ads tokens found for user {request.user.id}")
            return JsonResponse({"error": "No Amazon Ads tokens found. Please authenticate first."}, status=400)
        
        # Fix the payload based on the error message
        from datetime import datetime, timedelta
        
        # 1. Set startDate to the retention start date (2025-01-06) or later
        retention_start_date = "2025-01-06"
        
        # 2. Ensure endDate is no more than 31 days after startDate
        if "startDate" in payload:
            start_date = payload["startDate"]
            # Convert from YYYYMMDD to YYYY-MM-DD if needed
            if len(start_date) == 8 and "-" not in start_date:
                start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            
            # Ensure startDate is not before retention start date
            if start_date < retention_start_date:
                start_date = retention_start_date
        else:
            # Default to retention start date
            start_date = retention_start_date
        
        # Set the corrected startDate
        payload["startDate"] = start_date
        
        # Parse the start date for date calculations
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Calculate endDate (maximum 31 days from startDate)
        max_end_date = start_date_obj + timedelta(days=30)  # 31 days total (inclusive)
        max_end_date_str = max_end_date.strftime("%Y-%m-%d")
        
        if "endDate" in payload:
            end_date = payload["endDate"]
            # Convert from YYYYMMDD to YYYY-MM-DD if needed
            if len(end_date) == 8 and "-" not in end_date:
                end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
            
            # Ensure endDate is not more than 31 days after startDate
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            if (end_date_obj - start_date_obj).days > 30:
                end_date = max_end_date_str
        else:
            # Default to 30 days after startDate
            end_date = max_end_date_str
        
        # Set the corrected endDate
        payload["endDate"] = end_date
        
        # 3. Fix invalid columns
        valid_columns = [
            "impressions", "clicks", "cost", "purchases1d", "purchases7d", "purchases14d", "purchases30d",
            "purchasesSameSku1d", "purchasesSameSku7d", "purchasesSameSku14d", "purchasesSameSku30d",
            "unitsSoldClicks1d", "unitsSoldClicks7d", "unitsSoldClicks14d", "unitsSoldClicks30d",
            "sales1d", "sales7d", "sales14d", "sales30d", "attributedSalesSameSku1d", "attributedSalesSameSku7d",
            "attributedSalesSameSku14d", "attributedSalesSameSku30d", "unitsSoldSameSku1d", "unitsSoldSameSku7d",
            "unitsSoldSameSku14d", "unitsSoldSameSku30d", "kindleEditionNormalizedPagesRead14d",
            "kindleEditionNormalizedPagesRoyalties14d", "qualifiedBorrows", "royaltyQualifiedBorrows",
            "addToList", "date", "startDate", "endDate", "campaignBiddingStrategy", "costPerClick",
            "clickThroughRate", "spend", "acosClicks14d", "roasClicks14d", "retailer", "campaignName",
            "campaignId", "campaignStatus", "campaignBudgetAmount", "campaignBudgetType",
            "campaignRuleBasedBudgetAmount", "campaignApplicableBudgetRuleId", "campaignApplicableBudgetRuleName",
            "campaignBudgetCurrencyCode", "topOfSearchImpressionShare"
        ]
        
        # Replace invalid columns with valid alternatives
        column_mapping = {
            "attributedSales14d": "sales14d",
            "attributedConversions14d": "purchases14d"
        }
        
        if "configuration" in payload and "columns" in payload["configuration"]:
            corrected_columns = []
            for col in payload["configuration"]["columns"]:
                if col in valid_columns:
                    corrected_columns.append(col)
                elif col in column_mapping:
                    corrected_columns.append(column_mapping[col])
            
            # Ensure we have at least some valid columns
            if not corrected_columns:
                corrected_columns = ["campaignName", "campaignId", "impressions", "clicks", "cost", "sales14d", "purchases14d"]
            
            payload["configuration"]["columns"] = corrected_columns
        
        # 4. Ensure configuration has groupBy field
        if "configuration" in payload:
            if "groupBy" not in payload["configuration"]:
                payload["configuration"]["groupBy"] = ["campaign"]
        else:
            # If configuration is missing, create it with all required fields
            payload["configuration"] = {
                "adProduct": "SPONSORED_PRODUCTS",
                "groupBy": ["campaign"],
                "columns": ["campaignName", "campaignId", "impressions", "clicks", "cost", "sales14d", "purchases14d"],
                "reportTypeId": "spCampaigns",
                "timeUnit": "DAILY",
                "format": "CSV"
            }
        
        # 5. Ensure the payload has a name
        if "name" not in payload:
            payload["name"] = f"Campaign Report {payload['startDate']} to {payload['endDate']}"
        
        # Construct headers directly like in the working code
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Amazon-Advertising-API-ClientId": client.client_id,
            "Amazon-Advertising-API-Scope": profile_id,
            "Content-Type": "application/json"
        }
        
        # Use the reporting endpoint
        api_endpoint = f"{api_base_url}/reporting/reports"
        
        logger.info(f"Making request to: {api_endpoint}")
        logger.info(f"With headers: {headers}")
        logger.info(f"With payload: {json.dumps(payload)}")
        
        # Make the API request directly using requests like in the working code
        response = requests.post(api_endpoint, headers=headers, json=payload)
        
        logger.info(f"Report request response: {response.status_code} {response.text[:200]}")
        
        # Handle the response
        if response.status_code in [200, 202]:
            logger.info(f"Successfully requested report for profile {profile_id}")
            return JsonResponse(response.json())
        else:
            logger.error(f"Failed to request report: {response.status_code} {response.text}")
            try:
                error_details = response.json()
                return JsonResponse({"error": "Failed to request report", "details": error_details}, status=response.status_code)
            except:
                return JsonResponse({"error": "Failed to request report", "details": response.text}, status=response.status_code)
            
    except ValueError as e:
        logger.error(f"Error requesting report: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error requesting report: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_keyword_report(request):
    """
    Request an Amazon Ads Keyword Performance Report.
    
    Headers:
        Amazon-Advertising-API-Scope: Profile ID (required)
        Content-Type: application/json
    
    Body:
        JSON payload with report configuration (optional)
    
    Returns:
        JsonResponse: Report request details or error
    """
    # Check for required profile ID header
    profile_id = request.headers.get("Amazon-Advertising-API-Scope")
    if not profile_id:
        return JsonResponse({"error": "Missing Amazon-Advertising-API-Scope header (profileId)"}, status=400)
    
    try:
        # Parse request body if provided
        try:
            if request.body:
                payload = json.loads(request.body)
            else:
                # Use default payload
                payload = {}
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        # Get the user's tokens from the database
        from based.models import AmazonAdsToken
        try:
            token_obj = AmazonAdsToken.objects.get(user=request.user)
            
            # Create client with the tokens from the database
            client = AmazonAdsAPIClient(
                access_token=token_obj.access_token,
                refresh_token=token_obj.refresh_token
            )
            
            # Get the base URL from the client
            api_base_url = client.API_BASE_URL
            
        except AmazonAdsToken.DoesNotExist:
            logger.error(f"No Amazon Ads tokens found for user {request.user.id}")
            return JsonResponse({"error": "No Amazon Ads tokens found. Please authenticate first."}, status=400)
        
        # Create a properly formatted payload for keyword reports
        from datetime import datetime, timedelta
        
        # Set dates
        retention_start_date = "2025-01-06"  # Use the retention start date from previous error
        start_date = payload.get("startDate", retention_start_date)
        
        # Convert from YYYYMMDD to YYYY-MM-DD if needed
        if len(start_date) == 8 and "-" not in start_date:
            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        
        # Ensure startDate is not before retention start date
        if start_date < retention_start_date:
            start_date = retention_start_date
        
        # Parse the start date for date calculations
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Calculate endDate (maximum 31 days from startDate)
        max_end_date = start_date_obj + timedelta(days=30)  # 31 days total (inclusive)
        max_end_date_str = max_end_date.strftime("%Y-%m-%d")
        
        end_date = payload.get("endDate", max_end_date_str)
        
        # Convert from YYYYMMDD to YYYY-MM-DD if needed
        if len(end_date) == 8 and "-" not in end_date:
            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        
        # Ensure endDate is not more than 31 days after startDate
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        if (end_date_obj - start_date_obj).days > 30:
            end_date = max_end_date_str
        
        # Create the correct keyword report payload based on the error message
        formatted_payload = {
            "name": payload.get("name", "Keywords Performance Report"),
            "startDate": start_date,
            "endDate": end_date,
            "configuration": {
                "adProduct": "SPONSORED_PRODUCTS",
                "groupBy": ["adGroup"],  # Required for keyword reports
                "columns": [
                    "keywordId", 
                    "keywordText", 
                    "matchType", 
                    "impressions", 
                    "clicks", 
                    "cost", 
                    "attributedSales14d", 
                    "attributedConversions14d"
                ],
                "reportTypeId": "spKeywords",
                "timeUnit": "SUMMARY",
                "format": "GZIP_JSON"  # Using GZIP_JSON as it's more likely to be supported
            }
        }
        
        # Construct headers directly
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Amazon-Advertising-API-ClientId": client.client_id,
            "Amazon-Advertising-API-Scope": profile_id,
            "Content-Type": "application/json"
        }
        
        # Use the reporting endpoint
        api_endpoint = f"{api_base_url}/reporting/reports"
        
        logger.info(f"Making keyword report request to: {api_endpoint}")
        logger.info(f"With payload: {json.dumps(formatted_payload)}")
        
        # Make the API request directly using requests
        response = requests.post(api_endpoint, headers=headers, json=formatted_payload)
        
        logger.info(f"Keyword report request response: {response.status_code} {response.text[:200]}")
        
        # Handle the response
        if response.status_code in [200, 202]:
            logger.info(f"Successfully requested keyword report for profile {profile_id}")
            return JsonResponse(response.json())
        else:
            logger.error(f"Failed to request keyword report: {response.status_code} {response.text}")
            try:
                error_details = response.json()
                return JsonResponse({"error": "Failed to request keyword report", "details": error_details}, status=response.status_code)
            except:
                return JsonResponse({"error": "Failed to request keyword report", "details": response.text}, status=response.status_code)
            
    except ValueError as e:
        logger.error(f"Error requesting keyword report: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error requesting keyword report: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_report_status(request, report_id):
    """
    Check Report Status from Amazon Ads API and automatically download and save if ready.
    
    Path Parameters:
        report_id (str): ID of the report to check
    
    Headers:
        Amazon-Advertising-API-Scope: Profile ID (required)
    
    Query Parameters:
        save_to_db (bool): Whether to save the report to database if ready (default: true)
        user_id (int): User ID to associate with the campaign data (optional, defaults to current user)
    
    Returns:
        JsonResponse: Report status details or error
    """
    profile_id = request.headers.get("Amazon-Advertising-API-Scope")
    if not profile_id:
        return JsonResponse({"error": "Missing Amazon-Advertising-API-Scope header (profileId)"}, status=400)
    
    # Check if we should save the report when ready (default to true)
    save_to_db = request.GET.get("save_to_db", "true").lower() == "true"
    
    # Default to current user if user_id not provided
    user_id = request.GET.get("user_id", str(request.user.id))
    
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
            
            # Get the base URL from the client
            api_base_url = client.API_BASE_URL
            
        except AmazonAdsToken.DoesNotExist:
            logger.error(f"No Amazon Ads tokens found for user {request.user.id}")
            return JsonResponse({"error": "No Amazon Ads tokens found. Please authenticate first."}, status=400)
        
        # Construct headers directly like in the working code
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Amazon-Advertising-API-ClientId": client.client_id,
            "Amazon-Advertising-API-Scope": profile_id,
            "Content-Type": "application/json"
        }
        
        # Use the reporting endpoint to check status
        api_endpoint = f"{api_base_url}/reporting/reports/{report_id}"
        
        logger.info(f"Checking report status at: {api_endpoint}")
        
        # Make the API request directly using requests
        response = requests.get(api_endpoint, headers=headers)
        
        logger.info(f"Report status response: {response.status_code} {response.text[:200]}")
        
        # Handle the response
        if response.status_code == 200:
            report_data = response.json()
            logger.info(f"Successfully checked report status for report {report_id}")
            
            # If report is completed and we want to save it
            if save_to_db and report_data.get("status") == "COMPLETED":
                logger.info(f"Report {report_id} is complete. Downloading and saving to database...")
                download_result = download_and_save_report(report_id, headers, profile_id, user_id, client)
                report_data["database_save"] = download_result
            elif report_data.get("status") == "COMPLETED":
                logger.info(f"Report {report_id} is complete but save_to_db is false. Skipping download.")
                report_data["database_save"] = {"success": False, "message": "save_to_db parameter is false"}
            else:
                logger.info(f"Report {report_id} status: {report_data.get('status')}. Not ready for download.")
            
            return JsonResponse(report_data)
        else:
            logger.error(f"Failed to check report status: {response.status_code} {response.text}")
            try:
                error_details = response.json()
                return JsonResponse({"error": "Failed to check report status", "details": error_details}, status=response.status_code)
            except:
                return JsonResponse({"error": "Failed to check report status", "details": response.text}, status=response.status_code)
            
    except ValueError as e:
        logger.error(f"Error checking report status: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error checking report status: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)



def download_and_save_report(report_id, headers, profile_id, user_id, client):
    """
    Download a completed report and save it to the database
    
    Args:
        report_id (str): The Amazon report ID
        headers (dict): Headers for the API request
        profile_id (str): The Amazon profile ID
        user_id (int): The user ID to associate with the campaign data
        client (AmazonAdsAPIClient): The API client instance
        
    Returns:
        dict: Result of the download and save operation
    """
    try:
        # Get the report status to get the download URL
        api_endpoint = f"{client.API_BASE_URL}/reporting/reports/{report_id}"
        
        logger.info(f"Getting report details from: {api_endpoint}")
        
        # Use requests directly for consistency
        status_response = requests.get(api_endpoint, headers=headers)
        
        if status_response.status_code != 200:
            logger.error(f"Failed to get report details: {status_response.status_code} {status_response.text}")
            return {
                "success": False,
                "error": f"Failed to get report details: {status_response.status_code}",
                "details": status_response.text[:200]
            }
        
        status_data = status_response.json()
        
        # Check if report is ready and has a download URL
        if status_data.get("status") == "COMPLETED" and "url" in status_data:
            # Download the report
            download_url = status_data["url"]
            logger.info(f"Downloading report from: {download_url}")
            
            # For pre-signed URLs from S3, don't send authorization headers
            # as they conflict with the URL's own authentication
            report_response = requests.get(download_url)
            
            if report_response.status_code != 200:
                logger.error(f"Failed to download report: {report_response.status_code} {report_response.text[:200]}")
                return {
                    "success": False,
                    "error": f"Failed to download report: {report_response.status_code}",
                    "details": report_response.text[:200]
                }
            
            # Parse the report data (handling different formats)
            try:
                content_type = report_response.headers.get('Content-Type', '')
                logger.info(f"Report content type: {content_type}")
                
                # Handle binary/octet-stream (common for S3 CSV files)
                if 'binary/octet-stream' in content_type or 'application/octet-stream' in content_type:
                    # Check content to determine if it's CSV
                    content_sample = report_response.text[:100]
                    if '"' in content_sample and ',' in content_sample:
                        logger.info("Detected CSV format from binary content")
                        import pandas as pd
                        import io
                        df = pd.read_csv(io.StringIO(report_response.text))
                        report_data = df.to_dict(orient='records')
                    else:
                        # Try CSV anyway as a fallback
                        try:
                            import pandas as pd
                            import io
                            df = pd.read_csv(io.StringIO(report_response.text))
                            report_data = df.to_dict(orient='records')
                        except Exception as e:
                            logger.error(f"Failed to parse binary content as CSV: {str(e)}")
                            return {
                                "success": False,
                                "error": f"Failed to parse binary content: {str(e)}",
                                "content_sample": report_response.text[:200]
                            }
                
                # Handle standard content types
                elif 'application/json' in content_type:
                    # JSON format
                    report_data = report_response.json()
                elif 'text/csv' in content_type or download_url.endswith('.csv'):
                    # CSV format
                    import pandas as pd
                    import io
                    df = pd.read_csv(io.StringIO(report_response.text))
                    report_data = df.to_dict(orient='records')
                elif 'application/gzip' in content_type or download_url.endswith('.gz'):
                    # GZIP format (compressed JSON or CSV)
                    import gzip
                    import io
                    
                    # Decompress the gzip content
                    decompressed_content = gzip.decompress(report_response.content)
                    
                    # Try to parse as JSON first
                    try:
                        report_data = json.loads(decompressed_content)
                    except json.JSONDecodeError:
                        # If not JSON, try CSV
                        try:
                            df = pd.read_csv(io.BytesIO(decompressed_content))
                            report_data = df.to_dict(orient='records')
                        except Exception as csv_e:
                            logger.error(f"Failed to parse decompressed content as CSV: {str(csv_e)}")
                            return {
                                "success": False,
                                "error": f"Failed to parse report data: {str(csv_e)}",
                                "content_sample": decompressed_content[:200].decode('utf-8', errors='ignore')
                            }
                else:
                    # Unknown content type - try to detect format from content
                    logger.warning(f"Unknown content type: {content_type}, attempting to detect format")
                    
                    # Try CSV first since that's what we're seeing in the error
                    try:
                        import pandas as pd
                        import io
                        df = pd.read_csv(io.StringIO(report_response.text))
                        report_data = df.to_dict(orient='records')
                        logger.info("Successfully parsed as CSV")
                    except Exception as csv_e:
                        # If CSV fails, try JSON
                        try:
                            report_data = json.loads(report_response.text)
                            logger.info("Successfully parsed as JSON")
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse report with unknown content type: {content_type}")
                            return {
                                "success": False,
                                "error": f"Unsupported content type: {content_type}",
                                "content_sample": report_response.text[:200]
                            }
                
                # Save to database
                save_result = save_report_to_database(report_data, profile_id, user_id)
                
                return {
                    "success": True,
                    "database_save": save_result
                }
                
            except Exception as e:
                logger.error(f"Failed to process report data: {str(e)}")
                return {
                    "success": False,
                    "error": f"Failed to process report data: {str(e)}",
                    "raw_data": report_response.text[:200]
                }
        else:
            return {
                "success": False,
                "message": "Report not ready yet or missing download URL",
                "status": status_data.get("status", "UNKNOWN"),
                "has_url": "url" in status_data
            }
            
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return {
            "success": False,
            "error": f"Error downloading report: {str(e)}"
        }


def save_report_to_database(report_data, profile_id, user_id):
    """
    Save the fetched campaign report data to the database using the CampaignData model
    
    Args:
        report_data (list): The report data returned from Amazon API
        profile_id (str): The Amazon profile ID associated with the report
        user_id (int): The user ID to associate with the campaign data
        
    Returns:
        dict: Result of the database save operation
    """
    User = get_user_model()
    
    try:
        # Get the user
        user = User.objects.get(id=user_id)
        
        # Track stats for reporting
        campaigns_created = 0
        campaigns_updated = 0
        errors = []
        
        # Process each row in the report
        for row in report_data:
            try:
                # Extract campaign data from the report row
                # Handle different field names based on the API version
                campaign_id = row.get('campaignId')
                
                if not campaign_id:
                    errors.append(f"Missing campaign ID in row: {row}")
                    continue
                
                # Map the field names from the API to our database fields
                field_mapping = {
                    # Standard fields
                    'campaignName': 'product',
                    'impressions': 'impressions',
                    'clicks': 'clicks',
                    'cost': 'spend',
                    'spend': 'spend',
                    
                    # Metrics with different names in different API versions
                    'sales14d': 'spend',
                    'purchases14d': 'orders',
                    'attributedSales14d': 'spend',
                    'attributedConversions14d': 'orders',
                    
                    # Additional fields
                    'costPerClick': 'cpc',
                    'roasClicks14d': 'roas',
                    'acosClicks14d': 'acos',
                    'clickThroughRate': 'conversion_rate',
                    'campaignBudgetAmount': 'daily_budget'
                }
                
                # Create a data dictionary for the campaign
                campaign_data = {
                    'campaign_id': campaign_id,
                    'product': '',
                    'bid': 0.0,
                    'impressions': 0,
                    'clicks': 0,
                    'daily_budget': 0.0,
                    'cpc': 0.0,
                    'roas': 0.0,
                    'spend': 0.0,
                    'orders': 0,
                    'conversion_rate': 0.0,
                    'acos': 0.0,
                    'start_date': None,
                    'end_date': None,
                }
                
                # Fill in the data from the report row
                for api_field, db_field in field_mapping.items():
                    if api_field in row and row[api_field] is not None:
                        # Convert to appropriate type
                        if db_field in ['impressions', 'clicks', 'orders']:
                            campaign_data[db_field] = int(float(row[api_field]))
                        elif db_field in ['bid', 'daily_budget', 'cpc', 'roas', 'spend', 'conversion_rate', 'acos']:
                            campaign_data[db_field] = float(row[api_field])
                        else:
                            campaign_data[db_field] = row[api_field]
                
                # Handle date fields
                if 'startDate' in row:
                    campaign_data['start_date'] = row['startDate']
                if 'endDate' in row:
                    campaign_data['end_date'] = row['endDate']
                if 'date' in row:
                    # If there's a single date field, use it for both start and end
                    campaign_data['start_date'] = row['date']
                    campaign_data['end_date'] = row['date']
                
                # Try to find existing campaign or create new one
                campaign, created = CampaignData.objects.update_or_create(
                    user=user,
                    campaign_id=campaign_id,
                    defaults=campaign_data
                )
                
                if created:
                    campaigns_created += 1
                else:
                    campaigns_updated += 1
                    
            except Exception as e:
                errors.append(f"Error processing campaign {row.get('campaignId', 'unknown')}: {str(e)}")
                logger.error(f"Error processing campaign {row.get('campaignId', 'unknown')}: {str(e)}")
        
        logger.info(f"Report processed: {campaigns_created} campaigns created, {campaigns_updated} campaigns updated")
        return {
            "success": True,
            "campaigns_created": campaigns_created,
            "campaigns_updated": campaigns_updated,
            "errors": errors,
            "message": f"Report processed: {campaigns_created} campaigns created, {campaigns_updated} campaigns updated"
        }
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {
            "success": False,
            "error": f"User with ID {user_id} not found",
            "message": "Failed to save report to database - user not found"
        }
    except Exception as e:
        logger.error(f"Failed to save report to database: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save report to database"
        }
