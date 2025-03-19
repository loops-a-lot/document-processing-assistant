import json
from datetime import datetime

def update_json_with_provenance(json_data, changes, user_info, document_path, notes=""):
    """Updates JSON data with changes and adds provenance information
    
    Args:
        json_data: The original JSON data
        changes: List of changes made (field, old_value, new_value, action)
        user_info: Dictionary with user information (name, email)
        document_path: Path to the document being reviewed
        notes: Optional notes about the changes
        
    Returns:
        Updated JSON data with provenance information
    """
    # Make a copy of the original data
    updated_data = json_data.copy()
    
    # Ensure provenance section exists
    if "_provenance" not in updated_data:
        updated_data["_provenance"] = []
    
    # Create provenance entry
    provenance_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_info,
        "document": document_path,
        "changes": changes,
        "notes": notes
    }
    
    # Add to provenance history
    updated_data["_provenance"].append(provenance_entry)
    
    return updated_data

def get_field_history(json_data, field_name):
    """Extracts the change history for a specific field
    
    Args:
        json_data: The JSON data with provenance
        field_name: Name of the field to get history for
        
    Returns:
        List of changes for the specified field
    """
    if "_provenance" not in json_data:
        return []
    
    field_history = []
    
    for entry in json_data["_provenance"]:
        for change in entry["changes"]:
            if change["field"] == field_name:
                field_history.append({
                    "timestamp": entry["timestamp"],
                    "user": entry["user"],
                    "old_value": change["old_value"],
                    "new_value": change["new_value"],
                    "action": change["action"],
                    "notes": entry.get("notes", "")
                })
    
    return field_history

def export_provenance_report(json_data, output_path):
    """Exports a provenance report as a separate file
    
    Args:
        json_data: The JSON data with provenance
        output_path: Path to save the report
        
    Returns:
        Boolean indicating success
    """
    if "_provenance" not in json_data:
        return False
    
    try:
        # Organize by timestamp
        provenance = sorted(
            json_data["_provenance"],
            key=lambda x: x["timestamp"]
        )
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(provenance, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error exporting provenance report: {e}")
        return False