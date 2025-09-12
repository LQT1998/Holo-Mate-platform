class HoloMateError(Exception):
    """Base exception for the application."""
    pass

class NotFoundError(HoloMateError):
    """Raised when an item is not found."""
    pass

class ConflictError(HoloMateError):
    """Raised when a conflict occurs, e.g., duplicate item."""
    pass

class UnauthorizedError(HoloMateError):
    """Raised on authentication or authorization failure."""
    pass
