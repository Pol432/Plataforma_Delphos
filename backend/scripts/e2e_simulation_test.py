import json
import os
import sys
from typing import Dict, Any

import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    session = requests.Session()
    email = "demo_e2e@test.com"
    password = "DemoE2E123!"
    username = "demo_e2e"

    print_section("1. Register user")
    register_payload = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Demo E2E User",
        "phone": "0999999999",
    }
    register_resp = session.post(f"{BASE_URL}/api/v1/register", json=register_payload)
    if register_resp.status_code == 400 and "already registered" in register_resp.text.lower():
        print("User already exists; continuing with login flow.")
    else:
        print(f"Register status: {register_resp.status_code}")
        print(register_resp.text)

    print_section("2. Login and obtain token")
    form_data = {
        "username": username,
        "password": password,
    }
    token_resp = session.post(f"{BASE_URL}/api/v1/token", data=form_data)
    print(f"Token status: {token_resp.status_code}")
    print(token_resp.text)
    token = token_resp.json().get("access_token")
    if not token:
        raise RuntimeError("No access token returned")
    session.headers.update({"Authorization": f"Bearer {token}"})

    print_section("3. List simulations")
    catalog_resp = session.get(f"{BASE_URL}/api/v1/simulaciones")
    print(f"Catalog status: {catalog_resp.status_code}")
    sims = catalog_resp.json()
    skywork = next((sim for sim in sims if sim.get("title", "").startswith("Ingeniería de Datos")), None)
    if not skywork:
        raise RuntimeError("Skywork simulation not found")
    sim_id = skywork["id"]
    print(f"Selected simulation: {sim_id} - {skywork['title']}")

    task_id = None
    for sim in sims:
        if sim.get("id") == sim_id:
            task_id = 1
            break
    if task_id is None:
        raise RuntimeError("No task id available")

    print_section("4. Submit a high-quality answer")
    submit_payload = {
        "respuesta_texto": """
        Para abordar este problema de ingesta, propongo una arquitectura basada en un pipeline productor-consumidor con workers de normalización y persistencia. En Python usaría asyncio o ThreadPoolExecutor para paralelizar la deserialización y validación de payloads JSON, y aplicaría backoff exponencial con reintentos para evitar saturar PostgreSQL. La ingesta se dividiría en lotes con SQLAlchemy y psycopg2, usando insert_many de forma transaccional para reducir overhead. También añadí checks de integridad por checksum y partición por fecha para mantener latencia p95 bajo control.
        """
    }
    submit_resp = session.post(
        f"{BASE_URL}/api/v1/simulaciones/{sim_id}/tasks/{task_id}/submit",
        json=submit_payload,
    )
    print(f"Submit status: {submit_resp.status_code}")
    print(json.dumps(submit_resp.json(), indent=2, ensure_ascii=False))

    print_section("5. Finish simulation")
    finish_payload = {
        "skills": ["python", "sql", "data_engineering", "analytics"],
        "field_of_study": "Computer Science",
        "analytical_score": 88,
        "creative_score": 74,
        "social_score": 60,
        "linguistic_score": 72,
        "hands_on_score": 91,
    }
    finish_resp = session.post(f"{BASE_URL}/api/v1/simulaciones/{sim_id}/finish", json=finish_payload)
    print(f"Finish status: {finish_resp.status_code}")
    print(json.dumps(finish_resp.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
