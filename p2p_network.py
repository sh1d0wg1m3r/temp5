"""
P2P Network Layer using WebSockets
Handles peer-to-peer connections with encryption and obfuscation
"""

import asyncio
import websockets
from websockets.server import serve
from websockets.client import connect
import json
import socket
from typing import Optional, Callable, Dict, Set
from datetime import datetime
import traceback

from obfuscation import ProtocolWrapper, TrafficObfuscator
from crypto_engine import CryptoEngine
import time
from collections import deque


class Peer:
    """Represents a connected peer"""

    def __init__(self, websocket, address: str, public_key: str = None):
        self.websocket = websocket
        self.address = address
        self.public_key = public_key
        self.verify_key = None
        self.nickname = "Unknown"
        self.connected_at = datetime.now()
        self.protocol = ProtocolWrapper()

        # Rate limiting (max 100 messages per 60 seconds)
        self.message_timestamps = deque(maxlen=100)
        self.rate_limit_window = 60  # seconds
        self.max_messages_per_window = 100

    def check_rate_limit(self) -> bool:
        """Check if peer is within rate limits"""
        now = time.time()

        # Remove old timestamps
        while self.message_timestamps and (now - self.message_timestamps[0]) > self.rate_limit_window:
            self.message_timestamps.popleft()

        # Check limit
        if len(self.message_timestamps) >= self.max_messages_per_window:
            return False

        # Add current timestamp
        self.message_timestamps.append(now)
        return True

    def __str__(self):
        return f"{self.nickname} ({self.address})"


class P2PNetwork:
    """Manages P2P networking with WebSocket"""

    def __init__(self, crypto_engine: CryptoEngine, port: int = 8765):
        self.crypto = crypto_engine
        self.port = port
        self.server = None
        self.peers: Dict[str, Peer] = {}  # address -> Peer
        self.message_callbacks = []
        self.connection_callbacks = []
        self.running = False

        # Get local IP
        self.local_ip = self._get_local_ip()

    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to external address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    def get_public_address(self) -> str:
        """Get the address peers should connect to"""
        return f"{self.local_ip}:{self.port}"

    def register_message_callback(self, callback: Callable):
        """Register callback for received messages"""
        self.message_callbacks.append(callback)

    def register_connection_callback(self, callback: Callable):
        """Register callback for connection events"""
        self.connection_callbacks.append(callback)

    async def start_server(self):
        """Start WebSocket server to accept connections"""
        try:
            self.server = await serve(
                self._handle_client,
                "0.0.0.0",
                self.port,
                max_size=10 * 1024 * 1024  # 10MB max message size
            )
            self.running = True
            print(f"[P2P] Server started on {self.local_ip}:{self.port}")

            # Keep server running
            await asyncio.Future()  # Run forever
        except Exception as e:
            print(f"[P2P] Server error: {e}")
            traceback.print_exc()

    async def _handle_client(self, websocket, path):
        """Handle incoming client connection"""
        peer_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"[P2P] New connection from {peer_address}")

        peer = Peer(websocket, peer_address)

        try:
            # Send our handshake
            handshake = peer.protocol.initiate_handshake()
            await websocket.send(handshake)

            # Wait for their handshake
            their_handshake = await websocket.recv()
            if not peer.protocol.process_handshake(their_handshake):
                print(f"[P2P] Invalid handshake from {peer_address}")
                return

            # Exchange identity (public keys)
            await self._exchange_identity(peer)

            # Add to peers
            self.peers[peer_address] = peer

            # Notify connection
            for callback in self.connection_callbacks:
                callback('connected', peer)

            # Handle messages
            await self._message_loop(peer)

        except websockets.exceptions.ConnectionClosed:
            print(f"[P2P] Connection closed: {peer_address}")
        except Exception as e:
            print(f"[P2P] Error handling client {peer_address}: {e}")
            traceback.print_exc()
        finally:
            # Remove peer
            if peer_address in self.peers:
                del self.peers[peer_address]

            # Notify disconnection
            for callback in self.connection_callbacks:
                callback('disconnected', peer)

    async def _exchange_identity(self, peer: Peer):
        """Exchange public keys with peer"""
        # Send our identity
        identity = {
            'type': 'identity',
            'public_key': self.crypto.get_public_key_hex(),
            'verify_key': self.crypto.get_verify_key_hex(),
            'nickname': 'User'
        }

        wrapped = peer.protocol.wrap_application_message(identity)
        await peer.websocket.send(wrapped)

        # Receive their identity
        data = await peer.websocket.recv()

        if isinstance(data, bytes):
            their_identity = peer.protocol.unwrap_application_message(data)

            if their_identity.get('type') == 'identity':
                peer.public_key = their_identity['public_key']
                peer.verify_key = their_identity['verify_key']
                peer.nickname = their_identity.get('nickname', 'Unknown')
                print(f"[P2P] Identity exchanged with {peer.nickname}")

    async def _message_loop(self, peer: Peer):
        """Handle incoming messages from peer"""
        async for message in peer.websocket:
            try:
                # Check rate limit
                if not peer.check_rate_limit():
                    print(f"[P2P] Rate limit exceeded for {peer.address}, dropping message")
                    continue

                if isinstance(message, bytes):
                    # Unwrap obfuscation
                    data = peer.protocol.unwrap_application_message(message)

                    # Handle different message types
                    if data.get('type') == 'chat':
                        await self._handle_chat_message(peer, data)
                    elif data.get('type') == 'keepalive':
                        # Ignore keepalive messages
                        pass
                    else:
                        print(f"[P2P] Unknown message type: {data.get('type')}")

            except Exception as e:
                print(f"[P2P] Error processing message: {e}")
                traceback.print_exc()

    async def _handle_chat_message(self, peer: Peer, data: dict):
        """Handle encrypted chat message"""
        try:
            # Decrypt message
            encrypted_data = data['encrypted']
            plaintext = self.crypto.decrypt_message(encrypted_data)

            # Create message object
            message = {
                'sender': peer.nickname,
                'sender_address': peer.address,
                'content': plaintext,
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }

            # Notify callbacks
            for callback in self.message_callbacks:
                callback(message)

        except Exception as e:
            print(f"[P2P] Failed to decrypt message: {e}")

    async def connect_to_peer(self, host: str, port: int):
        """Connect to a peer"""
        uri = f"ws://{host}:{port}"
        peer_address = f"{host}:{port}"

        try:
            print(f"[P2P] Connecting to {uri}...")
            websocket = await connect(uri, max_size=10 * 1024 * 1024)

            peer = Peer(websocket, peer_address)

            # Receive their handshake
            their_handshake = await websocket.recv()
            if not peer.protocol.process_handshake(their_handshake):
                print(f"[P2P] Invalid handshake from {peer_address}")
                return

            # Send our handshake
            handshake = peer.protocol.initiate_handshake()
            await websocket.send(handshake)

            # Exchange identity
            await self._exchange_identity(peer)

            # Add to peers
            self.peers[peer_address] = peer

            # Notify connection
            for callback in self.connection_callbacks:
                callback('connected', peer)

            print(f"[P2P] Connected to {peer.nickname} at {peer_address}")

            # Start message loop
            asyncio.create_task(self._message_loop(peer))

        except Exception as e:
            print(f"[P2P] Failed to connect to {uri}: {e}")
            traceback.print_exc()

    async def send_message(self, peer_address: str, message: str):
        """Send encrypted message to peer"""
        if peer_address not in self.peers:
            print(f"[P2P] Peer not found: {peer_address}")
            return

        peer = self.peers[peer_address]

        try:
            # Encrypt message
            encrypted_data = self.crypto.encrypt_message(message, peer.public_key)

            # Wrap in chat message
            chat_message = {
                'type': 'chat',
                'encrypted': encrypted_data,
                'timestamp': datetime.now().isoformat()
            }

            # Add obfuscation
            wrapped = peer.protocol.wrap_application_message(chat_message)

            # Add random delay for timing jitter
            await asyncio.sleep(TrafficObfuscator.add_timing_jitter())

            # Send
            await peer.websocket.send(wrapped)

        except Exception as e:
            print(f"[P2P] Failed to send message: {e}")
            traceback.print_exc()

    async def broadcast_message(self, message: str):
        """Send message to all connected peers"""
        for peer_address in list(self.peers.keys()):
            await self.send_message(peer_address, message)

    def get_connected_peers(self) -> list:
        """Get list of connected peers"""
        return [
            {
                'address': peer.address,
                'nickname': peer.nickname,
                'public_key': peer.public_key,
                'connected_at': peer.connected_at.isoformat()
            }
            for peer in self.peers.values()
        ]

    async def disconnect_peer(self, peer_address: str):
        """Disconnect from a peer"""
        if peer_address in self.peers:
            peer = self.peers[peer_address]
            await peer.websocket.close()
            del self.peers[peer_address]

    async def shutdown(self):
        """Shutdown the network"""
        self.running = False

        # Close all peer connections
        for peer in list(self.peers.values()):
            await peer.websocket.close()

        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
