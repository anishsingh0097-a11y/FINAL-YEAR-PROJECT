import requests
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def get_location(ip):

    # Take first real IP if multiple IPs exist
    if "," in ip:
        ip = ip.split(",")[0].strip()

    # IPv4 private prefixes
    private_prefixes = (
        "127.", "192.168.", "10.",
        "172.16.", "172.17.", "172.18.", "172.19.",
        "172.20.", "172.21.", "172.22.", "172.23.",
        "172.24.", "172.25.", "172.26.", "172.27.",
        "172.28.", "172.29.", "172.30.", "172.31."
    )

    # IPv6 local prefixes
    ipv6_local_prefixes = ("::1", "fe80:", "fc", "fd")

    is_local_v4 = ip in ("127.0.0.1",) or any(
        ip.startswith(p) for p in private_prefixes
    )

    is_local_v6 = any(ip.lower().startswith(p) for p in ipv6_local_prefixes)

    if is_local_v4 or is_local_v6:

        # Local system testing
        print(f"[GEO] Local IP ({ip}) → Ranchi, India", flush=True)

        return {
            "country": "India",
            "city": "Ranchi",
            "latitude": 23.3441,
            "longitude": 85.3096,
        }

    else:

        # Real attacker IP location
        try:
            res = requests.get(
                f"{Config.GEO_API_URL}{ip}",
                timeout=Config.GEO_API_TIMEOUT
            )

            data = res.json()

            print(f"[GEO API RESPONSE] {data}", flush=True)

            if data.get("status") == "success":

                print(
                    f"[GEO] Attacker {ip} → "
                    f"{data.get('city')}, "
                    f"{data.get('country')}",
                    flush=True
                )

                return {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "latitude": data.get("lat", 0.0),
                    "longitude": data.get("lon", 0.0),
                }

        except Exception as e:
            print(f"[GEO] Error: {e}", flush=True)

        return {
            "country": "Unknown",
            "city": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0,
        }