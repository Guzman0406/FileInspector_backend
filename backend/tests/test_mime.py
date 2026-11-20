"""Tests del módulo mime."""
from app.modules.mime.repository import detectar_mime
from tests.conftest import a_base64


# Tests de la función pura detectar_mime 

def test_detectar_mime_pdf_real_con_extension_correcta(pdf_real):
    resultado = detectar_mime(pdf_real, "documento.pdf")

    assert resultado["detected_mime_type"] == "application/pdf"
    assert resultado["extension_matches"] is True
    assert resultado["suspicious"] is False


def test_detectar_mime_pdf_disfrazado_de_jpg(pdf_real):
    resultado = detectar_mime(pdf_real, "documento.jpg")

    assert resultado["detected_mime_type"] == "application/pdf"
    assert resultado["extension_matches"] is False
    assert resultado["suspicious"] is True
    assert len(resultado["suspicious_reasons"]) == 1


def test_detectar_mime_docx_real_se_distingue_de_zip_generico(docx_real):
    resultado = detectar_mime(docx_real, "reporte.docx")

    assert resultado["detected_mime_type"] == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert resultado["extension_matches"] is True
    assert resultado["suspicious"] is False


def test_detectar_mime_doble_extension_sospechosa(pdf_real):
    resultado = detectar_mime(pdf_real, "factura.pdf.exe")

    assert resultado["suspicious"] is True
    razones = " ".join(resultado["suspicious_reasons"])
    assert "doble extensión" in razones


def test_detectar_mime_jpeg_real_con_extension_correcta(jpeg_sin_exif):
    resultado = detectar_mime(jpeg_sin_exif, "foto.jpg")

    assert resultado["detected_mime_type"] == "image/jpeg"
    assert resultado["extension_matches"] is True
    assert resultado["suspicious"] is False


#  Tests del endpoint POST /api/v1/mime 

def test_endpoint_mime_pdf_real(client, pdf_real):
    resp = client.post(
        "/api/v1/mime",
        json={"file_base64": a_base64(pdf_real), "filename": "documento.pdf"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["detected_mime_type"] == "application/pdf"
    assert body["data"]["suspicious"] is False


def test_endpoint_mime_extension_mentirosa(client, pdf_real):
    resp = client.post(
        "/api/v1/mime",
        json={"file_base64": a_base64(pdf_real), "filename": "foto.jpg"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["suspicious"] is True
    assert body["data"]["extension_matches"] is False


def test_endpoint_mime_base64_invalido(client):
    resp = client.post(
        "/api/v1/mime",
        json={"file_base64": "no-es-base64!!!", "filename": "x.pdf"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_BASE64"
