class APIError(Exception):
    """Generic class for API errors"""

class GeocodeAPIError(APIError):
    """Generic class for geocoding API errors"""

class UnknownBackendError(Exception):
    """Unknown backend error"""
