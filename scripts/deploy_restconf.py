import json
import os
import sys
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
GITHUB_RAW_BASE = os.getenv("GITHUB_RAW_BASE")

BASE_URL = f"https://{DEVICE_HOST}/restconf/data"

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

TASKS = [
    {
        "name": "Hostname configureren",
        "github_file": "hostname.json",
        "method": "PATCH",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native"
    },
    {
        "name": "Loopback100 configureren",
        "github_file": "loopback100.json",
        "method": "PUT",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/interface/Loopback=100"
    },
    {
        "name": "Loopback101 configureren",
        "github_file": "loopback101.json",
        "method": "PUT",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/interface/Loopback=101"
    },
    {
        "name": "Banner MOTD configureren",
        "github_file": "banner.json",
        "method": "PATCH",
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native"
    }
]


def check_env():
    missing = []

    if not DEVICE_HOST:
        missing.append("DEVICE_HOST")
    if not DEVICE_USER:
        missing.append("DEVICE_USER")
    if not DEVICE_PASS:
        missing.append("DEVICE_PASS")
    if not GITHUB_RAW_BASE:
        missing.append("GITHUB_RAW_BASE")

    if missing:
        print("ERROR: Deze variabelen ontbreken in .env:")
        for item in missing:
            print(f"- {item}")
        sys.exit(1)


def fetch_json_from_github(filename):
    github_url = f"{GITHUB_RAW_BASE}/{filename}"
    print(f"\n[GitHub] Ophalen: {github_url}")

    response = requests.get(github_url, timeout=10)
    print(f"[GitHub] HTTP statuscode: {response.status_code}")

    if response.status_code != 200:
        raise RuntimeError(f"Kon {filename} niet ophalen uit GitHub.")

    data = response.json()
    print("[GitHub] JSON payload:")
    pprint(data)

    return data


def send_restconf_request(task, payload):
    print(f"\n[RESTCONF] Taak: {task['name']}")
    print(f"[RESTCONF] Methode: {task['method']}")
    print(f"[RESTCONF] URL: {task['url']}")

    response = requests.request(
        method=task["method"],
        url=task["url"],
        auth=HTTPBasicAuth(DEVICE_USER, DEVICE_PASS),
        headers=HEADERS,
        data=json.dumps(payload),
        verify=False,
        timeout=15
    )

    print(f"[RESTCONF] HTTP statuscode: {response.status_code}")

    if response.text:
        print("[RESTCONF] Response body:")
        try:
            pprint(response.json())
        except ValueError:
            print(response.text)

    if response.status_code in [200, 201, 204]:
        print("[OK] Configuratie succesvol toegepast.")
    else:
        raise RuntimeError(
            f"RESTCONF fout bij '{task['name']}' met statuscode {response.status_code}"
        )


def main():
    check_env()

    print("=== Network as Code RESTCONF Deployment ===")
    print(f"Device: {DEVICE_HOST}")

    for task in TASKS:
        try:
            payload = fetch_json_from_github(task["github_file"])
            send_restconf_request(task, payload)
        except Exception as error:
            print(f"\n[ERROR] {error}")
            print("Deployment gestopt om verdere fouten te vermijden.")
            sys.exit(1)

    print("\n=== Deployment volledig afgerond ===")


if __name__ == "__main__":
    main()