import os
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