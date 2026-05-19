import os
import requests
import urllib3
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings()
load_dotenv()

router_ip = os.getenv("DEVICE_HOST")
username = os.getenv("DEVICE_USER")
password = os.getenv("DEVICE_PASS")

url = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-native:native/hostname"

headers = {
    "Accept": "application/yang-data+json"
}

try:
    response = requests.get(
        url,
        headers=headers,
        auth=HTTPBasicAuth(username, password),
        verify=False,
        timeout=30
    )

    print(f"HTTP Status Code: {response.status_code}")

    if response.status_code == 200:
        print("RESTCONF connectie werkt!")
        print(response.text[:500])

    elif response.status_code == 401:
        print("Login fout: username/password klopt niet.")

    else:
        print("RESTCONF bereikbaar, maar response is niet OK.")
        print(response.text)

except Exception as e:
    print("Connectie mislukt:")
    print(e)