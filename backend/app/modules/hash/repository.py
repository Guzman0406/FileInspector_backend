import hashlib

TAMANO_BLOQUE = 65536  # 64 KB por bloque


def calcular_hashes(contenido: bytes) -> dict:

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()

# Calcular el hash bloque por bloque
    vista = memoryview(contenido)
    for inicio in range(0, len(vista), TAMANO_BLOQUE):
        bloque = vista[inicio:inicio + TAMANO_BLOQUE]
        md5.update(bloque)
        sha1.update(bloque)
        sha256.update(bloque)
        sha512.update(bloque)

# Muestra el resultado de los hashs
    return {
        "md5": md5.hexdigest(),
        "sha1": sha1.hexdigest(),
        "sha256": sha256.hexdigest(),
        "sha512": sha512.hexdigest(),
    }
