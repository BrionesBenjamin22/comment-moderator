# Backend — primera milestone

FastAPI, Python 3.11, SQLAlchemy 2 y PostgreSQL 17. Dependencias resueltas en `requirements.lock`, herramientas de prueba en `requirements-test.lock`.

## Ejecución

Desde la raíz:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
Invoke-RestMethod http://localhost:8000/health
```

Compose espera PostgreSQL, ejecuta Alembic y provisiona la credencial limitada `butchery_api` antes de arrancar la API. Esa credencial pertenece a infraestructura, no representa una identidad de la aplicación. El migrador posee permisos de esquema y no es la credencial de ejecución del backend.

Desarrollo local desde `backend/`, con PostgreSQL de Compose disponible:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-test.lock
Copy-Item .env.example .env
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m app.db.provision
.venv/Scripts/python -m uvicorn app.main:create_app --factory --reload --no-access-log
```

No se requiere instalación editable. En Linux reemplazar `.venv/Scripts/python` por `.venv/bin/python`.

## Endpoint operativo

`GET /health` ejecuta `SELECT 1` con timeout de conexión y sentencia. Devuelve `200`, `{"status":"ok","database":"ok"}`, o `503`, `{"status":"unavailable","database":"unavailable"}`. Comprueba conectividad; el proceso migrador comprueba el esquema. No expone errores internos ni secretos. OpenAPI está en `/docs` y `/openapi.json`.

No se implementan todavía `/api/comments`, autenticación, edición, eliminación ni Jev. CORS acepta orígenes explícitos sin credenciales. Los futuros errores de validación tienen envelope `{error: {code, message}}` y mensajes seguros en español.

## Modelos y migraciones

`0001_initial` crea `comments`, `classifications`, `feedbacks`, enums PostgreSQL, índice `created_at, id`, FK, unicidad, checks y triggers. UUID generados por aplicación; fechas con zona horaria generadas por la base.

- Comment: texto original, contexto opcional, idioma, fecha y `datasetStatus`, inicialmente `PENDING`.
- Classification: ocho dimensiones v0.1, versiones, tiempo y métricas opcionales. Una por comentario. R01 se valida en schemas y SQL.
- Feedback: cero o uno por comentario, append-only. La FK referencia `classifications.comment_id`, que referencia Comment; así no puede existir feedback sin clasificación y no se duplican referencias.

Triggers rechazan UPDATE/DELETE incluso con la credencial migradora. La API solo tiene SELECT/INSERT y no puede TRUNCATE. No hay modificación de `datasetStatus`: futura curación requiere una migración que permita el cambio o extraiga la responsabilidad sin cambiar su semántica. No existen DatasetEntry ni Observation. El futuro servicio de análisis garantizará exactamente una Classification por Comment mediante persistencia atómica; las restricciones actuales garantizan pertenencia y máximo de una.

```powershell
.venv/Scripts/python -m alembic current
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m alembic check
```

El downgrade elimina tablas y datos y se usa en la base aislada de pruebas. La migración es explícita y no importa modelos actuales para recrear versiones históricas.

## Schemas y reglas de negocio

Contratos camelCase, campos extra rechazados. Texto 1–5000 caracteres, contexto hasta 200 por campo, aclaración hasta 2000. Texto en blanco inválido; contenido original preservado. Booleanos estrictos y enums conocidos.

```json
{
  "acceptedFully": false,
  "disputedDimensions": ["sarcasm"],
  "corrections": {"sarcasm": true},
  "humanIntensities": {"sarcasmIntensity": 72},
  "clarification": "Lo expresé con ironía."
}
```

Aceptación completa exige dimensiones y correcciones vacías. Feedback parcial exige dimensiones únicas y exactamente un valor categórico por dimensión seleccionada. Las restantes son `NOT_DISPUTED`, sin copiar valores ni tratarlas como confirmación individual. Correcciones humanas no sujetas a R01.

Intensidades opcionales `sarcasmIntensity`, `mockeryIntensity`, `hostilityIntensity`: números finitos 0–100, sin coerción desde strings/booleanos. Cero y ausencia son distintos; omitir claves sin dato. Métricas del modelo: 0–1 con significado explícito, distintas de intensidades. Pydantic valida el payload completo; SQL protege relaciones, formas JSON y restricciones principales.

## Classifier y configuración

`Classifier` es un Protocol asíncrono, con `ClassifierError` independiente del proveedor. FakeClassifier devuelve fixture fija, versiones ficticias y métricas vacías. No realiza inferencia ni usa palabras clave. Permite inyectar fixtures o simular fallos; la fábrica de aplicación y `get_classifier` permiten reemplazarlo.

`DATABASE_URL` y `MIGRATION_DATABASE_URL` requieren `postgresql+psycopg` y se representan como secretos. `DB_APP_PASSWORD` se usa solo en provisión. `APP_ENV`, `CORS_ORIGINS`, `DB_CONNECT_TIMEOUT_SECONDS`, `CLASSIFIER_BACKEND` validan configuración. Solo `fake` está disponible.

`COMMENTS_PAGE_SIZE_DEFAULT=12` y `COMMENTS_PAGE_SIZE_MAX=50` configurables; default no puede superar max, con techo técnico de configuración 200. El listado no se implementa todavía; la cantidad mostrada pertenece al frontend.

## Pruebas

Desde `backend/`:

```powershell
.venv/Scripts/python -m pytest -q -m "not postgres"
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m ruff format --check .
```

Suite completa desde la raíz:

```powershell
docker compose --profile test run --build --rm backend-test
docker compose --profile test stop test-db
```

La fixture migra la base efímera `butchery_test` y ejecuta downgrade al terminar. Fuera de Compose, se omiten pruebas PostgreSQL salvo que existan `TEST_DATABASE_URL` y `TEST_API_DATABASE_URL`. Se rechazan nombres de base que no terminen en `_test`; usar exclusivamente una base descartable. No se usa SQLite.

Cobertura: validación, R01, independencia semántica, feedback parcial, intensidades, fake, inyección, CORS, health, migración vs metadata, timestamps, relaciones, FK, unicidad, feedback concurrente y permisos de escritura.

## Resultado de verificación inicial

El 2026-10-03 se ejecutó la suite completa en Docker sobre PostgreSQL 17: 51 tests aprobados, ninguno omitido ni fallido. Queda un aviso de deprecación de Starlette por el uso de httpx en TestClient; no impidió las pruebas. Ruff check y format check aprobaron los 24 archivos Python.

Compose completó migración y provisión. Alembic informó `0001_initial (head)` y `No new upgrade operations detected`. La comprobación HTTP real devolvió health 200 con base disponible, 503 al detenerla y 200 después de restaurarla. La base de tests quedó detenida y el volumen local se conservó.

El puerto 5432 del host fue bloqueado por Windows. `POSTGRES_PORT` permite elegirlo; el ejemplo utiliza 55432. Las URLs de desarrollo local deben usar el mismo puerto del host; Compose conserva 5432 entre servicios.
