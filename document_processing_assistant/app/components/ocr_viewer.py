import streamlit as st
import json
import numpy as np
import os
from PIL import Image, ImageDraw
import fitz  # PyMuPDF for PDF handling
import tempfile
import base64

class OcrViewer:
    """Component for visualizing OCR data with bounding boxes"""
    
    def __init__(self, document_path, ocr_path):
        """Initialize the OCR viewer
        
        Args:
            document_path: Path to the document file
            ocr_path: Path to the OCR data file (Textract JSON format)
        """
        self.document_path = document_path
        self.ocr_path = ocr_path
        self.ocr_data = self._load_ocr_data()
        self.file_extension = os.path.splitext(document_path)[1].lower()
    
    def _load_ocr_data(self):
        """Load OCR data from JSON file"""
        if not os.path.exists(self.ocr_path):
            return None
        
        try:
            with open(self.ocr_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading OCR data: {e}")
            return None
    
    def render(self):
        """Render the OCR visualization in the Streamlit UI"""
        if not self.ocr_data:
            st.warning("No OCR data available to visualize")
            return
        
        # Get document pages
        if self.file_extension == ".pdf":
            try:
                pdf_document = fitz.open(self.document_path)
                num_pages = len(pdf_document)
                
                # Page selector
                page_num = st.slider("Select Page", 1, num_pages, 1, key="ocr_page_slider") - 1
                
                # Extract page as image
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                
                # Save to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                    pix.save(temp_file.name)
                    img_path = temp_file.name
                
                # Visualize OCR on this page
                self._visualize_ocr_on_image(img_path, page_num)
                
                # Clean up
                os.unlink(img_path)
                pdf_document.close()
                
            except Exception as e:
                st.error(f"Error rendering PDF with OCR: {e}")
        
        elif self.file_extension in [".jpg", ".jpeg", ".png"]:
            # For images, assume it's a single page (page 0)
            self._visualize_ocr_on_image(self.document_path, 0)
        
        else:
            st.error(f"OCR visualization not supported for file type: {self.file_extension}")
    
    def _visualize_ocr_on_image(self, img_path, page_num):
        """Draw OCR bounding boxes on an image
        
        Args:
            img_path: Path to the image
            page_num: Page number (0-based) to visualize
        """
        try:
            # Load image
            image = Image.open(img_path)
            img_width, img_height = image.size
            
            # Create a drawing context
            draw = ImageDraw.Draw(image)
            
            # Extract bounding boxes for the page
            blocks = self._extract_blocks_for_page(page_num)
            
            if not blocks:
                st.warning(f"No OCR data found for page {page_num + 1}")
                st.image(image, use_column_width=True)
                return
            
            # Random colors for different blocks
            colors = [
                (255, 0, 0, 128),    # Red
                (0, 255, 0, 128),    # Green
                (0, 0, 255, 128),    # Blue
                (255, 255, 0, 128),  # Yellow
                (255, 0, 255, 128),  # Magenta
                (0, 255, 255, 128),  # Cyan
                (255, 128, 0, 128),  # Orange
                (128, 0, 255, 128),  # Purple
            ]
            
            # Draw bounding boxes
            for i, block in enumerate(blocks):
                color = colors[i % len(colors)]
                
                # Get coordinates (normalized to image dimensions)
                left = block["Geometry"]["BoundingBox"]["Left"] * img_width
                top = block["Geometry"]["BoundingBox"]["Top"] * img_height
                width = block["Geometry"]["BoundingBox"]["Width"] * img_width
                height = block["Geometry"]["BoundingBox"]["Height"] * img_height
                
                # Calculate rectangle coordinates
                rect = [(left, top), (left + width, top + height)]
                
                # Draw rectangle
                draw.rectangle(rect, outline=color, width=2)
                
                # Draw text label (if it's a word or line)
                if "Text" in block:
                    text = block["Text"]
                    confidence = block.get("Confidence", 0)
                    label = f"{text} ({confidence:.1f}%)"
                    draw.text((left, top - 10), label, fill=color[:3])
            
            # Display image with bounding boxes
            st.image(image, use_column_width=True)
            
            # Show text content in an expandable section
            with st.expander("View Extracted Text"):
                for block in blocks:
                    if "Text" in block:
                        confidence = block.get("Confidence", 0)
                        st.write(f"**{block.get('Text', '')}** (Confidence: {confidence:.1f}%)")
            
        except Exception as e:
            st.error(f"Error visualizing OCR data: {e}")
            
    def _extract_blocks_for_page(self, page_num):
        """Extract text blocks for a specific page from Textract JSON
        
        Args:
            page_num: Page number (0-based)
            
        Returns:
            List of text block objects with geometry and text
        """
        # Handle different Textract JSON formats
        if "Blocks" in self.ocr_data:
            # Standard Textract format
            blocks = []
            for block in self.ocr_data["Blocks"]:
                # Check if block belongs to the current page
                if block.get("Page", 1) - 1 == page_num:
                    if block["BlockType"] in ["WORD", "LINE"]:
                        blocks.append(block)
            return blocks
            
        elif "Pages" in self.ocr_data and len(self.ocr_data["Pages"]) > page_num:
            # Alternative format with pages array
            page_data = self.ocr_data["Pages"][page_num]
            if "Blocks" in page_data:
                return [b for b in page_data["Blocks"] if b["BlockType"] in ["WORD", "LINE"]]
        
        # If we have a simple array of blocks without page info, assume it's for page 0
        elif isinstance(self.ocr_data, list) and page_num == 0:
            return [b for b in self.ocr_data if b.get("BlockType") in ["WORD", "LINE"]]
            
        return []