"""
Exceptions used by the library.
"""

class HandshakeError(Exception):
    """
    Raised when handshake with the device fails.
    """
    pass


class ConnectionError(Exception):
    """
    Raised when connection to the device fails.
    """
    pass


class DeviceNotFound(Exception):
    """
    Raised when device with specified short ID is not found.
    """
    pass


class DeviceError(Exception):
    """
    Raised when connected device returns an error.

    Attributes:
        error_code: The error code returned by the device.
    """
    
    def __init__(self, error_code: int):
        self.error_code: int = error_code
        super().__init__(f"Device error: {error_code}")
