#!/usr/bin/env python3
"""Convert the full Amnezia mobile IP list to Shadowrocket IP rules."""
import ipaddress
import json
import urllib.request
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/lib4u/amnezia-tunneling-ru/main/amnezia-ip-lite.json"
OUTPUT = Path("ru-mobile-ip.list")

request = urllib.request.Request(SOURCE, headers={"User-Agent": "route-profile-rules"})
with urllib.request.urlopen(request, timeout=40) as response:
    entries = json.load(response)

networks = [ipaddress.IPv4Network(entry["hostname"]) for entry in entries]
if not 1000 <= len(networks) <= 3000:
    raise SystemExit(f"Unexpected mobile IP list size: {len(networks)}")

header = (
    "# Mobile IP ranges for Shadowrocket\n"
    "# Source: https://github.com/lib4u/amnezia-tunneling-ru/blob/main/amnezia-ip-lite.json\n"
    "# Full upstream list, including non-RU CDN addresses.\n"
)
OUTPUT.write_text(
    header + "".join(f"IP-CIDR,{network},no-resolve\n" for network in networks),
    encoding="utf-8",
)
print(f"Wrote {len(networks)} mobile IP rules to {OUTPUT}")
