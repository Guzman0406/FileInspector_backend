"""Tests del módulo clean: la función pura (repository) y el
endpoint HTTP completo (router + service)."""
import base64

from app.modules.clean.repository import limpiar_jpeg, limpiar_metadatos
from app.modules.exif.repository import extraer_exif
from tests.conftest import a_base64


# Tests de las funciones puras de repository

def test_limpiar_jpeg_quita_el_segmento_exif(jpeg_con_exif):
    limpio, eliminados = limpiar_jpeg(jpeg_con_exif)

    assert "EXIF (APP1)" in eliminados
    assert len(limpio) < len(jpeg_con_exif)
    # El archivo limpio, al volver a analizarse, ya no debe tener metadatos
    resultado = extraer_exif(limpio)
    assert resultado["fields"] == []
    assert resultado["gps"] is None


def test_limpiar_jpeg_sin_metadatos_no_quita_nada(jpeg_sin_exif):
    limpio, eliminados = limpiar_jpeg(jpeg_sin_exif)

    assert eliminados == []
    assert limpio == jpeg_sin_exif


def test_limpiar_metadatos_tipo_no_soportado_lanza_error():
    try:
        limpiar_metadatos(b"contenido cualquiera", "application/pdf")
        assert False, "debía lanzar ValueError"
    except ValueError:
        pass


# Tests del endpoint POST /api/v1/clean

def test_endpoint_clean_quita_exif_de_jpeg(client, jpeg_con_exif):
    resp = client.post(
        "/api/v1/clean",
        json={"file_base64": a_base64(jpeg_con_exif), "filename": "foto.jpg"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["file_type"] == "image/jpeg"
    assert "EXIF (APP1)" in data["removed_metadata"]
    assert data["cleaned_size_bytes"] < data["original_size_bytes"]

    # El archivo que regresa el endpoint, al re-analizarlo, no debe tener EXIF
    contenido_limpio = base64.b64decode(data["cleaned_file_base64"])
    resultado = extraer_exif(contenido_limpio)
    assert resultado["fields"] == []


def test_endpoint_clean_jpeg_sin_metadatos_queda_igual(client, jpeg_sin_exif):
    resp = client.post(
        "/api/v1/clean",
        json={"file_base64": a_base64(jpeg_sin_exif), "filename": "foto.jpg"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["removed_metadata"] == []
    assert body["data"]["cleaned_size_bytes"] == body["data"]["original_size_bytes"]


def test_endpoint_clean_formato_no_soportado(client, pdf_real):
    resp = client.post(
        "/api/v1/clean",
        json={"file_base64": a_base64(pdf_real), "filename": "doc.pdf"},
    )

    assert resp.status_code == 415
    assert resp.json()["error"]["code"] == "UNSUPPORTED_FORMAT"


def test_endpoint_clean_base64_invalido(client):
    resp = client.post(
        "/api/v1/clean",
        json={"file_base64": "esto-no-es-base64!!!", "filename": "x.jpg"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_BASE64"


def test_endpoint_clean_archivo_demasiado_grande(client):
    # max_size_cleaner son 10MB; mandamos un base64 que ya estimado lo supera
    base64_gigante = "A" * (11 * 1024 * 1024 * 4 // 3)

    resp = client.post(
        "/api/v1/clean",
        json={"file_base64": base64_gigante, "filename": "gigante.jpg"},
    )

    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_endpoint_clean_campo_faltante_da_422(client):
    resp = client.post("/api/v1/clean", json={"filename": "x.jpg"})

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
