#!/usr/bin/env python3
"""
Complete installation script for Document Processing Assistant project.
This script will recreate the entire repository structure and content.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path

# Define project configuration
PROJECT_ROOT = "document_processing_assistant"

# File structure with content (in a single file)
FILES = {
    # Configuration files
    "requirements.txt": """# Core dependencies
streamlit
pandas==2.0.3
pillow
pymupdf==1.22.5
markdown==3.4.4
pytest==7.4.0
numpy==1.25.2
""",
    
    "README.md": """# Document Processing Assistant

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
```
docker build -t doc-processing-assistant .
docker run -p 8501:8501 doc-processing-assistant
```

Then navigate to http://localhost:8501 in your browser.

## Development

### Project Structure

- app/: Main application code
- components/: UI components
- utils/: Utility functions
- models/: Data models
- data/: Sample data files
- tests/: Unit tests
""",

    "Dockerfile": """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py"]
""",

    # Streamlit config
    ".streamlit/config.toml": """[ui]
# Hide the "Deploy" button
deploy = false

[server]
# By default, streamlit checks for package updates and displays a message on startup.
# This can be disabled.
enableServerHeadless = true

[deprecation]
# Disable deprecation warnings
showPyplotGlobalUse = false
""",

    # Main application files
    "app/main.py": """import os
import streamlit as st
import json
import time
from datetime import datetime
import uuid

from components.document_viewer import DocumentViewer
from components.json_editor import JsonEditor
from components.guidelines import GuidelinesViewer
from components.chat import DocumentChat
from components.ocr_viewer import OcrViewer
from components.search import DocumentSearch

from utils.file_handling import load_file, save_file
from utils.json_manager import update_json_with_provenance
from utils.auth_stub import get_user_identity

# Page configuration
st.set_page_config(
    page_title="Document Processing Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Session state initialization
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "email": ""}
if 'document_path' not in st.session_state:
    st.session_state.document_path = None
if 'json_path' not in st.session_state:
    st.session_state.json_path = None
if 'ocr_path' not in st.session_state:
    st.session_state.ocr_path = None
if 'guidelines_path' not in st.session_state:
    st.session_state.guidelines_path = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def main():
    """Main application entry point"""
    st.title("Document Processing Assistant")
    
    # Sidebar for file selection and user info
    with st.sidebar:
        st.header("Files and Settings")
        
        # User identification (placeholder for authentication)
        st.subheader("User Information")
        user_name = st.text_input("Name", st.session_state.user_info.get("name", ""))
        user_email = st.text_input("Email", st.session_state.user_info.get("email", ""))
        
        if user_name and user_email:
            st.session_state.user_info = {"name": user_name, "email": user_email}
            st.success("User information saved")
        
        st.divider()
        
        # Document selection
        st.subheader("Select Document")
        uploaded_document = st.file_uploader("Upload Document (PDF/Image/XML)", 
                                          type=["pdf", "jpg", "jpeg", "png", "xml"],
                                          key="document_uploader")
        
        if uploaded_document:
            document_path = os.path.join("./temp", uploaded_document.name)
            save_file(uploaded_document, document_path)
            st.session_state.document_path = document_path
            st.success(f"Document loaded: {uploaded_document.name}")
        
        # JSON data selection
        st.subheader("Select Extracted Data")
        uploaded_json = st.file_uploader("Upload JSON Extraction", 
                                      type=["json"],
                                      key="json_uploader")
        
        if uploaded_json:
            json_path = os.path.join("./temp", uploaded_json.name)
            save_file(uploaded_json, json_path)
            st.session_state.json_path = json_path
            st.success(f"JSON data loaded: {uploaded_json.name}")
        
        # Optional OCR data selection
        st.subheader("Select OCR Data (Optional)")
        uploaded_ocr = st.file_uploader("Upload OCR Data", 
                                      type=["json"],
                                      key="ocr_uploader")
        
        if uploaded_ocr:
            ocr_path = os.path.join("./temp", uploaded_ocr.name)
            save_file(uploaded_ocr, ocr_path)
            st.session_state.ocr_path = ocr_path
            st.success(f"OCR data loaded: {uploaded_ocr.name}")
        
        # Guidelines selection
        st.subheader("Select Guidelines")
        uploaded_guidelines = st.file_uploader("Upload Guidelines", 
                                           type=["md", "txt"],
                                           key="guidelines_uploader")
        
        if uploaded_guidelines:
            guidelines_path = os.path.join("./temp", uploaded_guidelines.name)
            save_file(uploaded_guidelines, guidelines_path)
            st.session_state.guidelines_path = guidelines_path
            st.success(f"Guidelines loaded: {uploaded_guidelines.name}")
            
        # Layout options
        st.subheader("Layout Options")
        show_chat = st.checkbox("Show Chat Window", value=False)
        show_ocr = st.checkbox("Show OCR Visualization", value=True)
        show_search = st.checkbox("Show Search Tool", value=True)

    # Main content area with tabs
    if not st.session_state.document_path or not st.session_state.json_path:
        st.info("Please upload a document and JSON extraction data to begin.")
        return
    
    # Create flexible layout using columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Document viewer
        st.header("Document Viewer")
        document_viewer = DocumentViewer(st.session_state.document_path)
        document_viewer.render()
        
        # OCR visualization if enabled and available
        if show_ocr and st.session_state.ocr_path:
            st.header("OCR Visualization")
            ocr_viewer = OcrViewer(st.session_state.document_path, st.session_state.ocr_path)
            ocr_viewer.render()
            
        # Search tool if enabled
        if show_search:
            st.header("Document Search")
            search_tool = DocumentSearch(st.session_state.document_path, st.session_state.ocr_path)
            search_tool.render()
    
    with col2:
        # Guidelines viewer
        if st.session_state.guidelines_path:
            st.header("Guidelines")
            guidelines_viewer = GuidelinesViewer(st.session_state.guidelines_path)
            guidelines_viewer.render()
        
        # JSON editor with rules
        st.header("Extracted Data Editor")
        json_editor = JsonEditor(st.session_state.json_path, st.session_state.user_info)
        updated_data = json_editor.render()
        
        # Save button for edited JSON
        if st.button("Save Edited Data"):
            if updated_data:
                # Generate a new filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                original_filename = os.path.basename(st.session_state.json_path)
                name_without_ext = os.path.splitext(original_filename)[0]
                new_filename = f"{name_without_ext}_edited_{timestamp}.json"
                new_path = os.path.join("./temp", new_filename)
                
                # Save the updated JSON with provenance
                with open(new_path, 'w') as f:
                    json.dump(updated_data, f, indent=2)
                
                st.success(f"Saved edited data to {new_filename}")
                
                # Update the session to use the new file
                st.session_state.json_path = new_path
    
    # Chat window (collapsible)
    if show_chat:
        st.header("Document Chat")
        chat_component = DocumentChat(
            document_path=st.session_state.document_path,
            json_path=st.session_state.json_path,
            ocr_path=st.session_state.ocr_path,
            chat_history=st.session_state.chat_history
        )
        st.session_state.chat_history = chat_component.render()

if __name__ == "__main__":
    # Create temp directory if it doesn't exist
    os.makedirs("./temp", exist_ok=True)
    main()
""",

    "app/__init__.py": "# Document Processing Assistant Application",

    # Components
    "app/components/__init__.py": "# UI Components",

    "app/components/document_viewer.py": """import os
import streamlit as st
import base64
from PIL import Image
import xml.dom.minidom
from utils.file_handling import load_file

class DocumentViewer:
    """Document viewer component for PDF, images, and XML files"""
    
    def __init__(self, document_path):
        """Initialize the document viewer
        
        Args:
            document_path: Path to the document file
        """
        self.document_path = document_path
        self.file_extension = os.path.splitext(document_path)[1].lower()
    
    def render(self):
        """Render the document viewer in the Streamlit UI"""
        if not os.path.exists(self.document_path):
            st.error(f"Document file not found: {self.document_path}")
            return
        
        # Handle different file types
        if self.file_extension == ".pdf":
            self._render_pdf()
        elif self.file_extension in [".jpg", ".jpeg", ".png"]:
            self._render_image()
        elif self.file_extension == ".xml":
            self._render_xml()
        else:
            st.error(f"Unsupported file type: {self.file_extension}")
    
    def _render_pdf(self):
        """Render a PDF document"""
        # Display PDF using an iframe and base64 encoding
        with open(self.document_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        # Create a resizable container with the PDF
        pdf_height = st.slider("PDF Viewer Height", 400, 1000, 600, key="pdf_height_slider")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="{pdf_height}" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # Add download button
        st.download_button(
            label="Download PDF",
            data=open(self.document_path, "rb"),
            file_name=os.path.basename(self.document_path),
            mime="application/pdf"
        )
    
    def _render_image(self):
        """Render an image document"""
        image = Image.open(self.document_path)
        
        # Create a resizable image viewer
        img_width = st.slider("Image Width", 300, 1000, 600, key="img_width_slider")
        st.image(image, width=img_width)
        
        # Add download button
        st.download_button(
            label="Download Image",
            data=open(self.document_path, "rb"),
            file_name=os.path.basename(self.document_path),
            mime=f"image/{self.file_extension[1:]}"
        )
    
    def _render_xml(self):
        """Render an XML document"""
        try:
            with open(self.document_path, 'r') as f:
                xml_content = f.read()
            
            # Pretty format the XML
            dom = xml.dom.minidom.parseString(xml_content)
            pretty_xml = dom.toprettyxml()
            
            # Display with syntax highlighting
            st.code(pretty_xml, language="xml")
            
            # Add download button
            st.download_button(
                label="Download XML",
                data=pretty_xml,
                file_name=os.path.basename(self.document_path),
                mime="application/xml"
            )
        except Exception as e:
            st.error(f"Error rendering XML: {e}")
""",

    "app/components/json_editor.py": """import streamlit as st
import json
import pandas as pd
from datetime import datetime
from utils.json_manager import update_json_with_provenance

class JsonEditor:
    """Component for displaying and editing extracted JSON data with rules"""
    
    def __init__(self, json_path, user_info):
        """Initialize the JSON editor
        
        Args:
            json_path: Path to the JSON file with extracted data
            user_info: Dictionary with user information (name, email)
        """
        self.json_path = json_path
        self.user_info = user_info
        self.data = self._load_json()
    
    def _load_json(self):
        """Load JSON data from file"""
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading JSON data: {e}")
            return {"values": [], "_provenance": []}
    
    def render(self):
        """Render the JSON editor in the Streamlit UI
        
        Returns:
            The updated JSON data after any edits
        """
        if not self.data:
            st.error("No JSON data available to edit")
            return None
        
        # Ensure the data has the expected structure
        if "values" not in self.data:
            self.data["values"] = []
        if "_provenance" not in self.data:
            self.data["_provenance"] = []
        
        # Create a DataFrame for easier editing
        values_data = []
        for i, item in enumerate(self.data["values"]):
            row = {
                "id": i,
                "name": item.get("name", ""),
                "value": item.get("value", ""),
                "type": item.get("type", ""),
            }
            
            # Add rules if they exist
            if "rules" in item:
                if isinstance(item["rules"], list):
                    row["rules"] = ", ".join(item["rules"])
                else:
                    row["rules"] = str(item["rules"])
            else:
                row["rules"] = ""
                
            values_data.append(row)
        
        df = pd.DataFrame(values_data)
        
        # Display the data editor
        if len(df) > 0:
            st.write("Edit values below:")
            edited_df = st.data_editor(
                df,
                column_config={
                    "id": st.column_config.Column("ID", disabled=True, width="small"),
                    "name": st.column_config.Column("Field Name", width="medium"),
                    "value": st.column_config.Column("Value", width="medium"),
                    "type": st.column_config.SelectboxColumn(
                        "Type",
                        width="small",
                        options=["string", "number", "boolean", "date", "array", "object"]
                    ),
                    "rules": st.column_config.Column("Rules", width="large"),
                },
                num_rows="dynamic",
                key="json_editor"
            )
            
            # Add a section for edit notes
            st.subheader("Edit Notes")
            edit_notes = st.text_area(
                "Enter notes about your edits (will be saved in provenance):",
                key="edit_notes"
            )
            
            # Process changes
            if not edited_df.equals(df):
                # Find changes
                changes = []
                
                # Check for row additions and modifications
                for _, row in edited_df.iterrows():
                    row_id = row["id"]
                    
                    # Handle new rows (those with id beyond original data)
                    if row_id >= len(self.data["values"]):
                        changes.append({
                            "field": row["name"],
                            "old_value": None,
                            "new_value": row["value"],
                            "action": "added"
                        })
                    # Handle modified rows
                    elif (row["name"] != df.loc[df["id"] == row_id, "name"].values[0] or
                          row["value"] != df.loc[df["id"] == row_id, "value"].values[0] or
                          row["type"] != df.loc[df["id"] == row_id, "type"].values[0] or
                          row["rules"] != df.loc[df["id"] == row_id, "rules"].values[0]):
                        changes.append({
                            "field": row["name"],
                            "old_value": df.loc[df["id"] == row_id, "value"].values[0],
                            "new_value": row["value"],
                            "action": "modified"
                        })
                
                # Check for row deletions
                original_ids = set(df["id"])
                current_ids = set(edited_df["id"])
                deleted_ids = original_ids - current_ids
                
                for id_val in deleted_ids:
                    deleted_row = df.loc[df["id"] == id_val].iloc[0]
                    changes.append({
                        "field": deleted_row["name"],
                        "old_value": deleted_row["value"],
                        "new_value": None,
                        "action": "deleted"
                    })
                
                # Update the JSON data with changes
                updated_values = []
                for _, row in edited_df.iterrows():
                    # Convert rules back to list if needed
                    rules = row["rules"]
                    if isinstance(rules, str) and rules:
                        rules = [r.strip() for r in rules.split(",")]
                    
                    updated_values.append({
                        "name": row["name"],
                        "value": row["value"],
                        "type": row["type"],
                        "rules": rules if rules else []
                    })
                
                # Update the data
                self.data["values"] = updated_values
                
                # Add provenance
                if changes:
                    provenance_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "user": self.user_info,
                        "document": self.json_path,
                        "changes": changes,
                        "notes": edit_notes
                    }
                    self.data["_provenance"].append(provenance_entry)
                    
                    # Show summary of changes
                    st.subheader("Changes Detected")
                    changes_df = pd.DataFrame(changes)
                    st.dataframe(changes_df)
            
            # Display provenance information
            if self.data["_provenance"]:
                with st.expander("View Edit History"):
                    for i, entry in enumerate(reversed(self.data["_provenance"])):
                        st.write(f"**Edit {i+1}**: {entry['timestamp']}")
                        st.write(f"**User**: {entry['user'].get('name', 'Unknown')} ({entry['user'].get('email', 'No email')})")
                        st.write(f"**Document**: {entry['document']}")
                        st.write("**Changes**:")
                        changes_df = pd.DataFrame(entry["changes"])
                        st.dataframe(changes_df)
                        if entry.get("notes"):
                            st.write(f"**Notes**: {entry['notes']}")
                        st.divider()
            
            return self.data
        else:
            st.info("No data values found. Add values using the 'Add row' button.")
            return self.data
""",

    "app/components/guidelines.py": """import streamlit as st
import markdown
from utils.file_handling import load_file

class GuidelinesViewer:
    """Guidelines viewer component for displaying review guidelines in markdown"""
    
    def __init__(self, guidelines_path):
        """Initialize the guidelines viewer
        
        Args:
            guidelines_path: Path to the guidelines file (markdown or text)
        """
        self.guidelines_path = guidelines_path
        
    def render(self):
        """Render the guidelines in the Streamlit UI"""
        try:
            # Load the guidelines file
            with open(self.guidelines_path, 'r') as f:
                content = f.read()
            
            # Create tabs for different viewing options
            tab1, tab2 = st.tabs(["Formatted", "Raw"])
            
            with tab1:
                # Display formatted markdown
                st.markdown(content)
            
            with tab2:
                # Display raw content
                st.code(content)
                
            # Add download button
            st.download_button(
                label="Download Guidelines",
                data=content,
                file_name=f"guidelines.md",
                mime="text/markdown"
            )
                
        except Exception as e:
            st.error(f"Error loading guidelines: {e}")
""",

    "app/components/chat.py": """import streamlit as st
import time
import json
from datetime import datetime
from utils.file_handling import load_file

class DocumentChat:
    """Chat component for interacting with documents"""
    
    def __init__(self, document_path, json_path=None, ocr_path=None, chat_history=None):
        """Initialize the document chat component
        
        Args:
            document_path: Path to the main document
            json_path: Path to the JSON extraction data (optional)
            ocr_path: Path to the OCR data (optional)
            chat_history: Previous chat history (optional)
        """
        self.document_path = document_path
        self.json_path = json_path
        self.ocr_path = ocr_path
        self.chat_history = chat_history or []
    
    def render(self):
        """Render the chat interface
        
        Returns:
            Updated chat history
        """
        st.info("This is a placeholder for the chat interface. In a production environment, this would connect to an LLM.")
        
        # Display chat history
        for message in self.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        prompt = st.chat_input("Ask a question about the document...")
        
        if prompt:
            # Add user message to chat history
            self.chat_history.append({"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Simulate processing
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.text("Thinking...")
                
                # In a real implementation, this would call an LLM API
                time.sleep(1)  # Simulate processing delay
                
                # Generate a placeholder response
                if "invoice" in prompt.lower() or "document" in prompt.lower():
                    response = f"This appears to be an invoice document. I can see various fields like invoice number, dates, and line items. What specific information would you like to know about it?"
                elif "data" in prompt.lower() or "extraction" in prompt.lower():
                    response = f"The JSON data contains extracted fields from the document. These include metadata and values that have been processed. Is there a specific field you're interested in?"
                elif "help" in prompt.lower():
                    response = "I can help you review this document and the extracted data. You can ask me about specific fields, verification of values, or suggestions for corrections."
                else:
                    response = "I'm a document assistant here to help you review this document and its extracted data. What would you like to know about it?"
                
                # Display the response
                message_placeholder.text(response)
                
                # Add assistant response to chat history
                self.chat_history.append({"role": "assistant", "content": response, "timestamp": datetime.now().isoformat()})
        
        return self.chat_history
""",

    "app/components/ocr_viewer.py": """import streamlit as st
import json
import base64
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io
from utils.file_handling import load_file
from utils.ocr_parser import parse_textract_blocks

class OcrViewer:
    """OCR visualization component with bounding boxes"""
    
    def __init__(self, document_path, ocr_path):
        """Initialize the OCR viewer
        
        Args:
            document_path: Path to the document file
            ocr_path: Path to the OCR data file (AWS Textract format)
        """
        self.document_path = document_path
        self.ocr_path = ocr_path
        self.document_ext = document_path.split('.')[-1].lower()
        self.ocr_data = self._load_ocr_data()
    
    def _load_ocr_data(self):
        """Load OCR data from file"""
        try:
            with open(self.ocr_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading OCR data: {e}")
            return None
    
    def render(self):
        """Render the OCR visualization"""
        if not self.ocr_data:
            st.error("No OCR data available to visualize")
            return
        
        # Parse the OCR blocks
        blocks = parse_textract_blocks(self.ocr_data)
        
        if not blocks:
            st.error("No text blocks found in OCR data")
            return
        
        # Get document pages
        pages = []
        if self.document_ext == 'pdf':
            pdf_doc = fitz.open(self.document_path)
            for page_num in range(len(pdf_doc)):
                # Convert PDF page to image
                page = pdf_doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                pages.append((page_num + 1, Image.open(io.BytesIO(img_data))))
        else:
            # Single image document
            pages = [(1, Image.open(self.document_path))]
        
        # Create visualization options
        st.subheader("Visualization Options")
        show_text = st.checkbox("Show Text", value=True)
        show_confidence = st.checkbox("Show Confidence", value=False)
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 100.0, 80.0, 1.0)
        
        # Convert confidence threshold to fraction
        confidence_threshold /= 100.0
        
        # Filter blocks by confidence
        filtered_blocks = [block for block in blocks if block.get('Confidence', 100.0) / 100.0 >= confidence_threshold]
        
        st.write(f"Showing {len(filtered_blocks)} of {len(blocks)} text blocks (confidence >= {confidence_threshold:.2f})")
        
        # Display visualizations
        for page_num, img in pages:
            st.subheader(f"Page {page_num}")
            
            # Create a copy of the image for drawing
            img_draw = img.copy()
            draw = ImageDraw.Draw(img_draw)
            
            # Draw bounding boxes for blocks on this page
            page_blocks = [block for block in filtered_blocks if block.get('Page', 1) == page_num]
            
            for block in page_blocks:
                if 'Geometry' in block and 'BoundingBox' in block['Geometry']:
                    bbox = block['Geometry']['BoundingBox']
                    
                    # Convert relative coordinates to absolute
                    img_width, img_height = img.size
                    left = bbox['Left'] * img_width
                    top = bbox['Top'] * img_height
                    width = bbox['Width'] * img_width
                    height = bbox['Height'] * img_height
                    
                    # Draw rectangle
                    draw.rectangle(
                        [(left, top), (left + width, top + height)],
                        outline="red",
                        width=2
                    )
                    
                    # Draw text if enabled
                    if show_text and 'Text' in block:
                        text = block['Text']
                        if show_confidence and 'Confidence' in block:
                            text += f" ({block['Confidence']:.1f}%)"
                        
                        # Draw white background for text
                        text_width = len(text) * 7  # Approximate width
                        draw.rectangle(
                            [(left, top - 15), (left + text_width, top)],
                            fill="white"
                        )
                        
                        # Draw text
                        draw.text((left, top - 15), text, fill="black")
            
            # Display the image with bounding boxes
            st.image(img_draw, use_column_width=True)
            
            # Add option to download the visualized image
            buffered = io.BytesIO()
            img_draw.save(buffered, format="PNG")
            st.download_button(
                label=f"Download Page {page_num} with OCR",
                data=buffered.getvalue(),
                file_name=f"ocr_page_{page_num}.png",
                mime="image/png"
            )
""",

    "app/components/search.py": """import streamlit as st
import os
import json
import re
from utils.file_handling import load_file
from utils.ocr_parser import parse_textract_blocks

class DocumentSearch:
    """Document search component for finding text in documents"""
    
    def __init__(self, document_path, ocr_path=None):
        """Initialize the document search component
        
        Args:
            document_path: Path to the document file
            ocr_path: Path to the OCR data file (optional)
        """
        self.document_path = document_path
        self.ocr_path = ocr_path
        self.document_ext = document_path.split('.')[-1].lower()
        self.ocr_data = self._load_ocr_data() if ocr_path else None
    
    def _load_ocr_data(self):
        """Load OCR data from file"""
        try:
            with open(self.ocr_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading OCR data: {e}")
            return None
    
    def _get_document_text(self):
        """Get text content from the document"""
        if self.document_ext == 'xml':
            with open(self.document_path, 'r') as f:
                return f.read()
        elif self.ocr_data:
            # If OCR data is available, use it
            blocks = parse_textract_blocks(self.ocr_data)
            return " ".join([block.get('Text', '') for block in blocks if 'Text' in block])
        else:
            # For other document types without OCR, display a message
            return ""
    
    def render(self):
        """Render the search interface"""
        # Get document text
        document_text = self._get_document_text()
        
        if not document_text:
            if not self.ocr_data:
                st.warning("Search requires OCR data for this document type. Please upload OCR data.")
            else:
                st.error("No text content found in the document")
            return
        
        # Search interface
        st.subheader("Search Document")
        search_query = st.text_input("Enter search term:", key="document_search")
        
        # Search options
        col1, col2 = st.columns(2)
        with col1:
            case_sensitive = st.checkbox("Case sensitive", value=False)
        with col2:
            whole_word = st.checkbox("Whole words only", value=False)
        
        if search_query:
            # Prepare search pattern
            if whole_word:
                pattern = r'\b' + re.escape(search_query) + r'\b'
            else:
                pattern = re.escape(search_query)
            
            # Set flags
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Perform search
            matches = list(re.finditer(pattern, document_text, flags))
            
            if matches:
                st.success(f"Found {len(matches)} matches")
                
                # Display matches with context
                for i, match in enumerate(matches):
                    start = max(0, match.start() - 50)
                    end = min(len(document_text), match.end() + 50)
                    
                    # Get context text
                    before = document_text[start:match.start()]
                    matched = document_text[match.start():match.end()]
                    after = document_text[match.end():end]
                    
                    # Display with formatting
                    st.markdown(f"**Match {i+1}:**")
                    st.markdown(f"...{before}**__{matched}__**{after}...")
                    st.divider()
            else:
                st.warning(f"No matches found for '{search_query}'")
""",

    # Utils
    "app/utils/__init__.py": "# Utility modules",

    "app/utils/file_handling.py": """import os
import json
import shutil
import tempfile

def load_file(file_path):
    """Load a file from disk
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        File content as bytes or string depending on the file type
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Binary files
    if file_extension in ['.pdf', '.jpg', '.jpeg', '.png']:
        with open(file_path, 'rb') as f:
            return f.read()
    
    # Text files
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Parse JSON if it's a JSON file
            if file_extension == '.json':
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON format in {file_path}")
            
            return content

def save_file(file_obj, file_path):
    """Save a file to disk
    
    Args:
        file_obj: File object or content to save
        file_path: Path to save the file to
        
    Returns:
        Path to the saved file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Handle different file types
    if hasattr(file_obj, 'read'):
        # Handle StreamlitUploadedFile objects
        with open(file_path, 'wb') as f:
            f.write(file_obj.read())
    elif isinstance(file_obj, bytes):
        # Handle binary data
        with open(file_path, 'wb') as f:
            f.write(file_obj)
    elif isinstance(file_obj, str):
        # Handle string content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_obj)
    elif isinstance(file_obj, dict) or isinstance(file_obj, list):
        # Handle JSON data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(file_obj, f, indent=2)
    else:
        raise TypeError(f"Unsupported file object type: {type(file_obj)}")
    
    return file_path

def get_temp_path(filename):
    """Generate a path in the temporary directory
    
    Args:
        filename: Name of the file
        
    Returns:
        Full path in the temporary directory
    """
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, filename)
""",

    "app/utils/json_manager.py": """import json
from datetime import datetime

def update_json_with_provenance(json_data, changes, user_info, document_path, notes=""):
    """Update JSON data with provenance information
    
    Args:
        json_data: The JSON data to update
        changes: List of changes made
        user_info: User information dictionary
        document_path: Path to the document being reviewed
        notes: Any notes about the changes
        
    Returns:
        Updated JSON data with provenance
    """
    # Ensure the JSON has a _provenance field
    if "_provenance" not in json_data:
        json_data["_provenance"] = []
    
    # Create a provenance entry
    provenance_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_info,
        "document": document_path,
        "changes": changes,
        "notes": notes
    }
    
    # Add the entry to the provenance array
    json_data["_provenance"].append(provenance_entry)
    
    return json_data

def get_changes_summary(json_data):
    """Get a summary of changes made to the JSON data
    
    Args:
        json_data: The JSON data with provenance
        
    Returns:
        A summary of changes
    """
    if "_provenance" not in json_data:
        return []
    
    summary = []
    for entry in json_data["_provenance"]:
        summary.append({
            "timestamp": entry["timestamp"],
            "user": entry["user"].get("name", "Unknown user"),
            "document": entry["document"],
            "num_changes": len(entry["changes"]),
            "changes": entry["changes"]
        })
    
    return summary
""",

    "app/utils/ocr_parser.py": """import json

def parse_textract_blocks(ocr_data):
    """Parse AWS Textract OCR data
    
    Args:
        ocr_data: AWS Textract JSON data
        
    Returns:
        List of parsed text blocks
    """
    if not ocr_data or "Blocks" not in ocr_data:
        return []
    
    blocks = ocr_data["Blocks"]
    
    # Filter to include only LINE and WORD blocks (text content)
    text_blocks = [block for block in blocks if block.get("BlockType") in ["LINE", "WORD"]]
    
    return text_blocks

def get_text_coordinates(ocr_data, text, exact_match=False):
    """Find coordinates for a specific text in OCR data
    
    Args:
        ocr_data: AWS Textract JSON data
        text: Text to search for
        exact_match: Whether to require exact matches
        
    Returns:
        List of bounding boxes for matching text
    """
    blocks = parse_textract_blocks(ocr_data)
    matches = []
    
    for block in blocks:
        if "Text" in block and "Geometry" in block and "BoundingBox" in block["Geometry"]:
            block_text = block["Text"]
            
            if (exact_match and block_text == text) or (not exact_match and text.lower() in block_text.lower()):
                matches.append({
                    "text": block_text,
                    "bbox": block["Geometry"]["BoundingBox"],
                    "page": block.get("Page", 1),
                    "confidence": block.get("Confidence", 100.0)
                })
    
    return matches
""",

    "app/utils/auth_stub.py": """# Placeholder for app/utils/auth_stub.py
# Simplified authentication stub for development purposes

def get_user_identity():
    """
    Returns a default user identity for development/testing.
    In a production environment, this would connect to an authentication service.
    
    Returns:
        dict: A dictionary containing user identity information
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "role": "reviewer"
    }
""",

    # Models
    "app/models/__init__.py": "# Data models",

    "app/models/document.py": """class Document:
    """Document model representing a document being processed"""
    
    def __init__(self, path, document_type=None, metadata=None):
        """Initialize a document
        
        Args:
            path: Path to the document file
            document_type: Type of document (pdf, image, xml)
            metadata: Optional metadata about the document
        """
        self.path = path
        self.document_type = document_type or self._determine_type(path)
        self.metadata = metadata or {}
    
    def _determine_type(self, path):
        """Determine document type from file extension"""
        extension = path.split('.')[-1].lower()
        
        if extension == 'pdf':
            return 'pdf'
        elif extension in ['jpg', 'jpeg', 'png']:
            return 'image'
        elif extension == 'xml':
            return 'xml'
        else:
            return 'unknown'
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            "path": self.path,
            "type": self.document_type,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create document from dictionary"""
        return cls(
            path=data["path"],
            document_type=data.get("type"),
            metadata=data.get("metadata", {})
        )
""",

    "app/models/extraction.py": """import json
from datetime import datetime

class ExtractionValue:
    """Represents a single extracted value"""
    
    def __init__(self, name, value, value_type="string", rules=None):
        """Initialize an extraction value
        
        Args:
            name: Field name
            value: Field value
            value_type: Type of value (string, number, boolean, date, array, object)
            rules: List of validation rules
        """
        self.name = name
        self.value = value
        self.value_type = value_type
        self.rules = rules or []
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.value_type,
            "rules": self.rules
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            name=data["name"],
            value=data["value"],
            value_type=data.get("type", "string"),
            rules=data.get("rules", [])
        )

class Extraction:
    """Represents extracted data with provenance"""
    
    def __init__(self, values=None, provenance=None):
        """Initialize an extraction
        
        Args:
            values: List of ExtractionValue objects
            provenance: List of provenance entries
        """
        self.values = values or []
        self.provenance = provenance or []
    
    def add_value(self, value):
        """Add an extraction value"""
        self.values.append(value)
    
    def add_provenance(self, user, document, changes, notes=""):
        """Add a provenance entry
        
        Args:
            user: User information
            document: Document path
            changes: List of changes
            notes: Optional notes
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "document": document,
            "changes": changes,
            "notes": notes
        }
        self.provenance.append(entry)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "values": [v.to_dict() for v in self.values],
            "_provenance": self.provenance
        }
    
    def to_json(self, indent=2):
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        values = [ExtractionValue.from_dict(v) for v in data.get("values", [])]
        provenance = data.get("_provenance", [])
        return cls(values=values, provenance=provenance)
    
    @classmethod
    def from_json(cls, json_string):
        """Create from JSON string"""
        data = json.loads(json_string)
        return cls.from_dict(data)
""",

    "app/models/audit.py": """from datetime import datetime

class AuditEntry:
    """Represents an audit entry for tracking changes"""
    
    def __init__(self, user, document, action, field=None, old_value=None, new_value=None, notes=None):
        """Initialize an audit entry
        
        Args:
            user: User information
            document: Document path
            action: Action performed (add, modify, delete)
            field: Field name
            old_value: Previous value
            new_value: New value
            notes: Optional notes
        """
        self.timestamp = datetime.now().isoformat()
        self.user = user
        self.document = document
        self.action = action
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
        self.notes = notes
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "user": self.user,
            "document": self.document,
            "action": self.action,
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        entry = cls(
            user=data["user"],
            document=data["document"],
            action=data["action"]
        )
        entry.timestamp = data["timestamp"]
        entry.field = data.get("field")
        entry.old_value = data.get("old_value")
        entry.new_value = data.get("new_value")
        entry.notes = data.get("notes")
        return entry

class AuditTrail:
    """Collection of audit entries"""
    
    def __init__(self, entries=None):
        """Initialize an audit trail
        
        Args:
            entries: List of AuditEntry objects
        """
        self.entries = entries or []
    
    def add_entry(self, entry):
        """Add an audit entry"""
        self.entries.append(entry)
    
    def get_entries_for_document(self, document_path):
        """Get entries for a specific document"""
        return [e for e in self.entries if e.document == document_path]
    
    def get_entries_by_user(self, user_email):
        """Get entries for a specific user"""
        return [e for e in self.entries if e.user.get("email") == user_email]
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "entries": [e.to_dict() for e in self.entries]
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        entries = [AuditEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(entries=entries)
""",

    # Tests
    "tests/__init__.py": "# Test package",

    "tests/test_json_editor.py": """import unittest
import json
import os
import tempfile
import pandas as pd
from app.components.json_editor import JsonEditor

class TestJsonEditor(unittest.TestCase):
    """Tests for the JsonEditor component"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary JSON file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        
        # Sample JSON data
        self.test_data = {
            "values": [
                {
                    "name": "invoice_number",
                    "value": "INV-2023-1234",
                    "type": "string",
                    "rules": ["required", "format:INV-YYYY-####"]
                },
                {
                    "name": "amount",
                    "value": "1250.00",
                    "type": "number",
                    "rules": ["required", "min:0"]
                }
            ],
            "_provenance": []
        }
        
        # Write test data to temp file
        with open(self.temp_file.name, 'w') as f:
            json.dump(self.test_data, f)
        
        # User info for testing
        self.user_info = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        # Create JsonEditor instance
        self.editor = JsonEditor(self.temp_file.name, self.user_info)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_file.name)
    
    def test_load_json(self):
        """Test loading JSON data"""
        # Test that data was loaded correctly
        self.assertEqual(len(self.editor.data["values"]), 2)
        self.assertEqual(self.editor.data["values"][0]["name"], "invoice_number")
        self.assertEqual(self.editor.data["values"][1]["value"], "1250.00")
    
    def test_provenance_structure(self):
        """Test that provenance structure is maintained"""
        self.assertIn("_provenance", self.editor.data)
        self.assertIsInstance(self.editor.data["_provenance"], list)
    
    # Note: The following test would normally be implemented with mocking of Streamlit
    # components, but for this placeholder, we'll just check the structure of methods
    
    def test_render_method_exists(self):
        """Test that the render method exists"""
        self.assertTrue(hasattr(self.editor, 'render'))
        self.assertTrue(callable(getattr(self.editor, 'render')))

if __name__ == '__main__':
    unittest.main()
""",

    # Sample data
    "data/sample_documents/invoice_2023_1234.xml": """<?xml version="1.0" encoding="UTF-8"?>
<invoice>
    <invoice_number>INV-2023-1234</invoice_number>
    <date>2023-09-15</date>
    <due_date>2023-10-15</due_date>
    <customer>
        <name>Acme Corporation</name>
        <id>ACME001</id>
    </customer>
    <items>
        <item>
            <description>Product A</description>
            <quantity>2</quantity>
            <unit_price>250.00</unit_price>
            <total>500.00</total>
        </item>
        <item>
            <description>Product B</description>
            <quantity>3</quantity>
            <unit_price>250.00</unit_price>
            <total>750.00</total>
        </item>
    </items>
    <subtotal>1250.00</subtotal>
    <tax_rate>8.5</tax_rate>
    <tax_amount>106.25</tax_amount>
    <total_amount>1356.25</total_amount>
    <payment_terms>Net 30</payment_terms>
    <currency>USD</currency>
</invoice>
""",

    "data/sample_extractions/invoice_extraction.json": """{
  "values": [
    {
      "name": "invoice_number",
      "value": "INV-2023-1234",
      "type": "string",
      "rules": ["required", "format:INV-YYYY-####"]
    },
    {
      "name": "date",
      "value": "2023-09-15",
      "type": "date",
      "rules": ["required"]
    },
    {
      "name": "due_date",
      "value": "2023-10-15",
      "type": "date",
      "rules": ["required", "after:date"]
    },
    {
      "name": "customer_name",
      "value": "Acme Corporation",
      "type": "string",
      "rules": ["required"]
    },
    {
      "name": "customer_id",
      "value": "ACME001",
      "type": "string",
      "rules": ["required"]
    },
    {
      "name": "subtotal",
      "value": "1250.00",
      "type": "number",
      "rules": ["required", "min:0"]
    },
    {
      "name": "tax_rate",
      "value": "8.5",
      "type": "number",
      "rules": ["required", "min:0", "max:100"]
    },
    {
      "name": "tax_amount",
      "value": "106.25",
      "type": "number",
      "rules": ["required", "min:0"]
    },
    {
      "name": "total_amount",
      "value": "1356.25",
      "type": "number",
      "rules": ["required", "min:0"]
    },
    {
      "name": "payment_terms",
      "value": "Net 30",
      "type": "string",
      "rules": []
    },
    {
      "name": "currency",
      "value": "USD",
      "type": "string",
      "rules": ["required", "in:USD,EUR,GBP"]
    }
  ],
  "_provenance": []
}
""",

    "data/sample_ocr/invoice_2023_1234_ocr.json": """{
  "Blocks": [
    {
      "BlockType": "PAGE",
      "Page": 1,
      "Geometry": {
        "BoundingBox": {
          "Width": 1.0,
          "Height": 1.0,
          "Left": 0.0,
          "Top": 0.0
        }
      }
    },
    {
      "BlockType": "LINE",
      "Text": "INV-2023-1234",
      "Page": 1,
      "Confidence": 99.5,
      "Geometry": {
        "BoundingBox": {
          "Width": 0.2,
          "Height": 0.03,
          "Left": 0.7,
          "Top": 0.1
        }
      }
    },
    {
      "BlockType": "LINE",
      "Text": "Acme Corporation",
      "Page": 1,
      "Confidence": 98.7,
      "Geometry": {
        "BoundingBox": {
          "Width": 0.3,
          "Height": 0.03,
          "Left": 0.1,
          "Top": 0.2
        }
      }
    },
    {
      "BlockType": "LINE",
      "Text": "Total Amount: $1356.25",
      "Page": 1,
      "Confidence": 97.8,
      "Geometry": {
        "BoundingBox": {
          "Width": 0.25,
          "Height": 0.03,
          "Left": 0.6,
          "Top": 0.7
        }
      }
    }
  ]
}
""",

    "data/guidelines/invoice_review_guidelines.md": """# Invoice Review Guidelines

## Purpose
This document provides guidelines for reviewing and validating toy invoice data extractions.

## General Guidelines
1. All invoices must have a valid invoice number, date, and amount
2. The customer information must match our records
3. The total amount should be the sum of subtotal and taxes
4. Verify that the currency is supported

## Field-Specific Guidelines

### Invoice Number
* Must follow the format INV-YYYY-#### where YYYY is the year and #### is a sequence number
* Should be unique in our system

### Dates
* Invoice date should be in the past
* Due date should be after the invoice date
* Format should be YYYY-MM-DD

### Amounts
* All monetary values should have 2 decimal places
* Subtotal plus tax should equal the total amount (allow for rounding differences up to 0.02)
* Negative amounts should be flagged for review

### Customer Information
* Customer name should match our records
* Customer ID should be valid in our system

## OCR Validation
When reviewing OCR data:
1. Check text in bounding boxes against extracted values
2. Pay special attention to numbers and dates, which are prone to OCR errors
3. Flag any extractions with confidence below 90% for manual review

## Special Cases
* For invoices with multiple currencies, convert all to a single currency
* For invoices with multiple tax rates, verify each line item
* For credit notes, verify that amounts are properly marked as negative
"""
}

# Function to create the project structure
def create_project_structure():
    """Create the project structure and files"""
    root_dir = PROJECT_ROOT
    print(f"Creating project structure in {root_dir}")
    
    # Create root directory
    if os.path.exists(root_dir):
        choice = input(f"Directory {root_dir} already exists. Overwrite? (y/n): ")
        if choice.lower() != 'y':
            print("Installation cancelled.")
            return False
        
        # Remove the existing directory
        shutil.rmtree(root_dir)
    
    # Create directories
    directories = [
        "",  # Root directory
        "app",
        "app/components",
        "app/utils",
        "app/models",
        "data",
        "data/sample_documents",
        "data/sample_extractions",
        "data/sample_ocr",
        "data/guidelines",
        "tests",
        "temp",  # For temporary files
        ".streamlit"  # Streamlit config folder
    ]
    
    for directory in directories:
        dir_path = os.path.join(root_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create files
    for file_path, content in FILES.items():
        full_path = os.path.join(root_dir, file_path)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created file: {full_path}")
    
    return True

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(description="Install Document Processing Assistant")
    args = parser.parse_args()
    
    # Create project structure and files
    if create_project_structure():
        print("\nInstallation completed successfully!")
        print("\nNext steps:")
        print(f"1. Install requirements: pip install -r {PROJECT_ROOT}/requirements.txt")
        print(f"2. Run the application: cd {PROJECT_ROOT} && streamlit run app/main.py")
    else:
        print("Installation failed.")

if __name__ == "__main__":
    main()