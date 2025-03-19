import pytest
import os
import json
import tempfile
from app.components.json_editor import JsonEditor

class TestJsonEditor:
    """Unit tests for the JSON editor component"""
    
    @pytest.fixture
    def sample_json_path(self):
        """Create a temporary JSON file for testing"""
        sample_data = {
            "values": [
                {
                    "name": "test_field",
                    "value": "test_value",
                    "type": "string",
                    "rules": ["required"]
                }
            ],
            "_provenance": []
        }
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            json.dump(sample_data, temp_file)
            temp_file_path = temp_file.name
        
        yield temp_file_path
        
        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    @pytest.fixture
    def user_info(self):
        """Sample user info for testing"""
        return {
            "name": "Test User",
            "email": "test@example.com"
        }
    
    def test_load_json(self, sample_json_path, user_info):
        """Test loading JSON data"""
        editor = JsonEditor(sample_json_path, user_info)
        assert "values" in editor.data
        assert "_provenance" in editor.data
        assert len(editor.data["values"]) == 1
        assert editor.data["values"][0]["name"] == "test_field"
    
    def test_invalid_json_path(self, user_info):
        """Test handling of invalid JSON path"""
        editor = JsonEditor("nonexistent_file.json", user_info)
        assert editor.data == {"values": [], "_provenance": []}