import os
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