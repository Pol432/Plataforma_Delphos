from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import os
import logging
import socket
from urllib.parse import urlparse

# URL de conexión a la base de datos (puede venir de .env)
# URL de conexión a la base de datos (puede venir de .env)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Si la URL apunta a la host 'db' (docker) pero no es resolvible desde este entorno,
# hacemos fallback a SQLite para permitir ejecutar la app localmente sin Docker.
def _resolve_db_url(url: str) -> str:
	try:
		parsed = urlparse(url)
		hostname = parsed.hostname
		if hostname in (None, 'localhost', '127.0.0.1'):
			return url
		# Only try resolve for network hosts
		try:
			socket.gethostbyname(hostname)
			return url
		except Exception:
			logging.warning("DB host '%s' not resolvable; falling back to local sqlite for development.", hostname)
			return 'sqlite:///./sql_app.db'
	except Exception:
		return url

resolved_url = _resolve_db_url(SQLALCHEMY_DATABASE_URL)

# Crear el engine
engine = create_engine(resolved_url, pool_pre_ping=True)

# Base para los modelos
Base = declarative_base()

# Import all models here to ensure they are registered on `Base.metadata`
# This avoids needing to import models in every consumer and makes
# `from app.db.base import Base` populate `Base.metadata.tables`.
try:
	import app.models  # noqa: F401
except Exception:
	# Import errors are handled by the caller; keep Base defined even if models fail to import
	pass

from app.models.university import University  # noqa
