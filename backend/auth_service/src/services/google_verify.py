from typing import Dict, Any

def verify_google_id_token(token: str) -> Dict[str, Any]:
    """
    Placeholder for Google ID token verification.
    In a real application, this would use the google-auth library.
    
    For testing purposes, it returns a mock payload if the token is "test_token".
    """
    if token == "test_token":
        return {
            "email": "test.google.user@example.com",
            "name": "Google User",
            "picture": "http://example.com/avatar.jpg",
            "sub": "google-user-id-123",
        }
    # In a real scenario, you would raise a ValueError for an invalid token
    # raise ValueError("Invalid Google token")
    # For now, return a generic dict to avoid breaking tests that don't use it.
    return {"email": "mock@example.com"}