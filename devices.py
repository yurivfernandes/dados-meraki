import json
import os

import pandas as pd
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
headers = {
    "X-Cisco-Meraki-API-Key": os.getenv("API_KEY"),
    "Accept": "application/json",
}


class MerakiAPI:
    @staticmethod
    def extract_wan_ids_from_notes(notes: str) -> dict:
        """
        Extrai identificadores de 7 dígitos inteiros do campo notes.
        Retorna um dicionário: {"Wan 1": "1836542", ...}
        """
        import re

        ids = re.findall(r"(?<!\d)(\d{7})(?!\d)", notes)
        return {f"Wan {i + 1}": wan_id for i, wan_id in enumerate(ids)}

    def __init__(self, api_key: str):
        self.headers = {
            "X-Cisco-Meraki-API-Key": api_key,
            "Accept": "application/json",
        }

    def get_organization_id(self) -> str:
        """Retorna o organization id"""
        resp_orgs = requests.get(
            "https://api.meraki.com/api/v1/organizations",
            headers=self.headers,
            verify=False,
        )
        orgs = resp_orgs.json()
        return orgs[0]["id"]

    def get_devices(self, model: str) -> dict:
        """Retorna os dados dos Devices"""
        org_id = self.get_organization_id()
        devices = requests.get(
            f"https://api.meraki.com/api/v1/organizations/{org_id}/devices/?model={model}",
            headers=self.headers,
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


if __name__ == "__main__":
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("API_KEY não encontrada no .env")
    else:
        meraki = MerakiAPI(api_key)
        modelos = ["MX67", "MX68"]
        dados_planilha = []
        for modelo in modelos:
            print(f"\nDispositivos para o modelo {modelo}:")
            resultado = meraki.get_devices(modelo)
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            if isinstance(resultado, list):
                for device in resultado:
                    serial = device.get("serial", "")
                    notes = device.get("notes", "")
                    wans = MerakiAPI.extract_wan_ids_from_notes(notes)
                    linha = {"Serial": serial}
                    # Adiciona Wan 1, Wan 2, Wan 3 (ou vazio se não houver)
                    for i in range(1, 4):
                        linha[f"Wan {i}"] = wans.get(f"Wan {i}", "")
                    dados_planilha.append(linha)
        # Gerar planilha se houver dados
        if dados_planilha:
            df = pd.DataFrame(dados_planilha)
            df.to_excel("devices_wan.xlsx", index=False)
            print(
                "Planilha 'devices_wan.xlsx' gerada com sucesso no diretório raiz do projeto."
            )
        else:
            print("Nenhum dado encontrado para gerar a planilha.")
