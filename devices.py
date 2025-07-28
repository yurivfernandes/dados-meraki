import json
import os

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
headers = {
    "X-Cisco-Meraki-API-Key": os.getenv("API_KEY"),
    "Accept": "application/json",
}


@property
def organization_id(self) -> str:
    """Retorna o organization id"""
    resp_orgs = requests.get(
        "https://api.meraki.com/api/v1/organizations",
        headers=headers,
        verify=False,
    )
    orgs = resp_orgs.json()
    return orgs[0]["id"]


def get_devices(self, model: str) -> dict:
    """Retorna os dados dos Devices"""
    devices = requests.get(
        f"https://api.meraki.com/api/v1/organizations/{self.organization_id}/devices/?model={model}",
        headers=headers,
        verify=False,
    )

    if devices.status_code == 200:
        try:
            dados_json = json.loads(devices.text)
            return dados_json
        except json.JSONDecodeError:
            print("Erro: o campo 'text' não contém um JSON válido.")
    else:
        print(f"Erro na requisição: {devices.status_code}")
