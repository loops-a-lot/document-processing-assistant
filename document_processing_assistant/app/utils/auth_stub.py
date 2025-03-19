# Placeholder for app/utils/auth_stub.py
# Simplified authentication stub for development purposes

def get_user_identity():
    """
    Returns a default user identity for development/testing.
    In a production environment, this would connect to an authentication service.
    
    Returns:
        dict: A dictionary containing user identity information
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "role": "reviewer"
    }
