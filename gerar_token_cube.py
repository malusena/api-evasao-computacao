"""Gera um token para chamar a API REST do Cube.

Uso:
    python gerar_token_cube.py          # token valido por 30 dias
    python gerar_token_cube.py 365      # valido por 365 dias
"""
import base64
import hashlib
import hmac
import json
import os
import sys
import time

from dotenv import load_dotenv


def b64(dados):
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode()


def gerar_token(segredo, dias=30):
    cabecalho = {"alg": "HS256", "typ": "JWT"}
    corpo = {"iat": int(time.time()), "exp": int(time.time()) + dias * 86400}
    parte = b64(json.dumps(cabecalho).encode()) + "." + b64(json.dumps(corpo).encode())
    assinatura = hmac.new(segredo.encode(), parte.encode(), hashlib.sha256).digest()
    return parte + "." + b64(assinatura)


if __name__ == "__main__":
    load_dotenv()
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(gerar_token(os.environ["CUBEJS_API_SECRET"], dias))
