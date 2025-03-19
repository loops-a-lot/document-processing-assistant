# Placeholder for README.md
# Replace this with the actual content from GitHub repository or other source

Folder Structure
document_processing_assistant/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main Streamlit application
│   ├── components/
│   │   ├── __init__.py
│   │   ├── document_viewer.py  # PDF/Image/XML viewer component
│   │   ├── json_editor.py      # JSON data editor with rules display
│   │   ├── guidelines.py       # Guidelines viewer component
│   │   ├── chat.py             # Document chat component
│   │   ├── ocr_viewer.py       # OCR visualization with bounding boxes
│   │   └── search.py           # Advanced semantic search component
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_handling.py    # File loading/saving utilities
│   │   ├── json_manager.py     # JSON handling and provenance tracking
│   │   ├── ocr_parser.py       # AWS Textract OCR data processor
│   │   ├── search_engine.py    # Semantic search implementation
│   │   └── auth_stub.py        # Authentication stub for future implementation
│   │
│   └── models/
│       ├── __init__.py
│       ├── document.py         # Document data model
│       ├── extraction.py       # Extracted data model
│       └── audit.py            # Audit and provenance model
│
├── data/
│   ├── sample_documents/       # Sample PDFs, images, XMLs
│   ├── sample_extractions/     # Sample JSON extraction files
│   ├── sample_ocr/             # Sample OCR data
│   └── guidelines/             # Sample markdown guidelines
│
├── tests/
│   ├── __init__.py
│   ├── test_document_viewer.py
│   ├── test_json_editor.py
│   ├── test_guidelines.py
│   ├── test_json_manager.py
│   └── test_search.py
│
├── requirements.txt
├── Dockerfile
├── README.md
└── setup.py


# Document Processing Assistant

A Streamlit-based application for Operations Analysts to efficiently review and process documents with extracted data.

## Features

- Document viewer for PDF, images, and XML files
- JSON editor for extracted data with rules visualization
- Guidelines viewer for reference during review
- OCR visualization with bounding boxes
- Document search with different matching options
- Document chat interface
- Provenance tracking for all data changes

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/document-processing-assistant.git
   cd document-processing-assistant
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
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
docker build -t doc-processing-assistant . docker run -p 8501:8501 doc-processing-assistant ```

Then navigate to http://localhost:8501 in your browser.


# Development
## Project Structure

app/: Main application code
components/: UI components
utils/: Utility functions
models/: Data models
data/: Sample data files
tests/: Unit tests

## Running Tests

pytest tests/
