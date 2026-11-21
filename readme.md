# FileInspector API

API pública (sin autenticación) para inspección y limpieza de metadatos en archivos. Permite analizar fotos y documentos para detectar información sensible oculta, verificar integridad y comparar archivos, todo sin almacenar ni un byte en disco.

---

## Información Académica
* **Universidad:** Universidad Politécnica de Chiapas (UPChiapas)
* **Asignatura:** Seguridad Informática
* **Docente:** Jose Alonso Macias Montoya
* **Período:** Septiembre – Diciembre 2026, Grupo 7-C

## Equipo de Desarrollo 
* Angel Eduardo Guzman Lopez (Backend, base de datos y seguridad)
* Ayelen Montserrath Rodriguez Flores (Frontend en Next.js)
---

## Descripción y Problema que Resuelve
Muchos archivos que se comparten a diario (fotos, documentos) contienen metadatos ocultos que pueden revelar información sensible sin que el usuario se dé cuenta: ubicación GPS exacta, modelo de cámara o celular, software usado, fechas de creación, entre otros. FileInspector es una API pública que permite a cualquier persona o aplicación analizar un archivo, detectar esa información oculta, limpiarla, verificar su integridad mediante hashes, y compararlo contra otro archivo — todo en memoria, sin guardar jamás el contenido del archivo en un servidor.

## Funcionalidades Principales
* **Lectura de metadatos EXIF:** extrae todos los datos ocultos de una foto (cámara, fecha, GPS) y marca cuáles son sensibles.
* **Limpieza de metadatos:** elimina los datos ocultos de una imagen JPEG/PNG sin recomprimirla ni perder calidad.
* **Detección de tipo real de archivo:** identifica el tipo verdadero de un archivo por sus "magic bytes" y lo compara contra su extensión, para detectar archivos disfrazados.
* **Cálculo de huellas digitales (hash):** calcula MD5, SHA-1, SHA-256 y SHA-512 de un archivo para verificar su integridad.
* **Comparación de archivos:** compara dos archivos y muestra sus diferencias binarias.
* **Auditoría anónima:** cada uso se registra de forma anónima (módulo, tamaño, éxito/error) para fines estadísticos, sin guardar jamás contenido, metadatos ni direcciones IP.

## Tecnologías Utilizadas
* **Backend:** Python 3.11, FastAPI, Pydantic v2
* **Base de Datos:** PostgreSQL 16 + SQLAlchemy 2 (async) + asyncpg
* **Procesamiento de archivos:** Pillow, piexif, pillow-heif, python-magic, filetype
* **Infraestructura:** Docker y Docker Compose
* **Control de Versiones:** Git y GitHub
---

## Instalación

### Clonar el repositorio
```bash
git clone https://github.com/Guzman0406/Fileinspector
cd Fileinspector
```

### Configurar variables de entorno
Dentro de `backend/`, crea un archivo `.env` con la conexión a la base de datos:
```bash
DATABASE_URL=postgresql+asyncpg://fileinspector:fileinspector_dev_pass@db:5432/fileinspector_db
```

### Levantar el proyecto con Docker
```bash
docker compose up -d --build
```
La API queda disponible en `http://localhost:8003`, con documentación interactiva (Swagger) en `http://localhost:8003/docs`.

### Correr las pruebas automatizadas
```bash
docker compose exec api python -m pytest -v
```
---

## Despliegue
El backend está desplegado públicamente en Render:
* **URL base:** https://fileinspector-backend.onrender.com
* **Documentación interactiva (Swagger):** https://fileinspector-backend.onrender.com/docs

## Endpoints Principales
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/exif` | Extrae metadatos EXIF de una imagen (cámara, fecha, GPS) |
| POST | `/api/v1/clean` | Elimina metadatos de una imagen JPEG/PNG sin recomprimirla |
| POST | `/api/v1/mime` | Detecta el tipo real de un archivo y lo compara contra su extensión |
| POST | `/api/v1/hash` | Calcula MD5, SHA-1, SHA-256 y SHA-512 de un archivo |
| POST | `/api/v1/compare` | Compara dos archivos byte a byte y muestra sus diferencias |
| GET | `/health` | Verifica que la API esté activa |
---

