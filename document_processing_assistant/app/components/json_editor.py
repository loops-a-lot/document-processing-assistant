import streamlit as st
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