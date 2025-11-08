# ClassPlus Course Extractor Bot

A bot to extract course information from ClassPlus without login access.

## Features

- Extracts course title, description, and other relevant information.
- Saves extracted data to a file.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from bot.extractor import ClassPlusExtractor

extractor = ClassPlusExtractor(base_url="https://classplus.example.com")
course_info = extractor.fetch_course_info(course_id="12345")
print(course_info)
```

## Testing

```bash
python -m unittest discover tests
```

## License

This project is licensed under the MIT License.
