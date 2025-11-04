"""
Local Storage Module
Handles encrypted storage of messages and configuration
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from crypto_engine import CryptoEngine


class LocalStorage:
    """Manages encrypted local storage"""

    def __init__(self, crypto: CryptoEngine, data_dir: str = ".secure_chat"):
        self.crypto = crypto
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.db_path = self.data_dir / "messages.db"
        self._init_database()

    def _init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Messages table (encrypted)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peer_address TEXT NOT NULL,
                sender TEXT NOT NULL,
                encrypted_content BLOB NOT NULL,
                timestamp TEXT NOT NULL,
                is_outgoing INTEGER NOT NULL
            )
        ''')

        # Peers table (contacts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peers (
                address TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                public_key TEXT NOT NULL,
                verify_key TEXT,
                last_seen TEXT NOT NULL,
                notes TEXT
            )
        ''')

        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_peer
            ON messages(peer_address, timestamp)
        ''')

        conn.commit()
        conn.close()

    def save_message(self, peer_address: str, sender: str,
                    content: str, is_outgoing: bool = False):
        """Save an encrypted message"""
        try:
            # Encrypt the content
            encrypted = self.crypto.encrypt_local_data(content)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO messages
                (peer_address, sender, encrypted_content, timestamp, is_outgoing)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                peer_address,
                sender,
                encrypted,
                datetime.now().isoformat(),
                1 if is_outgoing else 0
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Storage] Error saving message: {e}")

    def get_messages(self, peer_address: str, limit: int = 100) -> List[Dict]:
        """Retrieve messages for a peer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT sender, encrypted_content, timestamp, is_outgoing
                FROM messages
                WHERE peer_address = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (peer_address, limit))

            rows = cursor.fetchall()
            conn.close()

            messages = []
            for row in rows:
                sender, encrypted_content, timestamp, is_outgoing = row

                # Decrypt content
                try:
                    content = self.crypto.decrypt_local_data(encrypted_content)
                    messages.append({
                        'sender': sender,
                        'content': content,
                        'timestamp': timestamp,
                        'is_outgoing': bool(is_outgoing)
                    })
                except Exception as e:
                    print(f"[Storage] Failed to decrypt message: {e}")

            # Reverse to get chronological order
            messages.reverse()
            return messages

        except Exception as e:
            print(f"[Storage] Error retrieving messages: {e}")
            return []

    def save_peer(self, address: str, nickname: str,
                 public_key: str, verify_key: str = None):
        """Save or update peer information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO peers
                (address, nickname, public_key, verify_key, last_seen)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                address,
                nickname,
                public_key,
                verify_key,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Storage] Error saving peer: {e}")

    def get_peer(self, address: str) -> Optional[Dict]:
        """Get peer information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT nickname, public_key, verify_key, last_seen, notes
                FROM peers
                WHERE address = ?
            ''', (address,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'address': address,
                    'nickname': row[0],
                    'public_key': row[1],
                    'verify_key': row[2],
                    'last_seen': row[3],
                    'notes': row[4]
                }
            return None

        except Exception as e:
            print(f"[Storage] Error retrieving peer: {e}")
            return None

    def get_all_peers(self) -> List[Dict]:
        """Get all known peers"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT address, nickname, public_key, verify_key, last_seen
                FROM peers
                ORDER BY last_seen DESC
            ''')

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'address': row[0],
                    'nickname': row[1],
                    'public_key': row[2],
                    'verify_key': row[3],
                    'last_seen': row[4]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"[Storage] Error retrieving peers: {e}")
            return []

    def update_peer_notes(self, address: str, notes: str):
        """Update notes for a peer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE peers
                SET notes = ?
                WHERE address = ?
            ''', (notes, address))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Storage] Error updating notes: {e}")

    def delete_peer(self, address: str):
        """Delete a peer and all associated messages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM messages WHERE peer_address = ?', (address,))
            cursor.execute('DELETE FROM peers WHERE address = ?', (address,))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Storage] Error deleting peer: {e}")

    def get_conversation_list(self) -> List[Dict]:
        """Get list of conversations with last message"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    m.peer_address,
                    p.nickname,
                    m.encrypted_content,
                    m.timestamp,
                    m.is_outgoing
                FROM messages m
                LEFT JOIN peers p ON m.peer_address = p.address
                WHERE m.id IN (
                    SELECT MAX(id)
                    FROM messages
                    GROUP BY peer_address
                )
                ORDER BY m.timestamp DESC
            ''')

            rows = cursor.fetchall()
            conn.close()

            conversations = []
            for row in rows:
                address, nickname, encrypted_content, timestamp, is_outgoing = row

                # Decrypt last message
                try:
                    content = self.crypto.decrypt_local_data(encrypted_content)
                    preview = content[:50] + '...' if len(content) > 50 else content

                    conversations.append({
                        'address': address,
                        'nickname': nickname or address,
                        'last_message': preview,
                        'timestamp': timestamp,
                        'is_outgoing': bool(is_outgoing)
                    })
                except Exception as e:
                    print(f"[Storage] Failed to decrypt preview: {e}")

            return conversations

        except Exception as e:
            print(f"[Storage] Error getting conversation list: {e}")
            return []

    def search_messages(self, query: str, limit: int = 50) -> List[Dict]:
        """Search messages (requires decrypting all messages)"""
        # Note: This is intentionally slow for security reasons
        # A better approach would use searchable encryption
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT peer_address, sender, encrypted_content, timestamp, is_outgoing
                FROM messages
                ORDER BY timestamp DESC
            ''')

            rows = cursor.fetchall()
            conn.close()

            results = []
            for row in rows:
                peer_address, sender, encrypted_content, timestamp, is_outgoing = row

                try:
                    content = self.crypto.decrypt_local_data(encrypted_content)

                    # Case-insensitive search
                    if query.lower() in content.lower():
                        results.append({
                            'peer_address': peer_address,
                            'sender': sender,
                            'content': content,
                            'timestamp': timestamp,
                            'is_outgoing': bool(is_outgoing)
                        })

                        if len(results) >= limit:
                            break
                except Exception as e:
                    continue

            return results

        except Exception as e:
            print(f"[Storage] Error searching messages: {e}")
            return []
