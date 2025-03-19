import os
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