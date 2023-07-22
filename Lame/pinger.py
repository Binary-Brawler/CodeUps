#!/usr/bin/env python3

# Lame CodeUp - pinger.py - use ICMP to see if target is alive
# ---------------------------------------------------------------
# Author    : Chaotic_Guru                                       |
# Github    : https://github.com/ChaoticHackingNetwork           |
# Discord   : https://discord.gg/nv445EX (ChaoticHackingNetwork) | 						 |					 
# ---------------------------------------------------------------

import os
import socket
import struct
import select
import sys
import time

# Calculate checksum for the given data
def checksum(data):
    # If the length of the data is odd, append a null byte to make it even.
    if len(data) % 2 != 0:
        data += b'\x00'
    
    # Initialize the checksum_value to 0.
    checksum_value = 0
    
    # Iterate through the data two bytes at a time.
    for i in range(0, len(data), 2):
        # Combine two bytes into a 16-bit value and add it to the checksum_value.
        checksum_value += (data[i] << 8) + data[i+1]
    
    # Add the carry bits (if any) to the lower 16 bits to the higher 16 bits.
    checksum_value = (checksum_value >> 16) + (checksum_value & 0xffff)
    
    # Add the carry bits (if any) to the higher 16 bits.
    checksum_value += checksum_value >> 16
    
    # Take the one's complement (bitwise NOT) of the checksum_value and keep only the lower 16 bits.
    return ~checksum_value & 0xffff


# Create a raw socket
def create_socket():
    try:
        # Create a raw socket using the socket() function with the following parameters:
        # - socket.AF_INET: Address Family (IPv4)
        # - socket.SOCK_RAW: Socket Type (Raw socket, which allows access to lower-level protocols)
        # - socket.IPPROTO_ICMP: Protocol (ICMP - Internet Control Message Protocol)
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        
        # Set socket option SO_REUSEADDR to 1 (True) to allow reusing local addresses.
        # This is useful in case the socket is closed but its port is still in a TIME_WAIT state.
        # It allows the socket to be reused immediately without waiting for the TIME_WAIT to expire.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Return the created socket object.
        return sock
    except socket.error as e:
        # If there is an error during socket creation, handle it by printing an error message.
        print(f"Socket creation failed: {e}")
        return None

# Function to send an ICMP echo request
def send_ping_request(sock, dest_ip, seq_num, timeout):
    # ICMP header fields
    icmp_type = 8  # ICMP type 8 = Echo Request
    code = 0
    checksum_value = 0
    identifier = os.getpid() & 0xffff  # Generate a unique identifier for this request based on the process ID

    # ICMP payload (data)
    payload = b'Hello, World!'  # Change this as needed. This is the data sent along with the request.

    # Create ICMP header
    icmp_header = struct.pack('!BBHHH', icmp_type, code, checksum_value, identifier, seq_num)

    # Calculate the checksum for the ICMP header and payload
    checksum_value = checksum(icmp_header + payload)

    # Create final ICMP packet by including the calculated checksum
    icmp_packet = struct.pack('!BBHHH', icmp_type, code, checksum_value, identifier, seq_num) + payload

    # Send ICMP packet to the destination IP address
    try:
        sock.sendto(icmp_packet, (dest_ip, 0))
    except socket.error as e:
        print(f"Socket error while sending packet: {e}")
        return

    # Wait for the response within the specified timeout period
    start_time = time.time()
    ready = select.select([sock], [], [], timeout)
    if ready[0]:
        # Receive the ICMP response and get the sender's address
        response, addr = sock.recvfrom(1024)

        # Calculate the elapsed time since the request was sent to measure the round-trip time (RTT)
        elapsed_time = (time.time() - start_time) * 1000

        # Print the received ICMP response and the elapsed time
        print(f"Received ICMP response from {addr[0]} in {elapsed_time:.2f}ms")
    else:
        # Request timed out if no response received within the timeout period
        print("Request timed out")


# Main function
def main():
    dest_ip = sys.argv[1] # This is a way of using arguments in your programs
    timeout = 1  # Timeout value in seconds
    num_pings = 4  # Number of pings to send

    # Create a connection
    sock = create_socket()
    # This is our socket object, if it is not None do work
    if sock:
    	# Iterate through our num_pings count
        for seq_num in range(num_pings):
            print(f"Pinging {dest_ip} with ICMP sequence number {seq_num+1}")
            send_ping_request(sock, dest_ip, seq_num+1, timeout)
            time.sleep(1)  # Wait for 1 second between pings
        sock.close()


# We shall touch on this later
if __name__ == '__main__':
    main()
