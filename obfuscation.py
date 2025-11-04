"""
Traffic Obfuscation Layer
Adds pseudo-SSH handshake and padding to make traffic analysis harder
"""

import os
import struct
import json
from typing import Tuple
import random


class TrafficObfuscator:
    """Obfuscates traffic to make it harder to analyze"""

    # SSH-like protocol identification
    SSH_BANNER = b"SSH-2.0-OpenSSH_8.9"
    PADDING_BYTE = b'\x00'

    @staticmethod
    def create_ssh_like_handshake() -> bytes:
        """
        Create a fake SSH handshake packet
        This makes initial connection look like SSH
        """
        banner = TrafficObfuscator.SSH_BANNER + b'\r\n'

        # Add some random "key exchange" data
        kex_data = os.urandom(32)

        handshake = banner + kex_data
        return handshake

    @staticmethod
    def wrap_message(message_data: dict) -> bytes:
        """
        Wrap message in obfuscated format:
        [4 bytes: total length][4 bytes: payload length][payload][random padding]
        """
        # Convert message to JSON
        payload = json.dumps(message_data).encode('utf-8')
        payload_len = len(payload)

        # Add random padding (between 16 and 256 bytes)
        padding_len = random.randint(16, 256)
        padding = os.urandom(padding_len)

        # Calculate total length
        total_len = 4 + 4 + payload_len + padding_len

        # Pack the message
        packed = struct.pack('!I', total_len)  # Total length
        packed += struct.pack('!I', payload_len)  # Payload length
        packed += payload  # Actual payload
        packed += padding  # Random padding

        return packed

    @staticmethod
    def unwrap_message(data: bytes) -> Tuple[dict, int]:
        """
        Unwrap obfuscated message
        Returns: (message_dict, bytes_consumed)
        """
        if len(data) < 8:
            raise ValueError("Insufficient data for header")

        # Unpack header
        total_len = struct.unpack('!I', data[0:4])[0]
        payload_len = struct.unpack('!I', data[4:8])[0]

        # Check if we have enough data
        if len(data) < total_len:
            raise ValueError(f"Incomplete message: have {len(data)}, need {total_len}")

        # Extract payload
        payload = data[8:8+payload_len]

        # Parse JSON
        message_data = json.loads(payload.decode('utf-8'))

        return message_data, total_len

    @staticmethod
    def add_timing_jitter(min_ms: int = 10, max_ms: int = 100) -> float:
        """
        Generate random delay to add timing jitter
        Makes traffic analysis harder
        Returns: delay in seconds
        """
        return random.randint(min_ms, max_ms) / 1000.0

    @staticmethod
    def create_dummy_packet() -> bytes:
        """
        Create a dummy packet for traffic pattern obfuscation
        Can be sent periodically to hide real message patterns
        """
        dummy_data = {
            'type': 'keepalive',
            'timestamp': random.randint(1000000000, 9999999999),
            'nonce': os.urandom(16).hex()
        }
        return TrafficObfuscator.wrap_message(dummy_data)

    @staticmethod
    def obfuscate_length(data: bytes, target_size: int = 1024) -> bytes:
        """
        Pad data to target size to hide actual message length
        """
        current_len = len(data)

        if current_len >= target_size:
            return data

        padding_needed = target_size - current_len
        padding = os.urandom(padding_needed)

        # Add length marker before padding
        return data + struct.pack('!I', current_len) + padding

    @staticmethod
    def deobfuscate_length(data: bytes) -> bytes:
        """
        Remove length obfuscation padding
        """
        if len(data) < 4:
            return data

        # Try to find length marker near the end
        try:
            # Last 4 bytes might be the length marker
            original_len = struct.unpack('!I', data[-4:])[0]

            if original_len < len(data) - 4:
                return data[:original_len]
        except:
            pass

        return data


class ProtocolWrapper:
    """Wraps the entire protocol with SSH-like appearance"""

    def __init__(self):
        self.handshake_complete = False
        self.buffer = b''

    def initiate_handshake(self) -> bytes:
        """Start the fake SSH handshake"""
        return TrafficObfuscator.create_ssh_like_handshake()

    def process_handshake(self, data: bytes) -> bool:
        """Process received handshake data"""
        # Just check if it looks like our handshake
        if TrafficObfuscator.SSH_BANNER in data:
            self.handshake_complete = True
            return True
        return False

    def wrap_application_message(self, message_dict: dict) -> bytes:
        """Wrap application-level message with obfuscation"""
        # First layer: our protocol wrapper
        wrapped = TrafficObfuscator.wrap_message(message_dict)

        # Second layer: length obfuscation (optional, for smaller messages)
        if len(wrapped) < 512:
            wrapped = TrafficObfuscator.obfuscate_length(wrapped, target_size=1024)

        return wrapped

    def unwrap_application_message(self, data: bytes) -> dict:
        """Unwrap application-level message"""
        # Try to deobfuscate length first
        data = TrafficObfuscator.deobfuscate_length(data)

        # Unwrap our protocol
        message, _ = TrafficObfuscator.unwrap_message(data)

        return message
