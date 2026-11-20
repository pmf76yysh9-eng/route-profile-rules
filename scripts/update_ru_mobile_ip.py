#!/usr/bin/env python3
"""Convert Amnezia's mobile IP list to RU-only Shadowrocket IP rules."""
import bisect
import ipaddress
import json
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/lib4u/amnezia-tunneling-ru/main/"
OUTPUT = Path("ru-mobile-ip.list")


def load(name):
    request = urllib.request.Request(BASE + name, headers={"User-Agent": "route-profile-rules"})
    with urllib.request.urlopen(request, timeout=40) as response:
        entries = json.load(response)
    return [ipaddress.IPv4Network(entry["hostname"]) for entry in entries]


lite = load("amnezia-ip-lite.json")
ru = sorted(ipaddress.collapse_addresses(load("amnezia-ip.json")),
            key=lambda net: int(net.network_address))
starts = [int(net.network_address) for net in ru]
kept = []
for net in lite:
    index = bisect.bisect_right(starts, int(net.network_address)) - 1
    if index >= 0 and net.subnet_of(ru[index]):
        kept.append(net)

if not 500 <= len(kept) <= 3000 or ipaddress.IPv4Address("1.1.1.1") in kept:
    raise SystemExit(f"Unexpected RU-only mobile IP list: {len(kept)}")

header = (
    "# Russian IPv4 ranges for Shadowrocket\n"
    "# Source: lib4u/amnezia-tunneling-ru amnezia-ip-lite.json\n"
    "# Kept only ranges contained in the source's full RU IP list.\n"
)
OUTPUT.write_text(
    header + "".join(f"IP-CIDR,{net},no-resolve\n" for net in sorted(kept, key=lambda n: int(n.network_address))),
    encoding="utf-8",
)
print(f"Wrote {len(kept)} RU-only IP rules to {OUTPUT}")
