import os
from pprint import pprint

import requests
import urllib3
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings()
load_dotenv()

DEVICE_HOST = os.getenv("DEVICE_HOST")
DEVICE_USER = os.getenv("DEVICE_USER")
DEVICE_PASS = os.getenv("DEVICE_PASS")

BASE_URL = f"https://{DEVICE_HOST}/restconf/data"

HEADERS = {
    "Accept": "application/yang-data+json"
}

CHECKS = [
    {
        "name": "Hostname controleren",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/hostname"
    },
    {
        "name": "Loopback100 controleren",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/interface/Loopback=100"
    },
    {
        "name": "Loopback101 controleren",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/interface/Loopback=101"
    },
    {
        "name": "Banner controleren",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/banner"
    }
]


def get_data(check):
    print(f"\n[VALIDATIE] {check['name']}")
    print(f"[RESTCONF] GET {check['url']}")

    response = requests.get(
        check["url"],
        auth=HTTPBasicAuth(DEVICE_USER, DEVICE_PASS),
        headers=HEADERS,
        verify=False,
        timeout=15
    )

    print(f"[RESTCONF] HTTP statuscode: {response.status_code}")

    if response.status_code == 200:
        print("[OK] Data succesvol opgehaald:")
        pprint(response.json())
    else:
        print("[FOUT] Validatie mislukt")
        print(response.text)


def main():
    print("=== Network as Code RESTCONF Validatie ===")
    print(f"Device: {DEVICE_HOST}")

    for check in CHECKS:
        get_data(check)

    print("\n=== Validatie afgerond ===")


if __name__ == "__main__":
    main()