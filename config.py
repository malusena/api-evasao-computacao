import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


# le as variaveis do arquivo .env (ver .env.example)
load_dotenv()


def criar_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        url = "postgresql://{}:{}@{}:{}/{}".format(
            os.getenv("POSTGRES_USER", "postgres"),
            os.environ["POSTGRES_PASSWORD"],
            os.getenv("POSTGRES_HOST", "localhost"),
            os.getenv("POSTGRES_PORT", "5433"),
            os.getenv("POSTGRES_DB", "pesquisa_evasao"),
        )
    return create_engine(url)
