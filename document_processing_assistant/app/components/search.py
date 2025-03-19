import streamlit as st
import re
import json
import fitz  # PyMuPDF
import os
from PIL import Image, ImageDraw
import numpy as np
import tempfile
import base64

class DocumentSearch:
    """Component for searching documents with semantic capabilities"""
    
    def __init__(self, document_path, ocr_path=None):
        """Initialize the document search component
        
        Args:
            document_path: Path to the document file
            ocr_path: Optional path to OCR data for more accurate search
        """
        self.document_path = document_path
        self.ocr_path = ocr_path
        self.file_extension = os.path.splitext(document_path)[1].lower()
        self.ocr_data = self._load_ocr_data() if ocr_path else None
    
    def _load_ocr_data(self):
        """Load OCR data if available"""
        if not os.path.exists(self.ocr_path):
            return None
        
        try:
            with open(self.ocr_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading OCR data for search: {e}")
            return None
    
    def render(self):
        """Render the search interface in the Streamlit UI"""
        st.subheader("Search Document")
        search_query = st.text_input("Enter search term:", key="document_search_input")
        
        search_type = st.radio(
            "Search Type:",
            ["Exact Match", "Fuzzy Match", "Semantic Search (stub)"],
            horizontal=True,
            key="search_type"
        )
        
        if search_query:
            if self.file_extension == ".pdf":
                self._search_pdf(search_query, search_type)
            elif self.file_extension in [".jpg", ".jpeg", ".png"]:
                self._search_image(search_query, search_type)
            elif self.file_extension == ".xml":
                self._search_xml(search_query, search_type)
            else:
                st.error(f"Search not supported for file type: {self.file_extension}")
    
    def _search_pdf(self, query, search_type):
        """Search within a PDF document
        
        Args:
            query: Search query string
            search_type: Type of search to perform
        """
        try:
            # Open PDF document
            pdf_document = fitz.open(self.document_path)
            results = []
            
            # Search based on type
            if search_type == "Exact Match":
                # Use PyMuPDF's search function
                for page_num, page in enumerate(pdf_document):
                    matches = page.search_for(query)
                    if matches:
                        # Extract some context around each match
                        for match in matches:
                            # Get words near the match for context
                            words = page.get_text("words")
                            context = " ".join([w[4] for w in words if self._is_near_rect(w[:4], match)])
                            
                            results.append({
                                "page": page_num + 1,
                                "rect": match,
                                "context": context
                            })
            
            elif search_type == "Fuzzy Match":
                # Simple fuzzy search implementation
                pattern = "".join([f"{c}.*?" for c in query])
                for page_num, page in enumerate(pdf_document):
                    text = page.get_text()
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        # Get some context around the match
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end]
                        
                        # Find the location of the match on the page
                        # (this is approximate since we don't have exact coordinates)
                        words = page.get_text("words")
                        match_rect = None
                        
                        for word in words:
                            if word[4].lower() in context.lower():
                                match_rect = word[:4]
                                break
                        
                        results.append({
                            "page": page_num + 1,
                            "rect": match_rect,
                            "context": context
                        })
            
            elif search_type == "Semantic Search (stub)":
                st.info("Semantic search would use embeddings to find related content.")
                # Stub implementation - just do a case-insensitive search
                for page_num, page in enumerate(pdf_document):
                    text = page.get_text().lower()
                    if query.lower() in text:
                        # Find position of match in text
                        idx = text.find(query.lower())
                        start = max(0, idx - 50)
                        end = min(len(text), idx + len(query) + 50)
                        context = text[start:end]
                        
                        results.append({
                            "page": page_num + 1,
                            "rect": None,  # We don't have exact coordinates
                            "context": context
                        })
            
            # Display results
            if results:
                st.success(f"Found {len(results)} matches")
                
                # Group by page
                page_results = {}
                for result in results:
                    page = result["page"]
                    if page not in page_results:
                        page_results[page] = []
                    page_results[page].append(result)
                
                # Display each page with highlights
                for page, page_matches in page_results.items():
                    with st.expander(f"Page {page} - {len(page_matches)} matches"):
                        # Extract page as image
                        pdf_page = pdf_document[page - 1]
                        pix = pdf_page.get_pixmap()
                        
                        # Save to a temporary file
                        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                            pix.save(temp_file.name)
                            img_path = temp_file.name
                        
                        # Draw highlights on the image
                        image = Image.open(img_path)
                        draw = ImageDraw.Draw(image)
                        
                        # Highlight each match
                        for match in page_matches:
                            if match["rect"]:
                                # Draw a highlight rectangle
                                rect = match["rect"]
                                draw.rectangle(
                                    [(rect[0], rect[1]), (rect[2], rect[3])],
                                    outline=(255, 0, 0),
                                    width=2
                                )
                        
                        # Show the context text
                        for i, match in enumerate(page_matches):
                            st.write(f"{i+1}. {match['context']}")
                        
                        # Display the image with highlights
                        st.image(image, use_column_width=True)
                        
                        # Clean up
                        os.unlink(img_path)
            else:
                st.info(f"No matches found for '{query}'")
            
            # Clean up
            pdf_document.close()
            
        except Exception as e:
            st.error(f"Error searching PDF: {e}")
    
    def _search_image(self, query, search_type):
        """Search within an image using OCR data
        
        Args:
            query: Search query string
            search_type: Type of search to perform
        """
        if not self.ocr_data:
            st.warning("OCR data is required to search images. Please upload OCR data.")
            return
        
        try:
            # Load the image
            image = Image.open(self.document_path)
            img_width, img_height = image.size
            draw = ImageDraw.Draw(image)
            
            results = []
            
            # Extract text blocks
            blocks = []
            if "Blocks" in self.ocr_data:
                blocks = [b for b in self.ocr_data["Blocks"] 
                         if b["BlockType"] in ["WORD", "LINE"] and "Text" in b]
            elif isinstance(self.ocr_data, list):
                blocks = [b for b in self.ocr_data 
                         if b.get("BlockType") in ["WORD", "LINE"] and "Text" in b]
            
            # Search based on type
            if search_type == "Exact Match":
                # Case-insensitive exact match
                for block in blocks:
                    if query.lower() in block["Text"].lower():
                        results.append(block)
            
            elif search_type == "Fuzzy Match":
                # Simple fuzzy match
                pattern = "".join([f"{c}.*?" for c in query])
                for block in blocks:
                    if re.search(pattern, block["Text"], re.IGNORECASE):
                        results.append(block)
            
            elif search_type == "Semantic Search (stub)":
                st.info("Semantic search would use embeddings to find related content.")
                # Stub implementation - just case-insensitive contains
                for block in blocks:
                    if query.lower() in block["Text"].lower():
                        results.append(block)
            
            # Display results
            if results:
                st.success(f"Found {len(results)} matches")
                
                # Draw bounding boxes on matches
                for block in results:
                    # Get coordinates (normalized to image dimensions)
                    left = block["Geometry"]["BoundingBox"]["Left"] * img_width
                    top = block["Geometry"]["BoundingBox"]["Top"] * img_height
                    width = block["Geometry"]["BoundingBox"]["Width"] * img_width
                    height = block["Geometry"]["BoundingBox"]["Height"] * img_height
                    
                    # Calculate rectangle coordinates
                    rect = [(left, top), (left + width, top + height)]
                    
                    # Draw rectangle
                    draw.rectangle(rect, outline=(255, 0, 0), width=2)
                
                # Display image with highlights
                st.image(image, use_column_width=True)
                
                # Show the matched text
                st.subheader("Matched Text:")
                for i, match in enumerate(results):
                    st.write(f"{i+1}. {match['Text']}")
            else:
                st.info(f"No matches found for '{query}'")
                
        except Exception as e:
            st.error(f"Error searching image: {e}")
    
    def _search_xml(self, query, search_type):
        """Search within an XML document
        
        Args:
            query: Search query string
            search_type: Type of search to perform
        """
        try:
            with open(self.document_path, 'r') as f:
                xml_content = f.read()
            
            results = []
            
            # Search based on type
            if search_type == "Exact Match":
                # Find all matches
                for i, line in enumerate(xml_content.split('\n')):
                    if query in line:
                        results.append({"line": i + 1, "content": line.strip()})
            
            elif search_type == "Fuzzy Match":
                # Simple fuzzy search
                pattern = "".join([f"{c}.*?" for c in query])
                for i, line in enumerate(xml_content.split('\n')):
                    if re.search(pattern, line, re.IGNORECASE):
                        results.append({"line": i + 1, "content": line.strip()})
            
            elif search_type == "Semantic Search (stub)":
                st.info("Semantic search would use embeddings to find related content.")
                # Stub implementation
                for i, line in enumerate(xml_content.split('\n')):
                    if query.lower() in line.lower():
                        results.append({"line": i + 1, "content": line.strip()})
            
            # Display results
            if results:
                st.success(f"Found {len(results)} matches")
                
                # Display results in a table
                results_df = [{"Line": r["line"], "Content": r["content"]} for r in results]
                st.table(results_df)
                
                # Create a version of the XML with highlights
                highlighted_lines = xml_content.split('\n')
                for result in results:
                    line_num = result["line"] - 1
                    if 0 <= line_num < len(highlighted_lines):
                        highlighted_lines[line_num] = highlighted_lines[line_num].replace(
                            query, f"**{query}**")
                
                with st.expander("View XML with Highlights"):
                    st.code("\n".join(highlighted_lines), language="xml")
            else:
                st.info(f"No matches found for '{query}'")
                
        except Exception as e:
            st.error(f"Error searching XML: {e}")
    
    def _is_near_rect(self, word_rect, match_rect, threshold=20):
        """Check if a word rectangle is near a match rectangle
        
        Args:
            word_rect: Rectangle of a word (x0, y0, x1, y1)
            match_rect: Rectangle of a match (x0, y0, x1, y1)
            threshold: Distance threshold in points
            
        Returns:
            True if the rectangles are near each other
        """
        # Calculate centers
        word_center_x = (word_rect[0] + word_rect[2]) / 2
        word_center_y = (word_rect[1] + word_rect[3]) / 2
        match_center_x = (match_rect[0] + match_rect[2]) / 2
        match_center_y = (match_rect[1] + match_rect[3]) / 2
        
        # Calculate distance
        distance = np.sqrt(
            (word_center_x - match_center_x) ** 2 + 
            (word_center_y - match_center_y) ** 2
        )
        
        return distance < threshold