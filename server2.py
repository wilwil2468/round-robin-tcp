#!/usr/bin/env python3
import socket
import threading

# --- CHANGE THESE VARIABLES FOR MAIN LAB SESSION---
server_port = 8006
server_host = '0.0.0.0'
# --- CHANGE THESE VARIABLES FOR MAIN LAB SESSION---

class TCPServer:
    def __init__(self, host=server_host, port=server_port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connections"""
        print(f"[SERVER] Connection from {client_address}")
        
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                print(f"[SERVER] Received: {message}")
                
                # Echo the message back
                response = f"Echo: {message}"
                client_socket.send(response.encode('utf-8'))
                print(f"[SERVER] Sent: {response}")
                
        except Exception as e:
            print(f"[SERVER] Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"[SERVER] Connection with {client_address} closed")
    
    def start(self):
        """Start the TCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"[SERVER] TCP Server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"[SERVER] Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"[SERVER] Error starting server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the TCP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            print("[SERVER] Server stopped")

if __name__ == "__main__":
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down server...")
        server.stop()

