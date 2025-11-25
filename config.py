"""Módulo de configuración de la API distribuida.

Proporciona lectura de variables de entorno y parsing de la lista de participantes
que intervienen en las transacciones 2PC.

Formato esperado en BANK_PARTICIPANTS:
  "nombre|url|rol,nombre|url|rol,..." donde rol ∈ {debit, credit, mirror}.
"""

import os
import json
from pathlib import Path
from functools import lru_cache
from typing import List, Dict
from dotenv import load_dotenv

# parse_participants: Convierte la cadena cruda de participantes en una lista
# de diccionarios con nombre, url y rol.
def parse_participants(raw: str) -> List[Dict[str, str]]:
    participants: List[Dict[str, str]] = []
    if not raw:
        return participants
    for item in raw.split(','):
        parts = item.split('|')
        if len(parts) >= 3:
            participants.append({
                'name': parts[0].strip(),
                'url': parts[1].strip(),
                'role': parts[2].strip()
            })
    return participants

def load_participants_from_file(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        result: List[Dict[str, str]] = []
        for item in data:
            if all(k in item for k in ('name', 'url', 'role')):
                result.append({
                    'name': str(item['name']).strip(),
                    'url': str(item['url']).strip(),
                    'role': str(item['role']).strip(),
                })
        return result
    except Exception:
        return []

# get_settings: Devuelve (cacheado) la instancia única de Settings.
@lru_cache
def get_settings():
    return Settings()

class Settings:
    """Agrupa todos los parámetros de configuración usados en la aplicación.

    Se inicializa leyendo variables de entorno. Incluye timeouts, reintentos
    y lista de participantes para 2PC.
    """
    def __init__(self):
        # Cargar .env local (aislado al directorio del módulo)
        base_dir = Path(__file__).resolve().parent
        load_dotenv(base_dir / '.env')

        # Base de datos: usar ruta absoluta local controlada para evitar crear el archivo fuera del proyecto.
        default_db_path = base_dir / 'transactions.db'
        self.database_url = os.getenv('TX_DB_URL', f"sqlite:///{default_db_path}")
        self.jwt_secret = os.getenv('JWT_SECRET', 'dev-secret-change')
        self.jwt_algorithm = os.getenv('JWT_ALG', 'HS256')
        self.jwt_exp_minutes = int(os.getenv('JWT_EXP_MIN', '60'))
        raw_participants = os.getenv('BANK_PARTICIPANTS', '')

        participants = parse_participants(raw_participants)
        if not participants:
            # Intentar cargar archivo JSON local si no hay env var.
            participants = load_participants_from_file(base_dir / 'participants.json')
        if not participants:
            # Fallback: intentar hostnames internos Docker, luego localhost.
            docker_candidates = [
                {'name': 'bank_a', 'url': 'http://bank_a_api:8000', 'role': 'debit'},
                {'name': 'bank_b', 'url': 'http://bank_b_api:8000', 'role': 'credit'}
            ]
            local_candidates = [
                {'name': 'bank_a', 'url': 'http://localhost:8001', 'role': 'debit'},
                {'name': 'bank_b', 'url': 'http://localhost:8002', 'role': 'credit'}
            ]
            # Seleccionar lista según variable de entorno DOCKER_ENV (marcar 'docker' para usar hostnames internos).
            mode = os.getenv('ENV_MODE', '').lower()
            participants = docker_candidates if mode == 'docker' else local_candidates
        self.participants = participants
        # Parámetros de red
        self.request_timeout = float(os.getenv('REQUEST_TIMEOUT', '3'))
        self.max_retries = int(os.getenv('REQUEST_RETRIES', '2'))
        self.reconcile_interval = int(os.getenv('RECONCILE_INTERVAL_SEC', '60'))
