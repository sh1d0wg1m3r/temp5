"""
Logging Module for Secure P2P Chat
Provides structured logging with different levels
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class ChatLogger:
    """Centralized logging for the application"""

    def __init__(self, log_dir: str = ".secure_chat", enable_file_logging: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create logger
        self.logger = logging.getLogger('SecureP2PChat')
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Console handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler (DEBUG and above)
        if enable_file_logging:
            log_file = self.log_dir / f"chat_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

    def security_event(self, event: str, details: str = ""):
        """Log security-related event"""
        msg = f"[SECURITY] {event}"
        if details:
            msg += f" - {details}"
        self.logger.warning(msg)

    def network_event(self, event: str, details: str = ""):
        """Log network-related event"""
        msg = f"[NETWORK] {event}"
        if details:
            msg += f" - {details}"
        self.logger.info(msg)

    def crypto_event(self, event: str, details: str = ""):
        """Log cryptography-related event"""
        msg = f"[CRYPTO] {event}"
        if details:
            msg += f" - {details}"
        self.logger.debug(msg)


# Global logger instance
_global_logger = None


def get_logger(log_dir: str = ".secure_chat", enable_file_logging: bool = True) -> ChatLogger:
    """Get or create the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ChatLogger(log_dir, enable_file_logging)
    return _global_logger
