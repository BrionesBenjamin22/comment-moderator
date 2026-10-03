# Butchery Moderation Lab
## Especificación Funcional — v0.2

**Estado:** Definición funcional inicial  
**Propósito:** Recolección y evaluación de comentarios para el clasificador de Butchery  
**Clasificador:** Jev — TypeSafe AI  
**Integración IA:** Python + TypeSafe Python SDK

---

# 1. Objetivo

Butchery Moderation Lab es una aplicación web pública y experimental destinada a recopilar comentarios académicos y evaluar cómo un clasificador basado en IA interpreta su contenido.

La aplicación no forma parte inicialmente del producto Butchery y no pretende implementar un sistema completo de reseñas.

Su finalidad es:

1. recopilar comentarios representativos;
2. ejecutar el clasificador experimental;
3. mostrar visualmente sus resultados;
4. obtener feedback del autor;
5. detectar errores sistemáticos;
6. recopilar casos ambiguos;
7. generar datos útiles para evaluar y mejorar futuras versiones del clasificador.

---

# 2. Principio fundamental

El clasificador:

**describe el comentario, pero no decide si debe publicarse.**

La decisión futura de:

- PUBLICAR;
- REVISAR;
- RECHAZAR;

pertenece a una política de moderación independiente.

---

# 3. Flujo principal

```text
Landing
   ↓
Escribir comentario
   ↓
Analizar
   ↓
Clasificador Jev
   ↓
Mostrar interpretación
   ↓
¿El autor está de acuerdo?
   │
   ├── Sí
   │    ↓
   │  Confirmar
   │
   └── No
        ↓
      Corregir
        ↓
      Confirmar
        ↓
Comentario disponible
para exploración pública
```

---

# 4. Landing

La landing deberá ser deliberadamente sencilla.

Debe explicar:

- qué es el experimento;
- quién lo desarrolla;
- por qué se está realizando;
- qué se pretende investigar;
- cómo puede colaborar el participante.

CTA principal:

`Probar el clasificador`

CTA secundario:

`Ver comentarios`

Se deberá solicitar que no se introduzca información privada o sensible innecesaria.

---

# 5. Creación del comentario

El participante podrá ingresar:

- comentario;
- materia/cátedra opcional;
- docente ficticio o referencia opcional.

No se requiere cuenta.

La aplicación deberá permitir participar anónimamente.

No será necesario registrar identidad para que el comentario sea válido.

---

# 6. Clasificación

El sistema analizará:

- categoría;
- insulto;
- falta de respeto;
- ataque personal;
- burla;
- sarcasmo;
- hostilidad;
- valor académico.

La clasificación deberá almacenar tanto el resultado categórico como cualquier señal probabilística relevante devuelta por el clasificador.

---

# 7. Visualización

Los resultados deberán ser visuales e interactivos.

Ejemplo conceptual:

```text
ANÁLISIS

Crítica constructiva                  82%

Sarcasmo             █████████░       91%
Burla                ██████░░░░       63%
Falta de respeto     ███░░░░░░░       28%
Ataque personal      ██░░░░░░░░       17%
Insulto              ░░░░░░░░░░        2%

Hostilidad
Nula ─── Baja ───●── Moderada ─── Alta ─── Severa

Valor académico
Muy bajo ─── Bajo ───●── Alto ─── Muy alto
```

Se podrán utilizar:

- gradientes;
- barras;
- sliders;
- badges;
- transiciones;
- animaciones suaves;
- expansión progresiva de información.

La interfaz deberá mantenerse clara en dispositivos móviles.

---

# 8. Feedback del autor

Después del análisis:

> ¿Interpretamos correctamente tu comentario?

Opciones:

`Sí, es correcto`

`Quiero corregir algo`

El autor constituye el **validador principal de la intención de su propio comentario**.

Esto resulta especialmente relevante para:

- sarcasmo;
- burla;
- hostilidad;
- intención comunicativa.

---

# 9. Corrección

Al seleccionar `Quiero corregir algo`, las métricas pasarán a modo interactivo.

El participante podrá seleccionar qué dimensiones considera incorrectas.

Sólo deberá corregir esas dimensiones.

Ejemplo:

```text
Sarcasmo

Interpretación del modelo
█████████░ 91%

¿Cómo lo quisiste expresar?

Nada sarcástico ───────────── Muy sarcástico
                  ●
```

No se obligará al usuario a modificar todas las dimensiones.

También podrá introducir:

**Aclaración opcional**

Ejemplo:

> Lo dije irónicamente, pero no pretendía burlarme del profesor.

---

# 10. Intención humana

Cuando corresponda se almacenarán dos conceptos diferentes:

## Clasificación humana

Corrección categórica.

Ejemplo:

```text
sarcasm = true
```

## Intensidad percibida

Señal complementaria proporcionada mediante slider.

Ejemplo:

```text
sarcasmIntensity = 0.72
```

La intensidad percibida no constituye una medición científica ni reemplaza la etiqueta categórica.

Es información experimental adicional.

---

# 11. Exploración pública

Los participantes podrán consultar comentarios previamente enviados.

Cada comentario podrá mostrar:

- texto;
- clasificación realizada;
- resultado general;
- fecha aproximada;
- feedback confirmado por su autor.

No se mostrarán datos identificatorios innecesarios.

---

# 12. Participación de terceros

Los participantes podrán aportar observaciones sobre comentarios existentes.

Un tercero:

**PUEDE**

- indicar que interpreta algo de otra manera;
- aportar una observación;
- señalar ambigüedad;
- explicar por qué considera problemática una clasificación.

Un tercero:

**NO PUEDE**

- modificar el feedback del autor;
- modificar la clasificación almacenada;
- reemplazar la intención declarada por el autor;
- validar definitivamente el comentario;
- convertir su opinión en ground truth.

---

# 13. Autoridad del feedback

La información deberá distinguir:

```text
MODEL PREDICTION
       │
       ▼
AUTHOR FEEDBACK
       │
       ├── principal señal humana
       │
       ▼
THIRD-PARTY OBSERVATIONS
       │
       └── evidencia secundaria
```

La aplicación nunca deberá mezclar estos conceptos.

---

# 14. Comentarios de terceros

Un tercero podrá agregar una observación anónima.

Ejemplo:

> Para mí “un capo” es claramente sarcástico considerando la segunda oración.

La observación deberá almacenarse separadamente.

Conceptualmente:

```text
Comment
│
├── Classification
│
├── AuthorFeedback
│
└── Observations[]
    ├── Observation
    ├── Observation
    └── Observation
```

---

# 15. Anonimato

El comportamiento predeterminado será anónimo.

No se requiere autenticación para el MVP.

No almacenar:

- IP como parte del dataset;
- geolocalización;
- fingerprint;
- información innecesaria del dispositivo;
- información personal no requerida.

Una futura versión podrá incorporar identificación voluntaria si existe una razón funcional concreta.

---

# 16. Metadata

Cada análisis deberá almacenar como mínimo:

```text
id
createdAt
classifiedAt
feedbackAt

classifierVersion
modelVersion
language

processingTimeMs
```

Cuando corresponda:

```text
feedbackUpdatedAt
```

Las observaciones deberán almacenar su propio timestamp.

---

# 17. Dataset

Los datos públicos no constituyen automáticamente ground truth.

Estados:

```text
PENDING
VERIFIED
REJECTED
```

Flujo:

```text
Datos públicos
     ↓
RAW DATA
     ↓
revisión
     ↓
CURATED DATASET
     ↓
evaluación
     ↓
nueva versión del clasificador
```

---

# 18. Restricciones del MVP

No implementar inicialmente:

- cuentas;
- autenticación;
- perfiles;
- profesores como entidades;
- materias como entidades;
- administración compleja;
- sistema de reputación;
- votos positivos/negativos;
- edición comunitaria;
- ranking de usuarios;
- entrenamiento online;
- modificación automática del clasificador.

---

# 19. Criterio de éxito

El MVP estará completo cuando permita:

1. enviar un comentario;
2. clasificarlo;
3. visualizar intuitivamente la clasificación;
4. explorar cada dimensión;
5. confirmar el análisis;
6. corregir dimensiones individuales;
7. expresar intensidad percibida cuando corresponda;
8. almacenar el feedback del autor;
9. consultar comentarios públicos;
10. agregar observaciones anónimas a comentarios ajenos;
11. mantener separadas predicción, intención del autor y opinión de terceros;
12. exportar posteriormente los datos para análisis y curación.