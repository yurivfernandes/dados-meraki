import json
import os
import re

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
    def gerar_planilha_wan(dados_planilha, caminho_arquivo="devices_wan.xlsx"):
        """
        Gera uma planilha Excel com as colunas Serial, Wan 1, Wan 2, Wan 3.
        """
        if not dados_planilha:
            print("Nenhum dado encontrado para gerar a planilha.")
            return
        df = pd.DataFrame(dados_planilha)
        df.to_excel(caminho_arquivo, index=False)
        print(
            f"Planilha '{caminho_arquivo}' gerada com sucesso no diretório raiz do projeto."
        )

    @staticmethod
    def extract_wan_ids_from_notes(notes: str) -> dict:
        """
        Extrai identificadores dos seguintes padrões do campo notes:
        - BN_XXXXXXX (BN_ + 7 números)
        - BLXXXXXXXXXXXXX (BL + 13 números)
        - SPO-XXXXXXXXX-XX (SPO-10 caracteres-3 caracteres)
        - ICCID com 20 dígitos (apenas os 20 dígitos após ICCID)
        - ARQ/IP/XXXXX (5 números após ARQ/IP/)
        - CAS/IP/XXXXX (5 números após CAS/IP/)
        - XXX/XXXXXXXX-X (3 números / 8 números - 1 número)
        - 7 dígitos inteiros (apenas se não fizer parte dos padrões acima)
        Retorna um dicionário: {"Wan 1": valor, ...}
        """

        ids = []
        # 1. BN_XXXXXXX
        ids += re.findall(r"BN_\d{7}", notes)
        # 2. BLXXXXXXXXXXXXX
        ids += re.findall(r"BL\d{13}", notes)
        # 3. SPO-XXXXXXXXX-XX
        ids += re.findall(r"SPO-[A-Za-z0-9]{10}-[A-Za-z0-9]{3}", notes)
        # 4. ICCID com 20 dígitos (apenas os 20 dígitos após ICCID)
        iccid_matches = re.findall(r"ICCID\s*=*\s*(\d{20})", notes)
        ids += iccid_matches
        # 5. ARQ/IP/XXXXX (5 números após ARQ/IP/)
        ids += re.findall(r"ARQ/IP/\d{5}", notes)
        # 6. CAS/IP/XXXXX (5 números após CAS/IP/)
        ids += re.findall(r"CAS/IP/\d{5}", notes)
        # 7. XXX/XXXXXXXX-X (3 números / 8 números - 1 número)
        ids += re.findall(r"\d{3}/\d{8}-\d", notes)
        # 8. 7 dígitos inteiros (apenas se não fizer parte dos padrões acima)
        ids += [
            m
            for m in re.findall(r"(?<!\d)(\d{7})(?!\d)", notes)
            if f"BN_{m}" not in ids
        ]
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
            resultado = meraki.get_devices(modelo)
            if isinstance(resultado, list):
                for device in resultado:
                    serial = device.get("serial", "")
                    notes = device.get("notes", "")
                    wan1ip = device.get("wan1Ip", "")
                    wan2ip = device.get("wan2Ip", "")
                    wan3ip = device.get("wan3Ip", "")
                    wans = MerakiAPI.extract_wan_ids_from_notes(notes)
                    linha = {
                        "Serial": serial,
                        "wan1Ip": wan1ip,
                        "wan2Ip": wan2ip,
                        "wan3Ip": wan3ip,
                    }
                    for i in range(1, 4):
                        linha[f"Wan {i}"] = wans.get(f"Wan {i}", "")
                    dados_planilha.append(linha)
    MerakiAPI.gerar_planilha_wan(dados_planilha)
