import io

from PIL import Image

JPEG_SEGMENTOS_METADATO = {
    0xFFE1: "EXIF (APP1)",
    0xFFED: "IPTC (APP13)",
}

PNG_CHUNKS_METADATO = {b"eXIf", b"tEXt", b"iTXt", b"zTXt"}

PNG_FIRMA = b"\x89PNG\r\n\x1a\n"


def limpiar_jpeg(contenido: bytes) -> tuple[bytes, list[str]]:
    """Recorre los segmentos del JPEG y elimina los de metadatos,
    dejando intactos los segmentos de la imagen"""
    eliminados = []
    resultado = bytearray()
    posicion = 2  
    resultado += contenido[0:2]

    while posicion < len(contenido):
        marcador = (contenido[posicion] << 8) | contenido[posicion + 1]

     
        if marcador == 0xFFDA:
            resultado += contenido[posicion:]
            break

        longitud_segmento = (contenido[posicion + 2] << 8) | contenido[posicion + 3]
        fin_segmento = posicion + 2 + longitud_segmento

        if marcador in JPEG_SEGMENTOS_METADATO:
            eliminados.append(JPEG_SEGMENTOS_METADATO[marcador])
        else:
            resultado += contenido[posicion:fin_segmento]

        posicion = fin_segmento

    return bytes(resultado), eliminados


def limpiar_png(contenido: bytes) -> tuple[bytes, list[str]]:
    """Recorre los chunks del PNG y elimina los de metadatos,
    dejando intactos los chunks estructurales de la imagen."""
    eliminados = []
    resultado = bytearray(PNG_FIRMA)
    posicion = len(PNG_FIRMA)

    while posicion < len(contenido):
        longitud_datos = int.from_bytes(contenido[posicion:posicion + 4], "big")
        tipo_chunk = contenido[posicion + 4:posicion + 8]
        fin_chunk = posicion + 12 + longitud_datos  # 4 (longitud) + 4 (tipo) + datos + 4 (CRC)

        if tipo_chunk in PNG_CHUNKS_METADATO:
            eliminados.append(tipo_chunk.decode("ascii"))
        else:
            resultado += contenido[posicion:fin_chunk]

        posicion = fin_chunk

    return bytes(resultado), eliminados


def limpiar_metadatos(contenido: bytes, file_type: str) -> tuple[bytes, list[str]]:
    if file_type == "image/jpeg":
        return limpiar_jpeg(contenido)
    if file_type == "image/png":
        return limpiar_png(contenido)
    raise ValueError(f"Tipo de archivo no soportado para limpieza: {file_type}")
