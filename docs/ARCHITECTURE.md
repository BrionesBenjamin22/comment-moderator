# Butchery Moderation Lab — Arquitectura del MVP

Estado: primera milestone implementada. Los flujos de comentarios describen el siguiente bloque; todavía no están implementados sus endpoints ni vistas.

## 1. Fuentes de verdad

Fuentes revisadas íntegramente:

- `functional-spec.md`: especificación funcional v0.2; recolección, clasificación, feedback y exploración pública.
- `data-feedback-policy.md`: política v0.1; separación de predicción, evaluación humana, observaciones y curación.
- `ux-guidelines.md`: flujo continuo de escribir, analizar, descubrir y confirmar o corregir; presentación y accesibilidad.
- `classifier.md`: especificación titulada `Butchery — Moderation Classifier v0.1`. Es el archivo disponible para la fuente solicitada como `classifier-v0.1.md`; no se renombra ni se modifica.

Las decisiones explícitas de esta revisión precisan el MVP: participación anónima, Comment y Classification inmutables, un único Feedback posterior al resultado, intensidades humanas 0–100 y Observation opcional para una etapa posterior. Prevalecen sobre ejemplos anteriores de escala 0–1, referencias a revisiones de feedback y observaciones como requisito inicial. Las fuentes se conservan intactas.

Esta prueba de concepto no requiere identidad ni autenticación. Feedback representa la evaluación humana declarada durante el flujo original, sin comprobar posteriormente quién escribió el comentario. No se introduce un mecanismo de identificación o autorización individual.

## 2. Primera milestone

Implementar únicamente:

- Base Next.js y TypeScript con página inicial mínima.
- FastAPI y configuración validada.
- PostgreSQL, modelos SQLAlchemy y schemas Pydantic.
- Alembic y migración inicial.
- Interfaz `Classifier` y `FakeClassifier` inyectable.
- `GET /health` con comprobación de conexión a PostgreSQL.
- Dockerfiles, Docker Compose, variables de ejemplo y healthchecks.
- Tests y documentación de lo implementado en `frontend/README.md` y `backend/README.md`.

Los modelos y schemas preparan el dominio. Los endpoints de comentarios y la interfaz completa se implementan en el siguiente bloque del MVP. No se integra Jev, su SDK ni credenciales del proveedor; tampoco se generan prompts, rúbricas nuevas o datasets sintéticos. Observation no necesita tabla, schema ni endpoint en la primera milestone. Terraform queda fuera de este trabajo.

## 3. Arquitectura y responsabilidades

```text
Navegador → Next.js → FastAPI → Servicios de aplicación
                                  ├→ Classifier
                                  │    └→ FakeClassifier (milestone 1)
                                  └→ SQLAlchemy → PostgreSQL
Alembic → esquema PostgreSQL
```

Monolito modular de backend separado del frontend. No se requieren colas, workers ni microservicios. API, servicios, persistencia y clasificador permanecen desacoplados para permitir sustituir el proveedor o extraer módulos posteriormente.

| Componente | Responsabilidad |
| --- | --- |
| Frontend | Capturar entradas, mostrar resultados y enviar evaluación humana posterior. |
| API y schemas | Validar contratos estrictos y devolver errores seguros. |
| Servicios | Coordinar clasificación, transacciones e invariantes. |
| Classifier | Describir semánticamente el comentario; no decidir publicación ni curación. |
| Persistencia | Conservar entrada, resultado original, feedback y trazabilidad temporal separados. |

La lógica de negocio no depende de un SDK externo. El contrato público usa camelCase; SQL/Python pueden usar snake_case mediante aliases explícitos.

## 4. Organización propuesta

```text
frontend/
  src/app/
  src/features/moderation/
    types/
    services/
    hooks/
    validation/
    components/
  tests/
  Dockerfile
  README.md
backend/
  app/
    main.py
    config.py
    api/
    schemas/
    services/
    models/
    classifier/
      interface.py
      fake.py
    db/
  migrations/
  tests/
  alembic.ini
  pyproject.toml
  Dockerfile
  README.md
datasets/
  seed/
  curated/
docs/
  ARCHITECTURE.md
docker-compose.yml
.env.example
README.md
```

Services, hooks, validaciones y componentes se crean cuando exista funcionalidad que los necesite. Cada README de frontend/backend documentará vistas o endpoints, contratos, validaciones, reglas, relaciones, errores, configuración y pruebas efectivamente implementados.

## 5. Modelo conceptual y persistencia

```text
Comment
├── Classification
└── Feedback (0..1)

Evolución opcional:
Comment
└── Observation[]
```

Cada Comment persistido tiene exactamente una Classification original. No hay reclasificación en el MVP. Feedback no es una nueva Classification ni reemplaza sus valores.

UUID para identificadores; timestamps con zona horaria normalizados a UTC. Materia y docente son texto opcional, sin entidades relacionadas.

| Entidad | Datos | Restricciones |
| --- | --- | --- |
| Comment | `id`, `text`, `subject?`, `teacher?`, `language`, `createdAt`, `datasetStatus` | Estado inicial `PENDING`; inmutable desde su persistencia; sin `updatedAt` ni operaciones de edición o eliminación. |
| Classification | `id`, `commentId`, ocho dimensiones v0.1, métricas opcionales, `classifierVersion`, `modelVersion`, `processingTimeMs`, `classifiedAt` | `commentId` único y FK a Comment; inmutable. |
| Feedback | `id`, `commentId`, `acceptedFully`, `disputedDimensions`, `corrections`, `humanIntensities`, `clarification?`, `feedbackAt` | `commentId` único; FK a `Classification.commentId`, que referencia Comment. Impide feedback sin clasificación; append-only. |

`datasetStatus` se almacena directamente en Comment por simplicidad del MVP. `PENDING`, `VERIFIED` y `REJECTED` conservan semántica independiente: no representan publicación, feedback ni validez automática. No existe DatasetEntry ni operaciones de curación. La futura curación podrá extraer esta responsabilidad a una entidad e historial separados sin cambiar su semántica. Mientras tanto Comment, incluido este campo, permanece inmutable.

La inmutabilidad se aplica en servicios y persistencia: no se ofrecen operaciones de actualización o borrado de estas tres entidades. La credencial de ejecución de la API tendrá permisos de lectura e inserción sobre sus tablas; las migraciones utilizarán otra credencial con permisos de esquema. No se habilitará borrado en cascada que destruya registros originales.

Índices: FK y orden de exploración por `createdAt, id`. La unicidad de Classification y Feedback debe existir en PostgreSQL además de la validación de aplicación. Las consultas cargan solo las relaciones necesarias.

## 6. Classification v0.1

Las ocho dimensiones son:

- `category`: `ACADEMIC_EXPERIENCE`, `CONSTRUCTIVE_CRITICISM`, `PRAISE`, `COMPLAINT`, `PERSONAL_ATTACK`, `IRRELEVANT`.
- `insult`, `disrespect`, `personalAttack`, `mockery`, `sarcasm`: booleanos estrictos.
- `hostility`: `NONE`, `LOW`, `MODERATE`, `HIGH`, `SEVERE`.
- `academicValue`: `VERY_LOW`, `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`.

R01: `insult = true` implica `disrespect = true` en una salida válida del clasificador. Un resultado inválido se rechaza sin reparación silenciosa.

No se deducen automáticamente hostilidad de ataque personal, falta de respeto de burla o sarcasmo, ni insultos de vocabulario vulgar. Crítica negativa o dura no activa otras dimensiones por sí sola. El valor académico es independiente de polaridad, hostilidad y futura política de publicación.

Probabilidades/confianzas reales se conservan como métricas opcionales con dimensión, significado y escala explícitos. No se inventan ni se convierten booleanos en porcentajes. La UI funciona con etiquetas categóricas cuando no hay métricas.

## 7. Feedback append-only/one-shot

Se crea después de mostrar el resultado en el flujo original. Antes de enviarlo, el formulario permite confirmar toda la clasificación o ajustar dimensiones seleccionadas. Estos ajustes locales no son ediciones de datos persistidos.

Payload propuesto:

```json
{
  "acceptedFully": false,
  "disputedDimensions": ["sarcasm", "hostility"],
  "corrections": {"sarcasm": true, "hostility": "LOW"},
  "humanIntensities": {"sarcasmIntensity": 72, "hostilityIntensity": 30},
  "clarification": "Lo expresé con ironía, sin intención de atacar."
}
```

Validación:

- `acceptedFully = true`: dimensiones cuestionadas y correcciones vacías; confirma el resultado completo. Admite aclaración e intensidades complementarias opcionales.
- `acceptedFully = false`: al menos una dimensión cuestionada, sin duplicados, y un valor corregido para cada dimensión seleccionada. Las claves de `corrections` coinciden exactamente con `disputedDimensions`.
- Correcciones con los mismos booleanos y enums de Classification. El resto queda `NOT_DISPUTED` por interpretación, sin copiar valores ni presentarlos como validación individual.
- `humanIntensities` admite exclusivamente `sarcasmIntensity`, `mockeryIntensity` y `hostilityIntensity`, opcionales, con números finitos entre 0 y 100 inclusive. Cero se conserva; ausencia no equivale a cero.
- Intensidades humanas son señales experimentales, distintas de probabilidad/confianza. No reemplazan etiquetas; no se deriva una etiqueta de un slider ni se exige intensidad para confirmar o corregir.
- Aclaración opcional; no se aceptan cambios del texto, contexto, clasificación o estado del dataset.

R01 valida la salida del clasificador. Feedback conserva declaraciones humanas tipadas aunque contradigan esa regla al compararlas con el resultado original: no se reparan ni se rechazan por imponer coherencia del modelo a la señal humana. La curación posterior podrá evaluar discrepancias sin alterar registros.

El endpoint inserta un único Feedback. No existen edición, eliminación ni revisiones posteriores. Una restricción única protege ante envíos simultáneos: uno obtiene `201` y los restantes `409`. Un reintento tras una respuesta perdida tampoco crea otro registro; el cliente puede consultar el detalle para verificar el feedback existente.

El backend comprueba que existe Comment con Classification; no acredita que una persona haya visto la pantalla. Visualizar antes de evaluar es una regla del frontend. El explorador presenta una declaración recibida sin prometer autoría verificada y no ofrece un formulario de feedback sobre comentarios consultados.

## 8. Flujo del MVP

```text
escribir comentario
        ↓
clasificar
        ↓
persistir Comment + Classification
        ↓
mostrar resultado
        ↓
confirmar o corregir
        ↓
persistir Feedback
```

1. Frontend envía texto y contexto opcional; API valida el payload.
2. Classifier devuelve salida tipada y validada, incluida R01.
3. Una transacción inserta Comment con `datasetStatus = PENDING` y Classification.
4. Solo después del commit se devuelve el resultado. Ante fallo de clasificación o persistencia no queda un comentario parcial.
5. Frontend presenta el resultado en lectura antes de habilitar confirmación o corrección.
6. El envío explícito crea Feedback en otra transacción y muestra confirmación visible.

No se mantiene una transacción abierta durante el análisis. El flujo permanece en la misma pantalla conforme a UX; las reglas generales de navegación tras altas o edición no agregan redirecciones intermedias aquí.

Según el flujo funcional, la lista pública muestra contribuciones completadas, es decir, comentarios con Feedback. Se consulta su existencia sin estado de publicación en Comment ni filtro por Comment.datasetStatus. El detalle por ID permite consultar también el resultado pendiente de feedback para el flujo original; no constituye un recurso privado.

## 9. API prevista

Solo `/health` se implementa en la primera milestone; los demás contratos orientan el siguiente bloque.

| Método y ruta | Entrada | Respuesta |
| --- | --- | --- |
| `POST /api/comments/analyze` | `{text, subject?, teacher?}` | `201`, `{comment, classification}` tras persistencia; no acepta resultados o estado del dataset del cliente. |
| `POST /api/comments/{id}/feedback` | Payload de sección 7 | `201`, Feedback creado; `404` si falta Comment; `409` si ya existe Feedback; `422` ante payload inválido. |
| `GET /api/comments` | `page`, `pageSize`, positivos; backend configurable, default 12 y máximo 50 | `200`, `{items, page, pageSize, total}`; contribuciones completadas, orden `createdAt DESC, id DESC`. |
| `GET /api/comments/{id}` | UUID | `200`, `{comment, classification, feedback, datasetStatus}`; `feedback` puede ser `null`; `404` si no existe. |
| `GET /health` | Sin payload | `200`, `{"status":"ok","database":"ok"}` tras `SELECT 1`; `503`, `{"status":"unavailable","database":"unavailable"}` ante fallo. |

Envelope uniforme `{error: {code, message}}`: `422` validación, `404` recurso ausente, `409` feedback existente, `503` dependencia indisponible. La integración externa futura podrá incorporar `502` para salida inválida y `504` para timeout. No se exponen trazas, SQL, secretos ni datos del proveedor.

UI con mensajes en español y acción útil: «¡Lo sentimos! No pudimos recuperar la información. Intentá nuevamente». Ante `409`, informa que la evaluación ya fue registrada y permite consultar el resultado, sin sugerir otro envío. Los errores conservan texto y ajustes locales. El éxito muestra la confirmación prevista por UX.

No hay endpoints de actualización, borrado o reclasificación. No se agrega un historial de ediciones a entidades inmutables: registros originales, versiones y timestamps aportan trazabilidad. Una futura curación tendrá historial separado paginado con 3 elementos.

## 10. Observation opcional

Podrá incorporarse posteriormente como entidad anónima con `id`, `commentId`, contenido y `createdAt`, en relación 1:N. No modifica Feedback, Classification ni decisiones del dataset y no requiere autenticación.

Un futuro `POST /api/comments/{id}/observations` sería append-only; se definirán entonces payload, límites y lectura paginada. No forma parte de la primera implementación ni bloquea sus modelos.

## 11. Classifier, FakeClassifier y versionado

Interfaz Python `Classifier` con operación asíncrona `classify(input) -> ClassifierResult`. Entrada: texto y contexto. Salida: dimensiones semánticas separadas de metadata y métricas opcionales. Los servicios conocen errores propios de la interfaz, sin depender de excepciones del SDK.

FakeClassifier devuelve fixtures deterministas válidos y permite simular fallos en tests. No usa heurísticas por palabras ni pretende interpretar correctamente textos reales. Identifica el origen ficticio mediante `classifierVersion` y `modelVersion`; no inventa probabilidades.

`classifierVersion` identifica contrato/rúbrica y configuración; `modelVersion`, el modelo utilizado. Un adaptador futuro podrá devolver `modelVersion = null` si el proveedor no ofrece una referencia fiable, sin fabricar una versión. `classifiedAt`, `processingTimeMs` y `language` conservan metadata del análisis. `feedbackAt` pertenece a Feedback y se expone cuando existe; no hay `feedbackUpdatedAt` en esta versión.

Alembic versiona el esquema independientemente del clasificador. Una futura reclasificación exigirá ampliar el modelo preservando el resultado original; no se anticipan cardinalidad 1:N ni endpoints para ello.

Jev queda para una milestone posterior: verificar SDK oficial, validar salidas y documentar métricas reales, timeout y configuración. Esta base no importa ni instala el SDK del proveedor.

## 12. Validación y seguridad

- Pydantic rechaza campos extra, booleanos coercionados, enums inválidos y números no finitos. Frontend replica validaciones para feedback inmediato; backend es la autoridad.
- Límites técnicos iniciales: texto 1–5000 caracteres, contexto hasta 200 por campo, aclaración hasta 2000. Texto solo de espacios es inválido. No se altera puntuación ni se reescribe el comentario antes de analizarlo.
- SQLAlchemy usa consultas parametrizadas. PostgreSQL impone FK, unicidad y restricciones de integridad. El conflicto de unicidad se maneja con rollback antes de devolver `409`.
- Frontend renderiza texto escapado, sin HTML arbitrario. Controles con etiquetas, soporte de teclado y valores visibles; no dependen solo del color y respetan `prefers-reduced-motion`.
- No se recopilan IP, geolocalización, fingerprint ni metadata personal innecesaria para el dataset. Se evita registrar texto y datos personales en logs.
- CORS usa orígenes explícitos por entorno; secretos de infraestructura permanecen en backend y `.env` fuera de Git.
- Health y errores no muestran conexiones, trazas ni credenciales. Se limitan tiempos de conexión y tamaño de requests.

No se agregan permisos por rol ni soft delete por convenciones generales que no corresponden a esta prueba de concepto.

## 13. Desarrollo local e infraestructura

Compose incluye `frontend`, `backend`, `db` y un proceso de migración de una sola ejecución. PostgreSQL usa volumen nombrado y `pg_isready`. Las migraciones esperan la base disponible; backend arranca después de su finalización exitosa. Alembic no se sustituye por `create_all` ni se ejecuta desde cada worker.

Puertos locales: 3000 frontend, 8000 backend y PostgreSQL configurable mediante `POSTGRES_PORT`, sobre loopback. Compose usa 5432 por defecto; `.env.example` propone 55432 porque Windows bloqueó 5432 en la verificación local. PostgreSQL conserva 5432 dentro de Docker. Health comprueba conexión; migraciones se verifican aparte. Los README documentan arranque, migraciones y tests sin borrado automático de volúmenes.

SQLAlchemy síncrono con psycopg y unidad de trabajo por operación de persistencia, fuera del event loop. La llamada asíncrona al clasificador ocurre antes de abrir la transacción. Versiones concretas se fijan y validan al implementar.

| Variable propuesta | Uso |
| --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Base y credencial local de migración. |
| `DATABASE_URL` | Conexión API con permisos limitados de ejecución. |
| `MIGRATION_DATABASE_URL` | Conexión Alembic y provisión de permisos de base. |
| `APP_ENV` | Entorno local/test/producción. |
| `CORS_ORIGINS` | Lista JSON; local `http://localhost:3000`. |
| `DB_CONNECT_TIMEOUT_SECONDS` | Tiempo máximo de conexión. |
| `CLASSIFIER_BACKEND` | `fake`; valores no implementados fallan explícitamente. |
| `NEXT_PUBLIC_API_BASE_URL` | URL pública de API, sin secretos. |
| `COMMENTS_PAGE_SIZE_DEFAULT`, `COMMENTS_PAGE_SIZE_MAX` | Límites backend configurables; 12 y 50 por defecto. |
| `DB_APP_PASSWORD` | Credencial de ejecución PostgreSQL usada por la provisión local. |
| `POSTGRES_PORT` | Puerto PostgreSQL del host; no altera la conexión interna de Compose. |

La cantidad de elementos mostrados pertenece al frontend. Los límites de paginación están configurados para el próximo flujo; todavía no existe endpoint de listado.

Arranque y configuración compatibles con CI/CD futuro, proxy reverso y despliegue cloud, sin infraestructura distribuida adicional.

## 14. Validación prevista

Primera milestone:

1. Backend: configuración, schemas estrictos, dimensiones, R01 y sustitución de FakeClassifier.
2. PostgreSQL aislado: migración desde base vacía, FK, unicidad, estado `PENDING`, timestamps y restricciones de escritura del rol de ejecución.
3. Health: `200` con base disponible, `503` ante fallo, sin información sensible.
4. Frontend: tipos y build; tests de comportamiento cuando existan componentes interactivos.
5. Integración completa de Compose, arranque, migraciones, health y apertura manual de la página inicial.

Al implementar el flujo completo: persistencia atómica, fallo del clasificador sin registros parciales, resultado antes del feedback, confirmación completa, corrección parcial, escala 0–100, valor cero, conflictos concurrentes y reintentos sin duplicación. Verificar paginación y que Feedback no altera entidades originales ni el estado del dataset.

Cada módulo documentará pruebas ejecutadas y limitaciones reales. Al finalizar cada tarea, se utilizará la skill `commit-work` para crear commits locales atómicos de los bloques previamente validados, con formato `tipo(scope): descripción breve`. No se realizará push. Se respetará `.gitignore`, sin agregar archivos ignorados de forma forzada salvo instrucción explícita del usuario. La política persistente y el catálogo están en `AGENTS.md` y `.agents/skills/README.md`.

Verificación inicial del 2026-10-03: 51 tests backend aprobados sobre PostgreSQL real, lint/formato Python y lint/tipos/build frontend aprobados. Migración `0001_initial` aplicada sin diferencias contra metadata. Compose y healthchecks operativos; health 200/503/200 verificado con caída y recuperación de la base. Página inspeccionada en Chrome para escritorio y móvil. Los README registran comandos, resultados y el aviso pendiente de las herramientas de lint.

## 15. Contradicciones técnicas pendientes

No se detectan contradicciones técnicas que bloqueen la primera milestone ni los contratos descritos del MVP.

Los ejemplos de escala 0–1 quedan resueltos por la decisión explícita 0–100. Las referencias a feedback actualizado y observaciones obligatorias quedan acotadas por entrega única y evolución opcional. La ubicación de la especificación semántica se aclara en la sección 1 sin exigir aprobación ni modificar fuentes.

La cuestión técnica que requiere resolución al integrar Jev es la correspondencia entre porcentajes de los ejemplos UX y métricas reales del proveedor: el contrato semántico v0.1 solo define booleanos y enums. Hasta verificar esa capacidad, las métricas son opcionales y la UI presenta valores categóricos sin porcentajes ficticios. No bloquea FakeClassifier ni requiere integrar Jev en esta milestone.
