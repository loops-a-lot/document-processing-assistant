import streamlit as st
import os

class DocumentChat:
    """Component for chatting with the document"""
    
    def __init__(self, document_path, json_path=None, ocr_path=None, chat_history=None):
        """Initialize the document chat component
        
        Args:
            document_path: Path to the document file
            json_path: Optional path to the JSON extraction data
            ocr_path: Optional path to the OCR data
            chat_history: List of previous chat messages
        """
        self.document_path = document_path
        self.json_path = json_path
        self.ocr_path = ocr_path
        self.chat_history = chat_history or []
    
    def render(self):
        """Render the chat interface in the Streamlit UI
        
        Returns:
            Updated chat history
        """
        # Chat container
        st.markdown(
            """
            <style>
            .chat-container {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
                max-height: 300px;
                overflow-y: auto;
            }
            .user-message {
                background-color: #E8F0FE;
                padding: 8px;
                border-radius: 15px;
                margin: 5px 0;
                text-align: right;
            }
            .assistant-message {
                background-color: #F0F0F0;
                padding: 8px;
                border-radius: 15px;
                margin: 5px 0;
                text-align: left;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in self.chat_history:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    st.markdown(f'<div class="user-message">👤 {content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="assistant-message">🤖 {content}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask about the document:", key="chat_input")
            submit_button = st.form_submit_button("Send")
            
            if submit_button and user_input:
                # Add user message to history
                self.chat_history.append({"role": "user", "content": user_input})
                
                # Process message and generate response (stub)
                response = self._generate_response(user_input)
                
                # Add assistant message to history
                self.chat_history.append({"role": "assistant", "content": response})
        
        # Clear chat button
        if st.button("Clear Chat History"):
            self.chat_history = []
            st.experimental_rerun()
        
        return self.chat_history
    
    def _generate_response(self, user_input):
        """Generate a response to the user's input (stub implementation)
        
        Args:
            user_input: User's chat message
            
        Returns:
            Generated response
        """
        # This is a stub implementation - in a real system, this would call an LLM API
        # with the document content and chat history for context
        
        document_name = os.path.basename(self.document_path)
        
        if "hello" in user_input.lower() or "hi" in user_input.lower():
            return f"Hello! I'm here to help you with document '{document_name}'. What would you like to know?"
        
        elif "what" in user_input.lower() and "document" in user_input.lower():
            return f"This is document '{document_name}'. I can help you understand its contents or answer questions about it."
        
        elif "search" in user_input.lower() or "find" in user_input.lower():
            return "You can use the search tool above to find specific information in the document."
        
        elif "json" in user_input.lower() or "data" in user_input.lower():
            return "The extracted JSON data is displayed in the editor panel. You can modify values there if needed."
        
        elif "ocr" in user_input.lower():
            if self.ocr_path:
                return "OCR data is available for this document. You can see the text extraction with bounding boxes in the OCR visualization panel."
            else:
                return "No OCR data has been provided for this document."
        
        elif "help" in user_input.lower():
            return "I can help you understand the document, find information, or explain the extracted data. You can also use the search tool to locate specific content."
        
        else:
            return "I'm just a stub implementation for now. In a full version, I would analyze the document and provide a helpful response to your query."