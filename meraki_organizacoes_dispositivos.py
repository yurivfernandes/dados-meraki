import os

import meraki
import pandas as pd
from dotenv import load_dotenv

from patch_requests_ssl import patch_requests_ssl

load_dotenv()


class MerakiAPI:
    def __init__(self, api_key: str):
        self.dashboard = meraki.DashboardAPI(
            api_key, suppress_logging=True, certificate_path=""
        )

    def get_organizations(self) -> list:
        return self.dashboard.organizations.getOrganizations()

    def get_all_devices(self, org_id: str) -> list:
        return self.dashboard.organizations.getOrganizationDevices(org_id)


if __name__ == "__main__":
    patch_requests_ssl()
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("API_KEY não encontrada no .env")
    else:
        meraki_api = MerakiAPI(api_key)
        orgs = meraki_api.get_organizations()
        if not orgs:
            print("Nenhuma organização encontrada.")
        else:
            all_devices = []
            for org in orgs:
                org_id = org.get("id")
                devices = meraki_api.get_all_devices(org_id)
                for device in devices:
                    device["organizationId"] = org_id
                all_devices.extend(devices)
            # Criar o Excel com duas abas
            with pd.ExcelWriter(
                "meraki_organizacoes_dispositivos.xlsx"
            ) as writer:
                pd.DataFrame(orgs).to_excel(
                    writer, sheet_name="Organizacoes", index=False
                )
                pd.DataFrame(all_devices).to_excel(
                    writer, sheet_name="Dispositivos", index=False
                )
            print(
                "Planilha 'meraki_organizacoes_dispositivos.xlsx' gerada com sucesso com duas abas: Organizacoes e Dispositivos."
            )
