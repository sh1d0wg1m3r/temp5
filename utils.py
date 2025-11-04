"""
Utility Functions for Secure P2P Chat
Input validation, formatting, and helper functions
"""

import re
import ipaddress
from typing import Tuple, Optional


class Validator:
    """Input validation utilities"""

    @staticmethod
    def validate_passphrase(passphrase: str, min_length: int = 8) -> Tuple[bool, str]:
        """
        Validate passphrase strength
        Returns: (is_valid, error_message)
        """
        if not passphrase:
            return False, "Passphrase cannot be empty"

        if len(passphrase) < min_length:
            return False, f"Passphrase must be at least {min_length} characters"

        # Check for basic strength
        has_upper = any(c.isupper() for c in passphrase)
        has_lower = any(c.islower() for c in passphrase)
        has_digit = any(c.isdigit() for c in passphrase)

        if len(passphrase) < 12 and not (has_upper and has_lower and has_digit):
            return True, "Warning: For better security, use uppercase, lowercase, and numbers"

        return True, ""

    @staticmethod
    def validate_ip_address(ip: str) -> Tuple[bool, str]:
        """
        Validate IP address format
        Returns: (is_valid, error_message)
        """
        if not ip:
            return False, "IP address cannot be empty"

        try:
            # Try to parse as IP address
            ipaddress.ip_address(ip)
            return True, ""
        except ValueError:
            # Maybe it's a hostname
            if re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', ip):
                return True, ""
            return False, "Invalid IP address or hostname format"

    @staticmethod
    def validate_port(port: int) -> Tuple[bool, str]:
        """
        Validate port number
        Returns: (is_valid, error_message)
        """
        if not isinstance(port, int):
            return False, "Port must be a number"

        if port < 1:
            return False, "Port must be greater than 0"

        if port > 65535:
            return False, "Port must be less than 65536"

        if port < 1024:
            return True, "Warning: Using privileged port (< 1024) may require root access"

        return True, ""

    @staticmethod
    def validate_address(address: str) -> Tuple[bool, str, Optional[str], Optional[int]]:
        """
        Validate peer address (IP:PORT format)
        Returns: (is_valid, error_message, host, port)
        """
        if not address:
            return False, "Address cannot be empty", None, None

        if ':' not in address:
            return False, "Address must be in format IP:PORT (e.g., 192.168.1.100:8765)", None, None

        parts = address.split(':')
        if len(parts) != 2:
            return False, "Address must contain exactly one colon", None, None

        host, port_str = parts
        host = host.strip()
        port_str = port_str.strip()

        # Validate IP
        ip_valid, ip_error = Validator.validate_ip_address(host)
        if not ip_valid:
            return False, ip_error, None, None

        # Validate port
        try:
            port = int(port_str)
        except ValueError:
            return False, f"Invalid port number: '{port_str}'", None, None

        port_valid, port_error = Validator.validate_port(port)
        if not port_valid:
            return False, port_error, None, None

        return True, "", host, port

    @staticmethod
    def validate_message(message: str, max_length: int = 10000) -> Tuple[bool, str]:
        """
        Validate chat message
        Returns: (is_valid, error_message)
        """
        if not message:
            return False, "Message cannot be empty"

        if len(message) > max_length:
            return False, f"Message too long (max {max_length} characters)"

        return True, ""

    @staticmethod
    def validate_nickname(nickname: str) -> Tuple[bool, str]:
        """
        Validate user nickname
        Returns: (is_valid, error_message)
        """
        if not nickname:
            return False, "Nickname cannot be empty"

        if len(nickname) < 2:
            return False, "Nickname must be at least 2 characters"

        if len(nickname) > 32:
            return False, "Nickname must be less than 32 characters"

        # Allow alphanumeric, spaces, and some special characters
        if not re.match(r'^[a-zA-Z0-9 _-]+$', nickname):
            return False, "Nickname can only contain letters, numbers, spaces, hyphens, and underscores"

        return True, ""


class Formatter:
    """Output formatting utilities"""

    @staticmethod
    def format_bytes(bytes_count: int) -> str:
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.0f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"

    @staticmethod
    def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def format_fingerprint(words: list, words_per_line: int = 4) -> str:
        """Format word list as multi-line fingerprint"""
        lines = []
        for i in range(0, len(words), words_per_line):
            line_words = words[i:i+words_per_line]
            lines.append(" - ".join(w.upper() for w in line_words))
        return "\n".join(lines)


class ErrorMessages:
    """Centralized error messages"""

    # Connection errors
    CONNECTION_REFUSED = "Connection refused. Make sure the peer is online and the address is correct."
    CONNECTION_TIMEOUT = "Connection timeout. The peer may be offline or unreachable."
    CONNECTION_FAILED = "Failed to connect to peer. Check your network connection."
    ALREADY_CONNECTED = "Already connected to this peer."
    CANNOT_CONNECT_SELF = "Cannot connect to yourself."

    # Encryption errors
    ENCRYPTION_FAILED = "Failed to encrypt message. Please try again."
    DECRYPTION_FAILED = "Failed to decrypt message. The message may be corrupted or from an unknown sender."
    INVALID_KEY = "Invalid encryption key format."
    KEY_LOAD_FAILED = "Failed to load encryption keys. Check your passphrase."

    # Validation errors
    INVALID_ADDRESS = "Invalid address format. Use IP:PORT (e.g., 192.168.1.100:8765)"
    INVALID_PORT = "Invalid port number. Must be between 1 and 65535."
    INVALID_MESSAGE = "Invalid message. Message cannot be empty."
    PASSPHRASE_TOO_SHORT = "Passphrase must be at least 8 characters long."

    # Storage errors
    STORAGE_FAILED = "Failed to save data. Check disk space and permissions."
    STORAGE_LOAD_FAILED = "Failed to load data from storage."

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "Message rate limit exceeded. Please slow down."

    @staticmethod
    def format_error(error_type: str, details: str = "") -> str:
        """Format error message with optional details"""
        if details:
            return f"{error_type}\nDetails: {details}"
        return error_type
