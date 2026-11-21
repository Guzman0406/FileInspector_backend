"""Tests del módulo compare: la función pura (repository) y el
endpoint HTTP completo (router + service)."""
from app.modules.compare.repository import comparar_archivos
from tests.conftest import a_base64


# Tests de la función pura comparar_archivos

def test_comparar_archivos_identicos():
    resultado = comparar_archivos(b"mismo contenido", b"mismo contenido")

    assert resultado["identical"] is True
    assert resultado["total_differences"] == 0
    assert resultado["differences"] == []


def test_comparar_archivos_una_diferencia():
    resultado = comparar_archivos(b"Hola mundo", b"Hola mundx")

    assert resultado["identical"] is False
    assert resultado["total_differences"] == 1
    assert resultado["differences"] == [{"position": 9, "value_a": ord("o"), "value_b": ord("x")}]


def test_comparar_archivos_de_distinto_tamano_rellena_con_none():
    resultado = comparar_archivos(b"corto", b"largototal")

    assert resultado["size_a"] == 5
    assert resultado["size_b"] == 10
    assert resultado["identical"] is False
    # Las posiciones 5 a 9 solo existen en el archivo B
    extras = [d for d in resultado["differences"] if d["value_a"] is None]
    assert len(extras) == 5


def test_comparar_archivos_trunca_a_partir_del_limite():
    contenido_a = bytes(range(0, 50))
    contenido_b = bytes(range(50, 100))  # los 50 bytes son distintos uno a uno

    resultado = comparar_archivos(contenido_a, contenido_b)

    assert resultado["total_differences"] == 50
    assert resultado["truncated"] is True
    assert len(resultado["differences"]) == 20


# Tests del endpoint POST /api/v1/compare

def test_endpoint_compare_archivos_identicos(client):
    contenido = b"reporte final del proyecto"
    resp = client.post(
        "/api/v1/compare",
        json={
            "file_base64_a": a_base64(contenido),
            "filename_a": "a.txt",
            "file_base64_b": a_base64(contenido),
            "filename_b": "b.txt",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["identical"] is True
    assert body["data"]["total_differences"] == 0


def test_endpoint_compare_archivos_distintos(client):
    resp = client.post(
        "/api/v1/compare",
        json={
            "file_base64_a": a_base64(b"version uno"),
            "filename_a": "a.txt",
            "file_base64_b": a_base64(b"version dos"),
            "filename_b": "b.txt",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["identical"] is False
    assert body["data"]["total_differences"] > 0


def test_endpoint_compare_base64_invalido_en_cualquiera_de_los_dos(client):
    resp = client.post(
        "/api/v1/compare",
        json={
            "file_base64_a": "!!!no-valido!!!",
            "filename_a": "a.txt",
            "file_base64_b": a_base64(b"contenido valido"),
            "filename_b": "b.txt",
        },
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_BASE64"


def test_endpoint_compare_archivo_demasiado_grande(client):
    # max_size_comparator son 20MB; mandamos un base64 que ya estimado lo supera
    base64_gigante = "A" * (21 * 1024 * 1024 * 4 // 3)

    resp = client.post(
        "/api/v1/compare",
        json={
            "file_base64_a": base64_gigante,
            "filename_a": "a.bin",
            "file_base64_b": a_base64(b"chico"),
            "filename_b": "b.bin",
        },
    )

    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_endpoint_compare_campo_faltante_da_422(client):
    resp = client.post("/api/v1/compare", json={"filename_a": "a.txt", "filename_b": "b.txt"})

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
