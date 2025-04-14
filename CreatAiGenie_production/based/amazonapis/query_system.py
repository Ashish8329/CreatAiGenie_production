import pandas as pd
import logging
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from based.models import CampaignData

# Set up logger
logger = logging.getLogger(__name__)

def get_campaign_data(user_id=None):
    """
    Load and preprocess the dataset from the CampaignData model.
    
    Args:
        user_id (int, optional): Filter data for a specific user. Defaults to None.
        
    Returns:
        DataFrame or None: Pandas DataFrame with campaign data or None if no data found
    """
    try:
        # Get records from the CampaignData table
        if user_id:
            logger.debug(f"Fetching campaign data for user_id: {user_id}")
            queryset = CampaignData.objects.filter(user_id=user_id)
        else:
            logger.debug("Fetching all campaign data")
            queryset = CampaignData.objects.all()
        
        # Convert queryset to pandas DataFrame for consistent filtering
        df = pd.DataFrame.from_records(queryset.values())
        
        if df.empty:
            logger.info("No campaign data found in database")
            return None
            
        # Convert numeric fields
        numeric_columns = ["bid", "impressions", "clicks", "daily_budget", "cpc", "roas", "spend", "orders", "conversion_rate", "acos"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert date fields
        date_columns = ["start_date", "end_date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        df.fillna(0, inplace=True)
        logger.info(f"Successfully loaded campaign data: {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading data from database: {str(e)}")
        return None

@api_view(['POST'])
def filter_campaigns(request):
    """
    API endpoint to filter campaign data based on user input with AND/OR logic.
    """
    logger.info("Received filter_campaigns request")
    
    # Get user_id from request if authenticated
    user_id = request.user.id if request.user.is_authenticated else None
    
    # Use the database function to get campaign data
    df = get_campaign_data(user_id)
    
    if df is None or df.empty:
        logger.warning("No campaign data available for filtering")
        return Response({"error": "No campaign data available"}, status=404)

    try:
        data = request.data
        logger.debug(f"Filter request data: {data}")

        main_operator = data.get("main_operator", "AND").upper()  # Default to AND
        conditions = data.get("conditions", [])

        logger.debug(f"Main operator: {main_operator}, Number of conditions: {len(conditions)}")

        if not isinstance(conditions, list) or not conditions:
            logger.warning("Invalid query format: conditions must be a non-empty list")
            return Response({"error": "Invalid query format. Expected a list of conditions."}, status=400)

        # Define field name mapping between API and database
        field_mapping = {
            "campaign_name": "product",  # Map campaign_name to product
            "campaignName": "product",   # Alternative capitalization
            # Add other mappings as needed
        }

        query_parts = []

        # Mapping JSON operators to Pandas query syntax
        operator_map = {
            "AND": "&",
            "OR": "|"
        }

        for i, condition in enumerate(conditions):
            if not isinstance(condition, dict) or "operator" not in condition or "filters" not in condition:
                logger.warning(f"Invalid condition format at index {i}: {condition}")
                return Response({"error": f"Invalid condition format at index {i}"}, status=400)

            operator = operator_map.get(condition["operator"].upper(), "&")  # Default to AND
            filters = condition["filters"]

            sub_query_parts = []
            for key, value in filters.items():
                # Map field names if needed
                mapped_key = field_mapping.get(key, key)
                
                # Check if the mapped field exists in the DataFrame
                if mapped_key not in df.columns:
                    logger.warning(f"Field '{mapped_key}' (mapped from '{key}') not found in DataFrame")
                    return Response({
                        "error": f"Unknown field: {key}",
                        "available_fields": list(df.columns)
                    }, status=400)
                
                if isinstance(value, dict):  # Handling range queries
                    min_val = value.get("min")
                    max_val = value.get("max")
                    if min_val is not None and max_val is not None:
                        sub_query_parts.append(f"({min_val} <= {mapped_key} <= {max_val})")
                    elif min_val is not None:
                        sub_query_parts.append(f"({mapped_key} >= {min_val})")
                    elif max_val is not None:
                        sub_query_parts.append(f"({mapped_key} <= {max_val})")
                else:
                    sub_query_parts.append(f"({mapped_key} == '{value}')")

            if sub_query_parts:
                sub_query = f" {operator} ".join(sub_query_parts)
                query_parts.append(f"({sub_query})")

        if not query_parts:
            logger.warning("No valid query parts generated from conditions")
            return Response({"error": "No valid filter conditions provided"}, status=400)

        full_query = f" {operator_map.get(main_operator, '&')} ".join(query_parts)
        logger.info(f"Generated pandas query: {full_query}")

        try:
            filtered_df = df.query(full_query, engine="python")  # Use safe Python engine
            logger.info(f"Filter applied successfully. Results: {len(filtered_df)} records")
        except Exception as e:
            logger.error(f"Error executing pandas query: {str(e)}")
            return Response({
                "error": f"Invalid query: {str(e)}",
                "available_fields": list(df.columns)  # Include available fields to help debugging
            }, status=400)

        result = filtered_df.to_dict(orient="records")
        return Response({"filtered_data": result, "count": len(result)})
        
    except Exception as e:
        logger.error(f"Unexpected error in filter_campaigns: {str(e)}")
        return Response({"error": "An unexpected error occurred", "details": str(e)}, status=500)
