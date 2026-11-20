"""Tests del módulo hash."""
import hashlib

from app.modules.hash.repository import calcular_hashes
from tests.conftest import a_base64


#  Tests de la función pura calcular_hashes 

def test_calcular_hashes_coincide_con_hashlib_directo():
    contenido = b"Hola FileInspector, esta es una prueba de hash."

    resultado = calcular_hashes(contenido)

    assert resultado["md5"] == hashlib.md5(contenido).hexdigest()
    assert resultado["sha1"] == hashlib.sha1(contenido).hexdigest()
    assert resultado["sha256"] == hashlib.sha256(contenido).hexdigest()
    assert resultado["sha512"] == hashlib.sha512(contenido).hexdigest()


def test_calcular_hashes_archivo_vacio_no_truena():
    resultado = calcular_hashes(b"")

    # Los hashes de "nada" son valores conocidos y fijos
    assert resultado["sha256"] == hashlib.sha256(b"").hexdigest()


def test_calcular_hashes_cambia_si_cambia_un_byte():
    resultado_a = calcular_hashes(b"contenido original")
    resultado_b = calcular_hashes(b"contenido original!")  
    assert resultado_a["sha256"] != resultado_b["sha256"]


#  Tests del endpoint POST /api/v1/hash 

def test_endpoint_hash_devuelve_los_4_algoritmos(client):
    contenido = b"archivo de prueba para el endpoint"
    resp = client.post(
        "/api/v1/hash",
        json={"file_base64": a_base64(contenido), "filename": "prueba.txt"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["file_size_bytes"] == len(contenido)
    assert body["data"]["hashes"]["sha256"] == hashlib.sha256(contenido).hexdigest()
    assert "MD5" in body["data"]["weak_algorithms_warning"] or "md5" in body["data"]["weak_algorithms_warning"].lower()


def test_endpoint_hash_acepta_cualquier_tipo_de_archivo(client):
    # A diferencia de exif, hash no debe rechazar archivos que no son imágenes
    resp = client.post(
        "/api/v1/hash",
        json={"file_base64": a_base64(b"contenido binario cualquiera"), "filename": "datos.bin"},
    )

    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_endpoint_hash_base64_invalido(client):
    resp = client.post(
        "/api/v1/hash",
        json={"file_base64": "!!!no-valido!!!", "filename": "x.bin"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_BASE64"


def test_endpoint_hash_archivo_demasiado_grande(client):
    # max_size_hash son 50MB; mandamos un base64 que ya estimado supera eso
    base64_gigante = "A" * (51 * 1024 * 1024 * 4 // 3)

    resp = client.post(
        "/api/v1/hash",
        json={"file_base64": base64_gigante, "filename": "gigante.bin"},
    )

    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"
