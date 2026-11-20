"""
Fixtures compartidos para todos los tests.

Decisiones importantes para quien lea esto:
- No usamos una base de datos real: sobreescribimos `get_db` con una sesión
  falsa (FakeDBSession) que solo "finge" guardar. Así los tests corren rápido
  y no dependen de que Postgres esté arriba ni ensucian audit_logs.
- Desactivamos el rate limiter durante los tests (si no, al correr muchos
  tests seguidos contra el mismo endpoint, el límite de 30/minuto los
  tumbaría con 429 y no estaríamos probando lo que queremos probar).
- Los archivos de prueba (JPEG con EXIF, PDF, DOCX falso, etc.) se generan
  en memoria con Pillow/piexif/zipfile, no se leen de disco.

  No se usara
"""
import base64
import io
import zipfile

import piexif
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.database import get_db
from app.core.limiter import limiter
from app.main import app


class FakeDBSession:
    """Sesión de base de datos falsa: solo cumple el contrato que usa
    log_audit (add + commit/rollback async), sin tocar Postgres."""

    def add(self, obj):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass


async def _override_get_db():
    yield FakeDBSession()


@pytest.fixture(scope="session", autouse=True)
def _desactivar_rate_limit():
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture(scope="session")
def client():
    # Un solo TestClient para toda la sesión de tests: el lifespan de la app
    # (que conecta a Postgres) corre una sola vez, en un solo event loop.
    # Crear uno por test choca el motor async de SQLAlchemy contra loops
    # distintos ("attached to a different loop").
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def a_base64(contenido: bytes) -> str:
    return base64.b64encode(contenido).decode()


def _dms(deg_float: float):
    deg = int(deg_float)
    minutos_float = (deg_float - deg) * 60
    minutos = int(minutos_float)
    segundos = round((minutos_float - minutos) * 60 * 100)
    return ((deg, 1), (minutos, 1), (segundos, 100))


@pytest.fixture()
def jpeg_con_exif() -> bytes:
    """JPEG real con Make, Model, Software, fecha y GPS (CDMX) incrustados."""
    img = Image.new("RGB", (20, 20), color="red")

    zero_ifd = {
        piexif.ImageIFD.Make: b"TestCamara",
        piexif.ImageIFD.Model: b"ModeloX",
        piexif.ImageIFD.Software: b"PytestSuite",
    }
    exif_ifd = {piexif.ExifIFD.DateTimeOriginal: b"2026:01:01 10:00:00"}
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: b"N",
        piexif.GPSIFD.GPSLatitude: _dms(19.4326),
        piexif.GPSIFD.GPSLongitudeRef: b"W",
        piexif.GPSIFD.GPSLongitude: _dms(99.1332),
    }
    exif_bytes = piexif.dump({"0th": zero_ifd, "Exif": exif_ifd, "GPS": gps_ifd})

    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif_bytes)
    return buf.getvalue()


@pytest.fixture()
def jpeg_sin_exif() -> bytes:
    """JPEG real sin ningún metadato EXIF."""
    img = Image.new("RGB", (20, 20), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture()
def pdf_real() -> bytes:
    """PDF mínimo pero válido: suficiente para que magic bytes lo detecte
    como application/pdf de verdad (empieza con %PDF-)."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\n"
        b"trailer<</Root 1 0 R>>\n"
        b"%%EOF"
    )


@pytest.fixture()
def docx_real() -> bytes:
    """DOCX real: un ZIP con la marca interna word/document.xml, igual
    a como lo genera Word de verdad por dentro."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", "<w:document/>")
    return buf.getvalue()
