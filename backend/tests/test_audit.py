"""Tests del módulo de auditoría.
"""
import pytest

from app.modules.audit.repository import log_audit


class _SesionQueFalla:
    """Simula una sesión de base de datos caída: cualquier intento de
    guardar truena, como pasaría si Postgres estuviera inaccesible."""

    def add(self, obj):
        raise RuntimeError("la base de datos no responde")

    async def commit(self):
        pass

    async def rollback(self):
        self.rollback_llamado = True


@pytest.mark.asyncio
async def test_log_audit_no_propaga_error_si_falla_el_guardado():
    sesion = _SesionQueFalla()

    # No debe lanzar ninguna excepción, aunque adentro todo falle
    await log_audit(
        sesion,
        module="exif",
        file_size_bytes=123,
        file_type="image/jpeg",
        success=True,
    )
