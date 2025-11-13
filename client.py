#!/usr/bin/env python3
import socket
import time

# --- CHANGE THESE VARIABLES FOR MAIN LAB SESSION---
proxy_host = '74.225.180.44'
proxy_port = 9090
# --- CHANGE THESE VARIABLES FOR MAIN LAB SESSION---

class TCPClient:
    def __init__(self, proxy_host=proxy_host, proxy_port=proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.client_socket = None
    
    def connect(self):
        """Connect to the proxy server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.proxy_host, self.proxy_port))
            print(f"[CLIENT] Connected to proxy at {self.proxy_host}:{self.proxy_port}")
            return True
        except Exception as e:
            print(f"[CLIENT] Error connecting to proxy: {e}")
            return False
    
    def send_message(self, message):
        """Send a message through the proxy"""
        try:
            if not self.client_socket:
                print("[CLIENT] Not connected to proxy")
                return None
            
            self.client_socket.send(message.encode('utf-8'))
            print(f"[CLIENT] Sent: {message}")
            
            response = self.client_socket.recv(1024)
            response_text = response.decode('utf-8')
            print(f"[CLIENT] Received: {response_text}")
            
            return response_text
            
        except Exception as e:
            print(f"[CLIENT] Error sending message: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from the proxy server"""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            print("[CLIENT] Disconnected from proxy")
    
    def run_test_session(self):
        """Run a test session with multiple messages"""
        if not self.connect():
            return
        
        test_messages = [
            "Hello, World!",
            "This is a test message",
            "Testing proxy communication",
            "Message number 4",
            "Final test message"
        ]
        
        print("\n[CLIENT] Starting test session...")
        print("=" * 50)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n[CLIENT] Test {i}/{len(test_messages)}")
            response = self.send_message(message)
            
            if response:
                print(f"[CLIENT] Communication successful")
            else:
                print(f"[CLIENT] Communication failed")
                break
            
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print("[CLIENT] Test session completed")
        self.disconnect()

def interactive_mode():
    """Interactive mode for manual testing"""
    client = TCPClient()
    
    if not client.connect():
        return
    
    print("\n[CLIENT] Interactive mode started")
    print("[CLIENT] Type messages to send (or 'quit' to exit)")
    print("-" * 40)
    
    try:
        while True:
            message = input("Enter message: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            if message:
                client.send_message(message)
            
    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user")
    finally:
        client.disconnect()

if __name__ == "__main__":
    import sys
    
    print("TCP Client - Proxy Communication Test")
    print("=====================================")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        client = TCPClient()
        client.run_test_session()
        
        print("\n[CLIENT] To run in interactive mode, use: python3 client.py --interactive")

