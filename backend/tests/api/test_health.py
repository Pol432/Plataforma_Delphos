"""
Healthcheck de infraestructura.

El HEALTHCHECK del Dockerfile hace `curl -f http://localhost:8000/health`. La
ruta no existía (solo estaba `/`), así que devolvía 404 y en la demo hubo que
usar `/` como sustituto. Este test existe para que no vuelva a desaparecer sin
que nadie se entere.
"""


def test_health_responde_200(client):
    response = client.get("/health")

    assert response.status_code == 200


def test_health_reporta_estado_y_version(client):
    body = client.get("/health").json()

    assert body["status"] == "ok"
    # La versión sale de `FastAPI(version=...)`, no de una constante aparte:
    # si se sube la versión de la app, este test no hay que tocarlo.
    assert body["version"]
    assert body["service"]


def test_health_no_depende_de_la_base_de_datos(client):
    """Es una sonda de liveness, no de readiness.

    Si comprobara la DB, una caída de PostgreSQL marcaría el contenedor como
    unhealthy y Docker lo reiniciaría en bucle sin que el fallo esté en la API.
    Se verifica sin overrides de sesión activos más allá de los del fixture.
    """
    from app.main import app

    ruta = next(r for r in app.routes if getattr(r, "path", None) == "/health")

    assert ruta.dependant.dependencies == []
