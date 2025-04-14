import requests
from utils.logger import logger
import time

class APIClient:
    """
    A client for interacting with external APIs. It handles authentication, API calls,
    error handling, and retries.
    """
    def __init__(self, base_url: str, client_id: str, client_scope: str, access_token: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_scope = client_scope
        self.access_token = access_token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Amazon-Advertising-API-ClientId': self.client_id,
            'Amazon-Advertising-API-Scope': self.client_scope,
        }

    def make_get_request(self, endpoint: str, params: dict = None, retries: int = 3, delay: int = 5):
        """
        Makes a GET request to the API with the provided endpoint and parameters.
        It supports retries and delay between retries in case of failure.
        """
        url = f"{self.base_url}{endpoint}"
        attempt = 0
        while attempt < retries:
            try:
                logger.info(f"Making GET request to {url} with params: {params}")
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()  # Raises HTTPError for bad responses
                logger.info(f"Successfully fetched data from {url}. Status code: {response.status_code}")
                return response
            except requests.exceptions.HTTPError as http_err:
                logger.error(f"HTTP error occurred: {http_err}")
            except requests.exceptions.RequestException as err:
                logger.error(f"Error occurred: {err}")
            
            attempt += 1
            if attempt < retries:
                logger.info(f"Retrying... attempt {attempt}/{retries}")
                time.sleep(delay)
        
        logger.error(f"Failed to fetch data from {url} after {retries} attempts.")
        return None

    def make_post_request(self, endpoint: str, data: dict, retries: int = 3, delay: int = 5):
        """
        Makes a POST request to the API with the provided endpoint and data.
        It supports retries and delay between retries in case of failure.
        """
        url = f"{self.base_url}{endpoint}"
        attempt = 0
        while attempt < retries:
            try:
                logger.info(f"Making POST request to {url} with data: {data}")
                response = requests.post(url, json=data, headers=self.headers)
                response.raise_for_status()  # Raises HTTPError for bad responses
                logger.info(f"Successfully posted data to {url}. Status code: {response.status_code}")
                return response
            except requests.exceptions.HTTPError as http_err:
                logger.error(f"HTTP error occurred: {http_err}")
            except requests.exceptions.RequestException as err:
                logger.error(f"Error occurred: {err}")
            
            attempt += 1
            if attempt < retries:
                logger.info(f"Retrying... attempt {attempt}/{retries}")
                time.sleep(delay)
        
        logger.error(f"Failed to post data to {url} after {retries} attempts.")
        return None

    def make_put_request(self, endpoint: str, data: dict, retries: int = 3, delay: int = 5):
        """
        Makes a PUT request to the API with the provided endpoint and data.
        It supports retries and delay between retries in case of failure.
        """
        url = f"{self.base_url}{endpoint}"
        attempt = 0
        while attempt < retries:
            try:
                logger.info(f"Making PUT request to {url} with data: {data}")
                response = requests.put(url, json=data, headers=self.headers)
                response.raise_for_status()  # Raises HTTPError for bad responses
                logger.info(f"Successfully put data to {url}. Status code: {response.status_code}")
                return response
            except requests.exceptions.HTTPError as http_err:
                logger.error(f"HTTP error occurred: {http_err}")
            except requests.exceptions.RequestException as err:
                logger.error(f"Error occurred: {err}")
            
            attempt += 1
            if attempt < retries:
                logger.info(f"Retrying... attempt {attempt}/{retries}")
                time.sleep(delay)
        
        logger.error(f"Failed to put data to {url} after {retries} attempts.")
        return None

    def make_delete_request(self, endpoint: str, retries: int = 3, delay: int = 5):
        """
        Makes a DELETE request to the API with the provided endpoint.
        It supports retries and delay between retries in case of failure.
        """
        url = f"{self.base_url}{endpoint}"
        attempt = 0
        while attempt < retries:
            try:
                logger.info(f"Making DELETE request to {url}")
                response = requests.delete(url, headers=self.headers)
                response.raise_for_status()  # Raises HTTPError for bad responses
                logger.info(f"Successfully deleted data from {url}. Status code: {response.status_code}")
                return response
            except requests.exceptions.HTTPError as http_err:
                logger.error(f"HTTP error occurred: {http_err}")
            except requests.exceptions.RequestException as err:
                logger.error(f"Error occurred: {err}")
            
            attempt += 1
            if attempt < retries:
                logger.info(f"Retrying... attempt {attempt}/{retries}")
                time.sleep(delay)
        
        logger.error(f"Failed to delete data from {url} after {retries} attempts.")
        return None
