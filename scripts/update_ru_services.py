#!/usr/bin/env python3
"""Convert the public Amnezia RU domain list to Shadowrocket RULE-SET format."""
import ipaddress
import json
import re
import urllib.request
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/lib4u/amnezia-tunneling-ru/main/amnezia.json"
OUTPUT = Path("ru-services.list")
EXCLUDED_ZONES = (".arpa", ".local", ".localhost", ".lan", ".internal", ".home",
                  ".invalid", ".test", ".example")
VALID_DOMAIN = re.compile(r"^[a-z0-9.-]+$")

request = urllib.request.Request(SOURCE, headers={"User-Agent": "route-profile-rules"})
with urllib.request.urlopen(request, timeout=30) as response:
    entries = json.load(response)

domains = set()
for entry in entries:
    name = str(entry.get("hostname", "")).strip().lower()
    if "." not in name or name.endswith(EXCLUDED_ZONES):
        continue
    if not VALID_DOMAIN.fullmatch(name):
        continue
    try:
        ipaddress.ip_address(name)
        continue
    except ValueError:
        pass
    domains.add(name)

if not 1500 <= len(domains) <= 10000:
    raise SystemExit(f"Unexpected domain count: {len(domains)}")

header = (
    "# Russian service domains for Shadowrocket\n"
    "# Source: https://github.com/lib4u/amnezia-tunneling-ru/blob/main/amnezia.json\n"
    "# Generated from the public domain list; private and reverse DNS zones excluded.\n"
)
OUTPUT.write_text(
    header + "".join(f"DOMAIN-SUFFIX,{name}\n" for name in sorted(domains)),
    encoding="utf-8",
)
print(f"Wrote {len(domains)} rules to {OUTPUT}")
