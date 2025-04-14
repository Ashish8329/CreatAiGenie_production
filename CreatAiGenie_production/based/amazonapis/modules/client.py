import logging
import time
import requests
from django.conf import settings
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)

class AmazonAdsAPIClient:
    """
    Client for interacting with Amazon Advertising API.
    Handles authentication, token refresh, and API requests with retry logic.
    """
    
    # API endpoints
    TOKEN_URL = "https://api.amazon.com/auth/o2/token"
    API_BASE_URL = "https://advertising-api-eu.amazon.com"
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(self, access_token=None, refresh_token=None):
        """
        Initialize the Amazon Ads API client.
        
        Args:
            access_token (str, optional): OAuth access token
            refresh_token (str, optional): OAuth refresh token
        """
        self.client_id = settings.AMAZON_ADS_CLIENT_ID
        self.client_secret = settings.AMAZON_ADS_CLIENT_SECRET
        self.redirect_uri = settings.AMAZON_ADS_REDIRECT_URI
        self.access_token = access_token
        self.refresh_token = refresh_token
    
    def get_auth_url(self):
        """
        Generate the OAuth authorization URL for Amazon Ads API.
        
        Returns:
            str: Authorization URL
        """
        return (
            f"https://www.amazon.com/ap/oa?scope=advertising::campaign_management"
            f"&response_type=code&client_id={self.client_id}&state=State"
            f"&redirect_uri={self.redirect_uri}"
        )
    
    def exchange_auth_code(self, code, user=None):
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code (str): Authorization code from OAuth redirect
            user (User, optional): Django user to associate tokens with
            
        Returns:
            dict: Token response containing access_token and refresh_token
            
        Raises:
            ValueError: If token exchange fails
        """
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        
        try:
            response = self._make_request("POST", self.TOKEN_URL, data=payload)
            
            if "access_token" in response:
                self.access_token = response["access_token"]
                self.refresh_token = response.get("refresh_token")
                
                # Save tokens to database if user is provided
                if user and self.refresh_token:
                    from based.models import AmazonAdsToken
                    AmazonAdsToken.objects.update_or_create(
                        user=user,
                        defaults={
                            'access_token': self.access_token,
                            'refresh_token': self.refresh_token
                        }
                    )
                    logger.info(f"Saved Amazon Ads tokens for user {user.id}")
                
                return response
            else:
                logger.error(f"Failed to exchange auth code: {response}")
                raise ValueError("Failed to fetch access token")
                
        except RequestException as e:
            logger.error(f"Request error during auth code exchange: {str(e)}")
            raise ValueError(f"Authentication request failed: {str(e)}")

    
    def refresh_access_token(self, user=None):
        """
        Refresh the access token using the refresh token.
        
        Args:
            user (User, optional): Django user to get/update tokens for
            
        Returns:
            str: New access token
            
        Raises:
            ValueError: If refresh fails or no refresh token is available
        """
        # If user is provided, try to get refresh token from database
        if user and not self.refresh_token:
            from based.models import AmazonAdsToken
            try:
                token_obj = AmazonAdsToken.objects.get(user=user)
                self.refresh_token = token_obj.refresh_token
                logger.info(f"Retrieved refresh token from database for user {user.id}")
            except AmazonAdsToken.DoesNotExist:
                logger.error(f"No refresh token found in database for user {user.id}")
        
        if not self.refresh_token:
            logger.error("No refresh token available")
            raise ValueError("No refresh token available")
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = self._make_request("POST", self.TOKEN_URL, data=payload)
            
            if "access_token" in response:
                self.access_token = response["access_token"]
                
                # If user is provided, update the access token in the database
                if user:
                    from based.models import AmazonAdsToken
                    AmazonAdsToken.objects.update_or_create(
                        user=user,
                        defaults={
                            'access_token': self.access_token,
                            # Update refresh token if a new one is provided
                            'refresh_token': response.get('refresh_token', self.refresh_token)
                        }
                    )
                    logger.info(f"Updated access token in database for user {user.id}")
                
                logger.info("Successfully refreshed access token")
                return self.access_token
            else:
                logger.error(f"Failed to refresh token: {response}")
                raise ValueError("Failed to refresh access token")
                
        except RequestException as e:
            logger.error(f"Request error during token refresh: {str(e)}")
            raise ValueError(f"Token refresh request failed: {str(e)}")

        
    
    def get_request_headers(self, profile_id=None):
        """
        Get headers required for Amazon Ads API requests.
        
        Args:
            profile_id (str, optional): Amazon Ads profile ID
            
        Returns:
            dict: Headers for API requests
            
        Raises:
            ValueError: If access token is not available
        """
        if not self.access_token:
            self.refresh_access_token()
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Amazon-Advertising-API-ClientId": self.client_id,
            "Content-Type": "application/json"
        }
        
        if profile_id:
            headers["Amazon-Advertising-API-Scope"] = profile_id
            
        return headers
    
    def _make_request(self, method, url, headers=None, data=None, json=None, retries=MAX_RETRIES):
        """
        Make an HTTP request with retry logic for transient failures.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): Request URL
            headers (dict, optional): HTTP headers
            data (dict, optional): Form data for request
            json (dict, optional): JSON data for request
            retries (int): Number of retries for transient failures
            
        Returns:
            dict: JSON response
            
        Raises:
            RequestException: If request fails after all retries
        """
        attempt = 0
        last_exception = None
        
        while attempt < retries:
            try:
                logger.debug(f"Making {method} request to {url}")
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json,
                    timeout=30
                )
                
                # Log response details
                logger.debug(f"Response status: {response.status_code}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', self.RETRY_DELAY))
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds")
                    time.sleep(retry_after)
                    attempt += 1
                    continue
                
                # Handle authentication errors - try to refresh token
                if response.status_code == 401 and self.refresh_token and attempt == 0:
                    logger.info("Received 401, attempting to refresh token")
                    self.refresh_access_token()
                    if headers and 'Authorization' in headers:
                        headers['Authorization'] = f"Bearer {self.access_token}"
                    attempt += 1
                    continue
                
                # Raise exception for other error status codes
                response.raise_for_status()
                
                return response.json()
                
            except (ConnectionError, Timeout) as e:
                last_exception = e
                wait_time = self.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Transient error: {str(e)}. Retrying in {wait_time}s. Attempt {attempt+1}/{retries}")
                time.sleep(wait_time)
                attempt += 1
            except RequestException as e:
                # Don't retry non-transient errors
                logger.error(f"Request failed: {str(e)}")
                raise
        
        # If we get here, we've exhausted our retries
        logger.error(f"Request failed after {retries} retries")
        if last_exception:
            raise last_exception
        raise RequestException("Request failed after maximum retries")
