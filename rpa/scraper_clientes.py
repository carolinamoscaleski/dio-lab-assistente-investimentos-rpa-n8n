"""
RPA - Extração de Clientes
--------------------------
Etapa de RPA do projeto "Criando um Processo de RPA com N8N e Python" (DIO).

Lê a página HTML simulada de clientes (docs/index.html, hospedada no GitHub Pages
ou servida localmente), extrai nome/email/saldo/perfil de cada cliente com
BeautifulSoup e envia cada registro para o Webhook do n8n, que dispara o
restante do fluxo (cruzamento com investimentos + geração de mensagem + Gmail).

Uso:
    python scraper_clientes.py --source docs/index.html --webhook https://SEU-N8N/webhook/clientes

    Requisitos:
        pip install beautifulsoup4 requests
        """

import argparse
import json
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extrair_clientes(html_path: str) -> list[dict]:
      html = Path(html_path).read_text(encoding="utf-8")
      soup = BeautifulSoup(html, "html.parser")

    tabela = soup.find("table", id="clientes")
    if tabela is None:
              raise ValueError("Tabela de clientes não encontrada no HTML.")

    clientes = []
    for linha in tabela.find("tbody").find_all("tr"):
              celulas = linha.find_all("td")
              cliente = {
                  "nome": celulas[0].get_text(strip=True),
                  "email": celulas[1].get_text(strip=True),
                  "saldo": celulas[2].get_text(strip=True),
                  "perfil": celulas[3].get_text(strip=True),
              }
              clientes.append(cliente)
          return clientes


def enviar_para_n8n(cliente: dict, webhook_url: str) -> requests.Response:
      return requests.post(webhook_url, json=cliente, timeout=15)


def main():
      parser = argparse.ArgumentParser(description="RPA de extração e envio de clientes para o n8n.")
      parser.add_argument("--source", default="docs/index.html", help="Caminho do HTML de clientes.")
      parser.add_argument("--webhook", required=True, help="URL do webhook do n8n.")
      parser.add_argument("--dry-run", action="store_true", help="Só imprime os clientes, não envia.")
      args = parser.parse_args()

    clientes = extrair_clientes(args.source)
    print(f"[RPA] {len(clientes)} clientes extraídos de {args.source}")

    for cliente in clientes:
              print(f"  -> {cliente['nome']} | {cliente['perfil']} | {cliente['saldo']}")

        if args.dry_run:
                      continue

        try:
                      resp = enviar_para_n8n(cliente, args.webhook)
                      resp.raise_for_status()
                      print(f"     enviado com sucesso (status {resp.status_code})")
except requests.RequestException as exc:
              print(f"     [ERRO] falha ao enviar cliente {cliente['email']}: {exc}", file=sys.stderr)

        time.sleep(0.5)

    if args.dry_run:
              print(json.dumps(clientes, ensure_ascii=False, indent=2))


if __name__ == "__main__":
      main()
  
