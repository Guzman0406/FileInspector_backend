# METADATOS 
import io

import piexif
from PIL import Image

# Nombres legibles de las etiquetas GPS que usa piexif 
# Evitar llamar a las funciones de piexif con su nombre completo
GPS_TAGS = piexif.GPSIFD
EXIF_TAGS = piexif.ExifIFD
IMAGE_TAGS = piexif.ImageIFD

# Etiquetas para saber cual es la información sensible
SENSITIVE_TAG_NAMES = {
    "Make",
    "Model",
    "Software",
    "Artist",
    "CameraOwnerName",
    "BodySerialNumber",
    "LensSerialNumber",
    "DateTime",
    "DateTimeOriginal",
    "DateTimeDigitized",
}

# Dentro de piexif cada tag esta en numero, busca el numero y lo 
# devuelve de manera legible (caso contrario solo trae codigo)
def _tag_name(ifd_name: str, tag_id: int) -> str:
    try:
        return piexif.TAGS[ifd_name][tag_id]["name"]
    except KeyError:
        return str(tag_id)

# Convierte los valores del EXIF de binario a string 
# .strip() quita los ceros
def _decode_value(value) -> str:
    if isinstance(value, bytes): # el valor son bytes?
        try:
            return value.decode("utf-8", errors="replace").strip("\x00").strip()
        except Exception:
            return str(value)
    return str(value)

# Conversion de las coordenadas
def _dms_to_decimal(dms, reference: str) -> float:
    grados, minutos, segundos = dms
    decimal = (
        grados[0] / grados[1]
        + (minutos[0] / minutos[1]) / 60
        + (segundos[0] / segundos[1]) / 3600
    )
    if reference in ("S", "W"):
        decimal = -decimal
    return decimal

# Junta la latitud y longitud 
def _extraer_gps(exif_dict: dict) -> dict | None:
    gps_ifd = exif_dict.get("GPS")
    if not gps_ifd:
        return None
    
    lat = gps_ifd.get(GPS_TAGS.GPSLatitude)
    lat_ref = gps_ifd.get(GPS_TAGS.GPSLatitudeRef)
    lon = gps_ifd.get(GPS_TAGS.GPSLongitude)
    lon_ref = gps_ifd.get(GPS_TAGS.GPSLongitudeRef)

    # Sino vienen completo los datos no se puede crear una coordenada
    if not (lat and lat_ref and lon and lon_ref):
        return None

    return {
        "latitude": _dms_to_decimal(lat, lat_ref.decode() if isinstance(lat_ref, bytes) else lat_ref),
        "longitude": _dms_to_decimal(lon, lon_ref.decode() if isinstance(lon_ref, bytes) else lon_ref),
    }


def extraer_exif(contenido: bytes) -> dict:
    imagen = Image.open(io.BytesIO(contenido))
    imagen.load()  # fuerza la lectura completa para detectar imágenes corruptas 

    formato = imagen.format  # ej. "JPEG", "PNG", "TIFF", "MPO", "HEIF"
    file_type = "image/jpeg" if formato == "MPO" else f"image/{formato.lower()}"

    exif_bytes = imagen.info.get("exif")

    campos = []
    gps = None

# Si la imagen trae metadatos
    if exif_bytes:
        exif_dict = piexif.load(exif_bytes)

        # Por cada bloque y cada etiqueta
        for ifd_name in ("0th", "Exif", "1st"):
            for tag_id, valor in exif_dict.get(ifd_name, {}).items():
                nombre = _tag_name(ifd_name, tag_id)
                campos.append({
                    "tag": nombre,
                    "value": _decode_value(valor),
                    "sensitive": nombre in SENSITIVE_TAG_NAMES,
                })

        gps = _extraer_gps(exif_dict)

    # Revisar si algun campo es sensible 
    has_sensitive = any(c["sensitive"] for c in campos) or gps is not None

    return {
        "file_type": file_type,
        "fields": campos,
        "gps": gps,
        "has_sensitive_data": has_sensitive,
    }
