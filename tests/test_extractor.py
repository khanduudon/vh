import unittest
from bot.extractor import ClassPlusExtractor


class TestClassPlusExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = ClassPlusExtractor(base_url="https://classplus.example.com")

    def test_fetch_course_info(self):
        course_info = self.extractor.fetch_course_info(course_id="12345")
        self.assertIsNotNone(course_info)
        self.assertIn('title', course_info)
        self.assertIn('description', course_info)


if __name__ == "__main__":
    unittest.main()
