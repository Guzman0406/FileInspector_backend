"""Tests del módulo exif: tanto la función pura (repository) como el
endpoint HTTP completo (router + service)."""
from app.modules.exif.repository import extraer_exif
from tests.conftest import a_base64


#  Tests de la función pura extraer_exif 

def test_extraer_exif_detecta_campos_y_gps(jpeg_con_exif):
    resultado = extraer_exif(jpeg_con_exif)

    assert resultado["file_type"] == "image/jpeg"
    assert resultado["has_sensitive_data"] is True

    tags = {campo["tag"] for campo in resultado["fields"]}
    assert "Make" in tags
    assert "Model" in tags
    # Los punteros internos ExifTag/GPSTag nunca deben aparecer como campo
    assert "ExifTag" not in tags
    assert "GPSTag" not in tags

    assert resultado["gps"] is not None
    assert resultado["gps"]["latitude"] == 19.4326
    # Longitud oeste -> debe quedar negativa
    assert resultado["gps"]["longitude"] < 0


def test_extraer_exif_sin_metadatos_no_truena(jpeg_sin_exif):
    resultado = extraer_exif(jpeg_sin_exif)

    assert resultado["fields"] == []
    assert resultado["gps"] is None
    assert resultado["has_sensitive_data"] is False


# Tests del endpoint POST /api/v1/exif 

def test_endpoint_exif_foto_con_gps(client, jpeg_con_exif):
    resp = client.post(
        "/api/v1/exif",
        json={"file_base64": a_base64(jpeg_con_exif), "filename": "foto.jpg"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["exif"]["has_sensitive_data"] is True
    assert body["data"]["exif"]["gps"]["latitude"] == 19.4326


def test_endpoint_exif_foto_sin_metadatos_es_exito(client, jpeg_sin_exif):
    resp = client.post(
        "/api/v1/exif",
        json={"file_base64": a_base64(jpeg_sin_exif), "filename": "sin_datos.jpg"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["exif"]["fields"] == []


def test_endpoint_exif_base64_invalido(client):
    resp = client.post(
        "/api/v1/exif",
        json={"file_base64": "esto-no-es-base64-valido!!!", "filename": "x.jpg"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_BASE64"


def test_endpoint_exif_archivo_no_es_imagen(client):
    resp = client.post(
        "/api/v1/exif",
        json={"file_base64": a_base64(b"esto no es una imagen"), "filename": "nota.jpg"},
    )

    assert resp.status_code == 415
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNSUPPORTED_FORMAT"


def test_endpoint_exif_campo_faltante_da_422(client):
    resp = client.post("/api/v1/exif", json={"filename": "x.jpg"})

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
