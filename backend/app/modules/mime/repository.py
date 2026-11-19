import zipfile
import io

import magic

EXTENSION_MIME_MAP = {
    "pdf": {"application/pdf"},
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "png": {"image/png"},
    "gif": {"image/gif"},
    "bmp": {"image/bmp", "image/x-ms-bmp"},
    "tiff": {"image/tiff"},
    "tif": {"image/tiff"},
    "heic": {"image/heic", "image/heif"},
    "txt": {"text/plain"},
    "csv": {"text/plain", "text/csv"},
    "zip": {"application/zip"},
    "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    "xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "pptx": {"application/vnd.openxmlformats-officedocument.presentationml.presentation"},
    "mp3": {"audio/mpeg"},
    "mp4": {"video/mp4"},
}

EXECUTABLE_MIMES = {
    "application/x-dosexec",
    "application/x-executable",
    "application/x-elf",
    "application/x-mach-binary",
    "application/x-sharedlib",
}

OFFICE_SIGNATURES = {
    "word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xl/workbook.xml": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ppt/presentation.xml": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def _extraer_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def _tiene_doble_extension(filename: str) -> bool:
    partes = filename.lower().split(".")
    if len(partes) < 3:
        return False
    penultima = partes[-2]
    return penultima in EXTENSION_MIME_MAP


def _refinar_office(contenido: bytes, detected: str) -> str:
    """Si el magic byte dice 'zip', revisamos adentro para ver si es
    en realidad un docx/xlsx/pptx (todos son ZIP por dentro)."""
    if detected != "application/zip":
        return detected

    try:
        with zipfile.ZipFile(io.BytesIO(contenido)) as zf:
            nombres = set(zf.namelist())
            for marca, mime_especifico in OFFICE_SIGNATURES.items():
                if marca in nombres:
                    return mime_especifico
    except zipfile.BadZipFile:
        pass

    return detected


def detectar_mime(contenido: bytes, filename: str) -> dict:
    """
    recibe los bytes del archivo y el nombre
    y regresa el análisis de tipo real vs el declarado.
    """
    detected = magic.from_buffer(contenido, mime=True)
    detected = _refinar_office(contenido, detected)

    declared_ext = _extraer_extension(filename)
    tipos_esperados = EXTENSION_MIME_MAP.get(declared_ext, set())
    extension_matches = detected in tipos_esperados if tipos_esperados else False

    razones = []

    if not extension_matches:
        razones.append(
            f"La extensión declarada ('.{declared_ext}') no coincide con el tipo real detectado ({detected})"
        )

    if detected in EXECUTABLE_MIMES and declared_ext not in ("exe", "dll", "bin", "so"):
        razones.append("El archivo es un ejecutable disfrazado de otro tipo de archivo")

    if _tiene_doble_extension(filename):
        razones.append("El nombre del archivo tiene doble extensión (ej. foto.jpg.exe)")

    return {
        "declared_extension": declared_ext,
        "detected_mime_type": detected,
        "extension_matches": extension_matches,
        "suspicious": len(razones) > 0,
        "suspicious_reasons": razones,
    }
