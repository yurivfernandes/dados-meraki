import os

import meraki
import pandas as pd
from dotenv import load_dotenv

from patch_requests_ssl import patch_requests_ssl

load_dotenv()


class MerakiAPI:
    def marcar_devices_migrados(self, devices, migrados_path):
        if not os.path.exists(migrados_path):
            print(
                f"Arquivo migrados.xlsx não encontrado na raiz do projeto: {migrados_path}"
            )
            for device in devices:
                device["migrados"] = "Não"
            return devices
        df_migrados = pd.read_excel(migrados_path)
        df_migrados.columns = [
            col.strip().upper() for col in df_migrados.columns
        ]
        siglas_restaurantes = set(
            [
                f"MCD_{sigla.upper().strip()}"
                for sigla in df_migrados[
                    df_migrados["TIPO 2"].str.upper() == "RESTAURANTE"
                ]["SIGLA"]
                if pd.notna(sigla)
            ]
        )
        if "SIGLA REVISTA" in df_migrados.columns:
            siglas_quiosques = set(
                [
                    f"MCD_{sigla_revista.upper().strip()}"
                    for sigla_revista in df_migrados[
                        df_migrados["TIPO 2"].str.upper() == "QUIOSQUE"
                    ]["SIGLA REVISTA"]
                    if pd.notna(sigla_revista)
                ]
            )
        else:
            siglas_quiosques = set()

        devices["sigla_match"] = devices["name"].apply(
            self._extrair_sigla_match
        )
        devices["migrados"] = devices["sigla_match"].apply(
            lambda sigla: self._is_migrado_sigla(
                sigla, siglas_restaurantes, siglas_quiosques
            )
        )
        devices = devices.drop(columns=["sigla_match"])
        return devices.to_dict(orient="records")

    def _extrair_sigla_match(self, name):
        if not isinstance(name, str):
            return ""
        name = name.upper().strip()
        if name.startswith("MCD_"):
            partes = name.split("_")
            if len(partes) >= 3 and partes[2].startswith("KSK"):  # Quiosque
                return "_".join(partes[:3])
            elif len(partes) >= 2:  # Restaurante
                return "_".join(partes[:2])
        return ""

    def _is_migrado_sigla(
        self, sigla_match, siglas_restaurantes, siglas_quiosques
    ):
        if (
            sigla_match in siglas_restaurantes
            or sigla_match in siglas_quiosques
        ):
            return "Sim"
        return "Não"

    def _is_migrado(self, name, siglas_restaurantes, siglas_quiosques):
        for sigla in siglas_restaurantes:
            if name.startswith(f"MCD_{sigla}_") or name == f"MCD_{sigla}":
                return "Sim"
        for sigla_ksk in siglas_quiosques:
            if name.startswith(f"MCD_{sigla_ksk}"):
                return "Sim"
        return "Não"

    def __init__(self, api_key: str):
        self.dashboard = meraki.DashboardAPI(
            api_key, suppress_logging=True, certificate_path=""
        )

    def get_organizations(self) -> list:
        return self.dashboard.organizations.getOrganizations()

    def get_all_devices(self, org_id: str) -> list:
        """Busca todos os dispositivos de uma organização, paginando se necessário."""
        all_devices = []
        starting_after = None
        while True:
            params = {"perPage": 1000}
            if starting_after:
                params["startingAfter"] = starting_after
            resp = self.dashboard.organizations.getOrganizationDevices(
                org_id, **params
            )
            if not resp:
                break
            all_devices.extend(resp)
            if len(resp) < params["perPage"]:
                break
            starting_after = resp[-1]["serial"]
        return all_devices


if __name__ == "__main__":
    patch_requests_ssl()
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("API_KEY não encontrada no .env")
    else:
        meraki_api = MerakiAPI(api_key)
        all_devices = []
        orgs = meraki_api.get_organizations()
        for org in orgs:
            org_id = org.get("id")
            devices = meraki_api.get_all_devices(org_id)
            for device in devices:
                device["organizationId"] = org_id
                if isinstance(device.get("tags"), list):
                    device["tags"] = ", ".join(device["tags"])
                if isinstance(device.get("details"), list):
                    details_list = device["details"]
                    details_str = "; ".join(
                        f"{d.get('name', '')}: {d.get('value', '')}"
                        for d in details_list
                        if isinstance(d, dict)
                    )
                    device["details"] = details_str
                notes = device.get("notes")
                if isinstance(notes, str) and "\n\n" in notes:
                    notes_split = notes.split("\n\n")
                    for idx, note in enumerate(notes_split):
                        key = f"note.{idx + 1}"
                        device[key] = note
            all_devices.extend(devices)
        migrados_path = os.path.join(
            os.path.dirname(__file__), "migrados.xlsx"
        )
        all_devices = meraki_api.marcar_devices_migrados(
            all_devices, migrados_path
        )
        with pd.ExcelWriter("meraki_organizacoes_dispositivos.xlsx") as writer:
            pd.DataFrame(all_devices).to_excel(
                writer, sheet_name="Dispositivos", index=False
            )
        print(
            "Planilha 'meraki_organizacoes_dispositivos.xlsx' gerada com sucesso apenas com a aba Dispositivos."
        )
