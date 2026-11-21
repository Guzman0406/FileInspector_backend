from app.core.base_model import LIMITE_DIFERENCIAS

"""
    recorrer ambos archivos byte por byte y
    regresa las primeras diferencias encontradas, más el
    conteo total, si la lista trae mas de 20 para.
"""

def comparar_archivos(contenido_a: bytes, contenido_b: bytes) -> dict:

    tamano_a = len(contenido_a)
    tamano_b = len(contenido_b)
    tamano_mayor = max(tamano_a, tamano_b)

    diferencias = []
    total_differences = 0

    for posicion in range(tamano_mayor):
        byte_a = contenido_a[posicion] if posicion < tamano_a else None
        byte_b = contenido_b[posicion] if posicion < tamano_b else None

        if byte_a != byte_b:
            total_differences += 1
            if len(diferencias) < LIMITE_DIFERENCIAS:
                diferencias.append({
                    "position": posicion,
                    "value_a": byte_a,
                    "value_b": byte_b,
                })

    return {
        "size_a": tamano_a,
        "size_b": tamano_b,
        "identical": total_differences == 0,
        "total_differences": total_differences,
        "truncated": total_differences > LIMITE_DIFERENCIAS,
        "differences": diferencias,
    }
