"""
GUI for Secure P2P Chat
Discord-like interface using customtkinter
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, simpledialog
import asyncio
import threading
from datetime import datetime
from typing import Optional
import traceback

from crypto_engine import CryptoEngine
from p2p_network import P2PNetwork
from local_storage import LocalStorage
from word_encoder import WordEncoder


class LoginWindow(ctk.CTk):
    """Login/Setup window"""

    def __init__(self):
        super().__init__()

        self.title("Secure P2P Chat - Login")
        self.geometry("400x300")

        self.passphrase = None

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="🔐 Secure P2P Chat",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=20)

        # Info
        self.info_label = ctk.CTkLabel(
            self,
            text="Enter your passphrase to unlock your identity.\nThis passphrase encrypts your local data.",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(pady=10)

        # Passphrase entry
        self.passphrase_entry = ctk.CTkEntry(
            self,
            placeholder_text="Passphrase",
            show="*",
            width=300
        )
        self.passphrase_entry.pack(pady=10)
        self.passphrase_entry.bind('<Return>', lambda e: self.login())

        # Login button
        self.login_button = ctk.CTkButton(
            self,
            text="Unlock",
            command=self.login,
            width=300
        )
        self.login_button.pack(pady=10)

        # Status
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=10))
        self.status_label.pack(pady=5)

    def login(self):
        """Handle login"""
        passphrase = self.passphrase_entry.get()

        if len(passphrase) < 8:
            self.status_label.configure(
                text="Passphrase must be at least 8 characters",
                text_color="red"
            )
            return

        self.passphrase = passphrase
        self.destroy()


class ChatWindow(ctk.CTk):
    """Main chat window"""

    def __init__(self, crypto: CryptoEngine, network: P2PNetwork, storage: LocalStorage):
        super().__init__()

        self.crypto = crypto
        self.network = network
        self.storage = storage

        self.title("Secure P2P Chat")
        self.geometry("1000x600")

        # Current selected peer
        self.current_peer = None

        # Setup UI
        self._setup_ui()

        # Register callbacks
        self.network.register_message_callback(self.on_message_received)
        self.network.register_connection_callback(self.on_connection_event)

        # Start network in background
        self.network_thread = threading.Thread(target=self._run_network, daemon=True)
        self.network_thread.start()

        # Protocol to close window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Update peer list periodically
        self.after(1000, self.update_peer_list)

    def _setup_ui(self):
        """Setup the UI components"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left sidebar (peer list)
        self._setup_sidebar()

        # Main chat area
        self._setup_chat_area()

    def _setup_sidebar(self):
        """Setup left sidebar with peer list"""
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.sidebar.grid_rowconfigure(2, weight=1)

        # Title
        title = ctk.CTkLabel(
            self.sidebar,
            text="💬 Conversations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Connect button
        connect_btn = ctk.CTkButton(
            self.sidebar,
            text="+ Connect to Peer",
            command=self.show_connect_dialog,
            height=32
        )
        connect_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Peer list
        self.peer_listbox = tk.Listbox(
            self.sidebar,
            bg="#2b2b2b",
            fg="white",
            selectmode=tk.SINGLE,
            font=("Arial", 11),
            bd=0,
            highlightthickness=0
        )
        self.peer_listbox.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.peer_listbox.bind('<<ListboxSelect>>', self.on_peer_selected)

        # Info button
        info_btn = ctk.CTkButton(
            self.sidebar,
            text="ℹ️ My Info",
            command=self.show_my_info,
            height=32,
            fg_color="gray30"
        )
        info_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

    def _setup_chat_area(self):
        """Setup main chat area"""
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.chat_frame.grid_rowconfigure(1, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.chat_header = ctk.CTkLabel(
            self.chat_frame,
            text="Select a conversation",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.chat_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # Messages area
        self.messages_text = tk.Text(
            self.chat_frame,
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 11),
            state=tk.DISABLED,
            wrap=tk.WORD,
            bd=0
        )
        self.messages_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Configure message tags
        self.messages_text.tag_config("incoming", foreground="#5DADE2")
        self.messages_text.tag_config("outgoing", foreground="#52BE80")
        self.messages_text.tag_config("system", foreground="#F4D03F")
        self.messages_text.tag_config("timestamp", foreground="gray")

        # Input area
        input_frame = ctk.CTkFrame(self.chat_frame)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message...",
            height=40
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=5)
        self.message_entry.bind('<Return>', lambda e: self.send_message())

        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_message,
            width=80,
            height=40
        )
        send_btn.grid(row=0, column=1, padx=5)

    def show_connect_dialog(self):
        """Show dialog to connect to peer"""
        dialog = ctk.CTkInputDialog(
            text="Enter peer address (IP:PORT):",
            title="Connect to Peer"
        )
        address = dialog.get_input()

        if address:
            try:
                if ':' not in address:
                    messagebox.showerror("Error", "Address must be in format IP:PORT")
                    return

                host, port = address.split(':')
                port = int(port)

                # Connect in background
                asyncio.run_coroutine_threadsafe(
                    self.network.connect_to_peer(host, port),
                    self.network_loop
                )

                self.add_system_message(f"Connecting to {address}...")

            except Exception as e:
                messagebox.showerror("Error", f"Invalid address: {e}")

    def show_my_info(self):
        """Show user's own information"""
        public_key = self.crypto.get_public_key_hex()
        address = self.network.get_public_address()

        fingerprint = WordEncoder.create_fingerprint(public_key, address)

        info_text = f"Your Address: {address}\n\n"
        info_text += f"Your Public Key:\n{public_key[:32]}...\n\n"
        info_text += f"Fingerprint:\n{fingerprint}\n\n"
        info_text += "Share your address with peers to allow them to connect."

        # Create info window
        info_window = ctk.CTkToplevel(self)
        info_window.title("My Information")
        info_window.geometry("500x400")

        text_widget = ctk.CTkTextbox(info_window, width=480, height=350)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")

    def update_peer_list(self):
        """Update the peer list"""
        self.peer_listbox.delete(0, tk.END)

        # Get connected peers
        connected = self.network.get_connected_peers()

        for peer in connected:
            display_name = f"🟢 {peer['nickname']} ({peer['address']})"
            self.peer_listbox.insert(tk.END, display_name)

        # Schedule next update
        self.after(2000, self.update_peer_list)

    def on_peer_selected(self, event):
        """Handle peer selection"""
        selection = self.peer_listbox.curselection()
        if not selection:
            return

        # Get selected peer address
        text = self.peer_listbox.get(selection[0])
        # Extract address from text (format: "🟢 Name (address)")
        if '(' in text and ')' in text:
            address = text.split('(')[1].split(')')[0]
            self.current_peer = address
            self.chat_header.configure(text=f"Chat with {text.split('(')[0].strip()}")

            # Load message history
            self.load_message_history(address)

    def load_message_history(self, peer_address: str):
        """Load message history for peer"""
        self.messages_text.configure(state=tk.NORMAL)
        self.messages_text.delete(1.0, tk.END)

        messages = self.storage.get_messages(peer_address, limit=100)

        for msg in messages:
            self.display_message(
                msg['sender'],
                msg['content'],
                msg['timestamp'],
                msg['is_outgoing']
            )

        self.messages_text.configure(state=tk.DISABLED)
        self.messages_text.see(tk.END)

    def display_message(self, sender: str, content: str,
                       timestamp: str, is_outgoing: bool = False):
        """Display a message in the chat"""
        self.messages_text.configure(state=tk.NORMAL)

        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp

        # Format message
        tag = "outgoing" if is_outgoing else "incoming"
        prefix = "You" if is_outgoing else sender

        self.messages_text.insert(tk.END, f"[{time_str}] ", "timestamp")
        self.messages_text.insert(tk.END, f"{prefix}: ", tag)
        self.messages_text.insert(tk.END, f"{content}\n")

        self.messages_text.configure(state=tk.DISABLED)
        self.messages_text.see(tk.END)

    def add_system_message(self, message: str):
        """Add a system message"""
        self.messages_text.configure(state=tk.NORMAL)
        self.messages_text.insert(tk.END, f"[SYSTEM] {message}\n", "system")
        self.messages_text.configure(state=tk.DISABLED)
        self.messages_text.see(tk.END)

    def send_message(self):
        """Send message to current peer"""
        if not self.current_peer:
            messagebox.showwarning("No Peer", "Select a peer first")
            return

        message = self.message_entry.get().strip()
        if not message:
            return

        # Clear entry
        self.message_entry.delete(0, tk.END)

        # Send message
        asyncio.run_coroutine_threadsafe(
            self.network.send_message(self.current_peer, message),
            self.network_loop
        )

        # Display message
        self.display_message("You", message, datetime.now().isoformat(), is_outgoing=True)

        # Save to storage
        self.storage.save_message(self.current_peer, "You", message, is_outgoing=True)

    def on_message_received(self, message: dict):
        """Callback for received messages"""
        # Save to storage
        self.storage.save_message(
            message['sender_address'],
            message['sender'],
            message['content'],
            is_outgoing=False
        )

        # Display if this is the current conversation
        if self.current_peer == message['sender_address']:
            self.after(0, lambda: self.display_message(
                message['sender'],
                message['content'],
                message['timestamp'],
                is_outgoing=False
            ))

    def on_connection_event(self, event_type: str, peer):
        """Callback for connection events"""
        if event_type == 'connected':
            self.after(0, lambda: self.add_system_message(
                f"Connected to {peer.nickname} ({peer.address})"
            ))
            # Save peer
            self.storage.save_peer(
                peer.address,
                peer.nickname,
                peer.public_key,
                peer.verify_key
            )
        elif event_type == 'disconnected':
            self.after(0, lambda: self.add_system_message(
                f"Disconnected from {peer.nickname} ({peer.address})"
            ))

    def _run_network(self):
        """Run network in background thread"""
        try:
            self.network_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.network_loop)

            self.network_loop.run_until_complete(self.network.start_server())
        except Exception as e:
            print(f"[GUI] Network error: {e}")
            traceback.print_exc()

    def on_closing(self):
        """Handle window closing"""
        # Shutdown network
        if hasattr(self, 'network_loop'):
            asyncio.run_coroutine_threadsafe(
                self.network.shutdown(),
                self.network_loop
            )

        self.destroy()


def main():
    """Main entry point"""
    # Set appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Show login window
    login_window = LoginWindow()
    login_window.mainloop()

    if not login_window.passphrase:
        return

    # Initialize crypto
    crypto = CryptoEngine()
    if not crypto.initialize_keys(login_window.passphrase):
        messagebox.showerror("Error", "Failed to initialize encryption keys")
        return

    # Initialize storage
    storage = LocalStorage(crypto)

    # Initialize network
    network = P2PNetwork(crypto, port=8765)

    # Show main window
    app = ChatWindow(crypto, network, storage)
    app.mainloop()


if __name__ == "__main__":
    main()
