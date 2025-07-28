# dados-meraki

Este projeto facilita a extração de informações de dispositivos Meraki e a geração de planilhas Excel com dados relevantes de WAN.

## Estrutura dos Arquivos

- **devices_meraki.py**: Script principal para extração dos dados dos dispositivos Meraki, filtrando por modelo, extraindo informações de WAN a partir das notas e gerando uma planilha Excel. Inclui uma função para desabilitar a verificação SSL do requests (apenas para desenvolvimento).

- **devices.py**: (Descreva aqui o propósito do arquivo caso ele seja utilizado. Exemplo: Script auxiliar para manipulação ou análise adicional dos dados extraídos. Caso não esteja em uso, pode ser ignorado.)

## Como usar

1. Crie um arquivo `.env` na raiz do projeto com sua chave de API:
	```
	API_KEY=seu_api_key_aqui
	```

2. Instale as dependências:
	```bash
	pip install -r requirements.txt
	```

3. Execute o script principal:
	```bash
	python devices_meraki.py
	```

4. Será gerado um arquivo `devices_wan.xlsx` com as colunas Serial, wan1Ip, wan2Ip, wan3Ip, Wan 1, Wan 2, Wan 3.

## Observações

- O método `patch_requests_ssl()` desabilita a verificação SSL globalmente para o pacote requests, útil para ambientes de desenvolvimento com certificados autoassinados.
- O script busca dispositivos dos modelos MX67 e MX68, mas pode ser facilmente adaptado para outros modelos.


# dados-meraki

<p align="center">
	<img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
	<img src="https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white" alt="Pandas">
	<img src="https://img.shields.io/badge/requests-%2300ACD7.svg?style=flat&logo=python&logoColor=white" alt="Requests">
	<img src="https://img.shields.io/badge/dotenv-%2332CD32.svg?style=flat&logo=python&logoColor=white" alt="Dotenv">
	<img src="https://img.shields.io/badge/Cisco%20Meraki-API-green?logo=cisco" alt="Cisco Meraki API">
</p>

<p align="center">
	<b>Extraia informações de dispositivos Cisco Meraki e gere planilhas de forma simples e automatizada!</b>
</p>

---

## ✨ O que o projeto faz?

- Consulta a API da Cisco Meraki para buscar dispositivos dos modelos <b>MX67</b> e <b>MX68</b>.
- Para cada dispositivo, extrai o número de série (<code>serial</code>) e, a partir do campo <code>notes</code>, identifica diversos padrões de identificadores de WAN.
- Gera uma planilha <b>devices_wan.xlsx</b> no diretório raiz do projeto, contendo as colunas:
	- Serial
	- Wan 1
	- Wan 2
	- Wan 3

## 🛠 Tecnologias Utilizadas

- Python 3.8+
- pandas
- requests
- python-dotenv

## ⚡ Pré-requisitos

- Conta Cisco Meraki com permissão de acesso à API
- Chave de API da Cisco Meraki

## 🚀 Instalação

1. Clone este repositório:

	 ```bash
	 git clone <url-do-repositorio>
	 cd dados-meraki
	 ```

2. Crie um ambiente virtual (opcional, mas recomendado):

	 ```bash
	 python3 -m venv .venv
	 source .venv/bin/activate
	 ```

3. Instale as dependências:

	 ```bash
	 pip install -r requirements.txt
	 ```

4. Crie um arquivo <code>.env</code> na raiz do projeto e adicione sua chave de API:

	 ```
	 API_KEY=suachaveaqui
	 ```

## ▶️ Como rodar o projeto

Execute o script principal:

```bash
python devices.py
```

O script irá:
- Buscar os dispositivos dos modelos MX67 e MX68.
- Gerar a planilha <b>devices_wan.xlsx</b> com os dados extraídos.

## 🔎 Observações
- O campo <code>notes</code> de cada dispositivo é analisado para encontrar:
	- Sequências de 7 dígitos inteiros
	- BN_XXXXXXX (BN_ + 7 números)
	- BLXXXXXXXXXXXXX (BL + 13 números)
	- SPO-XXXXXXXXX-XX (SPO-10 caracteres-3 caracteres)
	- ICCID com 20 dígitos (apenas os 20 dígitos após ICCID)
	- ARQ/IP/XXXXX (5 números após ARQ/IP/)
	- CAS/IP/XXXXX (5 números após CAS/IP/)
	- XXX/XXXXXXXX-X (3 números / 8 números - 1 número)
- Caso não haja identificadores suficientes, as colunas correspondentes ficarão vazias.
- O script ignora outros números que não estejam nos padrões acima.

---

<p align="center">
	<b>Licença</b><br>
	MIT
</p>
