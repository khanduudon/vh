import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from bot.config import (
    CLASSPLUS_BASE_URL, API_TIMEOUT, MAX_RETRIES, 
    RETRY_BACKOFF_FACTOR, VALIDATE_SSL
)
from bot.exceptions import (
    OrgCodeNotFoundError, DownloadFailedError, 
    RateLimitExceededError, ParseError
)
from bot.logger import setup_logger, log_api_request, log_api_response

logger = setup_logger(__name__)


class ClassPlusExtractor:
    def __init__(self, base_url: str = CLASSPLUS_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = VALIDATE_SSL

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic and exponential backoff
        
        Args:
            url: Request URL
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional request parameters
            
        Returns:
            Response object
            
        Raises:
            DownloadFailedError: If request fails after retries
            RateLimitExceededError: If rate limit is exceeded
        """
        log_api_request(logger, method, url, **kwargs)
        
        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()
                response = self.session.request(
                    method, 
                    url, 
                    timeout=API_TIMEOUT,
                    **kwargs
                )
                duration = time.time() - start_time
                
                log_api_response(logger, response.status_code, url, duration)
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitExceededError(retry_after)
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_BACKOFF_FACTOR ** attempt
                    logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {MAX_RETRIES} attempts: {e}")
                    raise DownloadFailedError(url, str(e))
        
        raise DownloadFailedError(url, "Max retries exceeded")

    def fetch_course_info(self, course_id: str) -> Optional[Dict]:
        """
        Fetch course information (legacy method)
        
        Args:
            course_id: Course ID
            
        Returns:
            Course information dictionary or None
        """
        url = f"{self.base_url}/course/{course_id}"
        try:
            response = self._make_request(url)
            return self.parse_course_page(response.text)
        except Exception as e:
            logger.error(f"Failed to fetch course info for {course_id}: {e}")
            return None

    def parse_course_page(self, html_content: str) -> Dict:
        """
        Parse course page HTML content
        
        Args:
            html_content: HTML content
            
        Returns:
            Parsed course information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        course_info = {}
        
        try:
            # Extract course title
            title_elem = soup.find('h1', class_='course-title')
            if title_elem:
                course_info['title'] = title_elem.text.strip()
            
            # Extract course description
            desc_elem = soup.find('div', class_='course-description')
            if desc_elem:
                course_info['description'] = desc_elem.text.strip()
            
            return course_info
        except Exception as e:
            logger.error(f"Failed to parse course page: {e}")
            raise ParseError(html_content[:100], str(e))

    def fetch_org_batches(self, org_code: str) -> List[Dict]:
        """
        Fetch all batches for an organization code
        
        Args:
            org_code: Organization code
            
        Returns:
            List of batch metadata dictionaries
            
        Raises:
            OrgCodeNotFoundError: If org code is invalid
        """
        url = f"{self.base_url}/api/org/{org_code}/batches"
        
        try:
            response = self._make_request(url)
            data = response.json()
            
            # Check if org code is valid
            if not data or 'batches' not in data:
                raise OrgCodeNotFoundError(org_code)
            
            batches = data['batches']
            logger.info(f"Found {len(batches)} batches for org {org_code}")
            
            return batches
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise OrgCodeNotFoundError(org_code)
            raise DownloadFailedError(url, str(e))

    def fetch_batch_file_url(self, batch_id: str, org_code: str) -> str:
        """
        Get download URL for a specific batch file
        
        Args:
            batch_id: Batch file ID
            org_code: Organization code
            
        Returns:
            Download URL for the batch file
        """
        url = f"{self.base_url}/api/org/{org_code}/batch/{batch_id}/download"
        
        try:
            response = self._make_request(url)
            data = response.json()
            
            if 'download_url' not in data:
                raise ParseError(str(data), "Missing download_url in response")
            
            download_url = data['download_url']
            logger.info(f"Got download URL for batch {batch_id}")
            
            return download_url
            
        except requests.exceptions.HTTPError as e:
            raise DownloadFailedError(url, str(e))

    def download_batch_content(self, url: str) -> bytes:
        """
        Download batch file content from URL
        
        Args:
            url: Download URL
            
        Returns:
            File content as bytes
        """
        try:
            response = self._make_request(url, stream=True)
            
            # Download file content
            file_data = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_data += chunk
            
            logger.info(f"Downloaded {len(file_data)} bytes from {url}")
            return file_data
            
        except Exception as e:
            logger.error(f"Failed to download content from {url}: {e}")
            raise DownloadFailedError(url, str(e))


if __name__ == "__main__":
    extractor = ClassPlusExtractor(base_url="https://classplus.example.com")
    course_info = extractor.fetch_course_info(course_id="12345")
    print(course_info)
