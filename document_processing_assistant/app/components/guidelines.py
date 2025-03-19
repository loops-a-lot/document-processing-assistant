import streamlit as st
import markdown
import os

class GuidelinesViewer:
    """Component for displaying guidelines in markdown format"""
    
    def __init__(self, guidelines_path):
        """Initialize the guidelines viewer
        
        Args:
            guidelines_path: Path to the guidelines file (markdown or text)
        """
        self.guidelines_path = guidelines_path
    
    def render(self):
        """Render the guidelines in the Streamlit UI"""
        if not os.path.exists(self.guidelines_path):
            st.error(f"Guidelines file not found: {self.guidelines_path}")
            return
        
        try:
            with open(self.guidelines_path, 'r') as f:
                guidelines_content = f.read()
            
            file_extension = os.path.splitext(self.guidelines_path)[1].lower()
            
            # For markdown files, render as HTML
            if file_extension == ".md":
                # Convert markdown to HTML
                html_content = markdown.markdown(guidelines_content)
                # Display in a scrollable container
                st.markdown(
                    f"""
                    <div style="height: 400px; overflow-y: scroll; padding: 10px; 
                             border: 1px solid #ccc; border-radius: 5px;">
                        {html_content}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            # For text files, display as plain text
            else:
                st.text_area("Guidelines", guidelines_content, height=400, disabled=True)
                
            # Add download button
            st.download_button(
                label="Download Guidelines",
                data=guidelines_content,
                file_name=os.path.basename(self.guidelines_path),
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Error rendering guidelines: {e}")