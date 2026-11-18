def tamano_base64_estimado(texto_base64: str) -> int:
    """
    Calcula el tamaño real aproximado (en bytes) de un texto Base64,
    SIN decodificarlo. Útil para rechazar archivos demasiado grandes
    """
    relleno = texto_base64.count("=")
    return (len(texto_base64) * 3) // 4 - relleno
