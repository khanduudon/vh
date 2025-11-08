import requests
from bs4 import BeautifulSoup


class ClassPlusExtractor:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_course_info(self, course_id):
        url = f"{self.base_url}/course/{course_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return self.parse_course_page(response.text)
        else:
            return None

    def parse_course_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        course_info = {}
        # Extract course title
        course_info['title'] = soup.find('h1', class_='course-title').text.strip()
        # Extract course description
        course_info['description'] = soup.find('div', class_='course-description').text.strip()
        # Extract other relevant information
        # ...
        return course_info


if __name__ == "__main__":
    extractor = ClassPlusExtractor(base_url="https://classplus.example.com")
    course_info = extractor.fetch_course_info(course_id="12345")
    print(course_info)
