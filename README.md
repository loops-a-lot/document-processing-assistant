# Document Processing Assistant

A Streamlit-based web application for Operations Analysts to efficiently review and process documents with extracted data in a human-in-the-loop workflow.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Features

- **Document Viewer**: Support for PDF, images, and XML files
- **JSON Editor**: Edit extracted data with rules visualization
- **OCR Visualization**: View OCR data with bounding boxes
- **Smart Search**: Find text in documents quickly
- **Chat Interface**: Interact with documents through natural language
- **Provenance Tracking**: Full audit trail for all data changes

## Quick Start

### Using the Installation Script

```bash
# Clone the repository
git clone https://github.com/cknouss/document-processing-assistant.git
cd document-processing-assistant

# Run the install script to set up the project
python install.py

# Install dependencies
cd document_processing_assistant
pip install -r requirements.txt

# Run the application
streamlit run app/main.py
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/cknouss/document-processing-assistant.git
cd document-processing-assistant/document_processing_assistant

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/main.py
```

## Usage

1. Upload a document (PDF, image, or XML)
2. Upload the extracted JSON data
3. Optionally upload OCR data (AWS Textract format)
4. Upload review guidelines in markdown format
5. Review and edit the extracted data
6. Save edited data with provenance tracking

## Docker Deployment

To run the application in a Docker container:
```bash
docker build -t doc-processing-assistant .
docker run -p 8501:8501 doc-processing-assistant
```

Then navigate to http://localhost:8501 in your browser.

## Project Structure

```
document_processing_assistant/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main Streamlit application
│   ├── components/             # UI Components
│   ├── utils/                  # Utility functions
│   └── models/                 # Data models
│
├── data/                       # Sample data
│   ├── sample_documents/
│   ├── sample_extractions/
│   ├── sample_ocr/
│   └── guidelines/
│
├── tests/                      # Unit tests
├── requirements.txt
├── Dockerfile
└── .streamlit/                 # Streamlit configuration
```

## Development

### Setting Up Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.