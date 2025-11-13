#!/usr/bin/env python3
import socket
import threading
import hashlib
import time

# --- CHANGE THESE VARIABLES FOR MAIN LAB SESSION---
proxy_host = '0.0.0.0'
proxy_port = 9090

# Two target servers for load balancing
server1_host = '20.193.255.80'
server1_port = 8005
server2_host = '20.193.255.80'  # Change this if using different host
server2_port = 8006  # Change this to the second server's port
# --- CHANGE THESE VARIABLES FOR MAIN LAB SESSION---

class TCPProxy:
    def __init__(self, proxy_host=proxy_host, proxy_port=proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        
        # Two target servers
        self.servers = [
            {'host': server1_host, 'port': server1_port, 'id': 1},
            {'host': server2_host, 'port': server2_port, 'id': 2}
        ]
        
        self.proxy_socket = None
        self.running = False

    def compute_delay(self, message):
        """
        Compute a deterministic delay value based on the MD5 hash of the input message.

        This function generates a pseudo-random delay (0-999 milliseconds) that is 
        consistently reproducible for the same input message. It uses MD5 hashing to 
        convert the input message into a byte sequence, then aggregates the byte values 
        using modulo arithmetic to produce a delay within the range [0, 1000).

        Args:
            message (str): The input message to hash and compute delay from.

        Returns:
            int: A delay value in milliseconds, ranging from 0 to 999 (inclusive).
                 The same input message will always produce the same delay value. 
        """
        # Convert message to MD5 hash
        md5_hash = hashlib.md5(message.encode('utf-8')).digest()
    
        # Aggregate byte values
        byte_sum = sum(md5_hash)
    
        # Use modulo to get value in range [0, 999]
        delay = byte_sum % 1000
    
        return delay
    
    def handle_client(self, client_socket, client_address):
        """Handle client connection with round-robin load balancing"""
        print(f"[PROXY] Client connected from {client_address}")
        
        # Each client has its own round-robin counter
        round_robin_index = 0
        request_count = 0
        
        try:
            while True:
                # Receive data from client
                data = client_socket.recv(1024)
                if not data:
                    print(f"[PROXY] Client {client_address} disconnected")
                    break
                
                request_count += 1
                message = data.decode('utf-8').strip()
                
                # Select server using round-robin
                server = self.servers[round_robin_index]
                server_id = server['id']
                server_host = server['host']
                server_port = server['port']
                
                print(f"[PROXY] Client {client_address} | Request #{request_count} | Message: '{message}' -> Server {server_id} ({server_host}:{server_port})")
                
                try:
                    # Connect to selected server
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.settimeout(5.0)  # 5 second timeout
                    server_socket.connect((server_host, server_port))
                    
                    # Send data to server
                    server_socket.send(data)
                    
                    # Receive response from server
                    response = server_socket.recv(1024)
                    server_socket.close()
                    
                    if response:
                        response_message = response.decode('utf-8').strip()
                        print(f"[PROXY] Server {server_id} response: '{response_message}'")
                        
                        # Compute and apply delay
                        expected_delay = self.compute_delay(message)
                        print(f"[PROXY] Applying delay: {expected_delay}ms")
                        time.sleep(expected_delay / 1000.0)
                        
                        # Send response back to client
                        client_socket.send(response)
                        print(f"[PROXY] Response sent to client {client_address}")
                    
                except socket.timeout:
                    print(f"[PROXY] Timeout connecting to Server {server_id}")
                    error_msg = f"Error: Server {server_id} timeout\n"
                    client_socket.send(error_msg.encode('utf-8'))
                    
                except Exception as e:
                    print(f"[PROXY] Error communicating with Server {server_id}: {e}")
                    error_msg = f"Error: Failed to reach Server {server_id}\n"
                    client_socket.send(error_msg.encode('utf-8'))
                
                # Move to next server in round-robin (0 -> 1 -> 0 -> 1 ...)
                round_robin_index = (round_robin_index + 1) % len(self.servers)
                print(f"[PROXY] Next request from {client_address} will go to Server {self.servers[round_robin_index]['id']}")
                print("-" * 60)
                
        except Exception as e:
            print(f"[PROXY] Error handling client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            print(f"[PROXY] Connection with {client_address} closed (Total requests: {request_count})")
    
    def start(self):
        """Start the TCP proxy server"""
        try:
            self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.proxy_socket.bind((self.proxy_host, self.proxy_port))
            self.proxy_socket.listen(5)
            self.running = True
            
            print(f"[PROXY] TCP Proxy with Round-Robin Load Balancing")
            print(f"[PROXY] Listening on {self.proxy_host}:{self.proxy_port}")
            print(f"[PROXY] Server 1: {self.servers[0]['host']}:{self.servers[0]['port']}")
            print(f"[PROXY] Server 2: {self.servers[1]['host']}:{self.servers[1]['port']}")
            print("=" * 60)
            
            while self.running:
                try:
                    client_socket, client_address = self.proxy_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"[PROXY] Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"[PROXY] Error starting proxy: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the TCP proxy server"""
        self.running = False
        if self.proxy_socket:
            self.proxy_socket.close()
            print("[PROXY] Proxy stopped")

if __name__ == "__main__":
    proxy = TCPProxy()
    try:
        proxy.start()
    except KeyboardInterrupt:
        print("\n[PROXY] Shutting down proxy...")
        proxy.stop()