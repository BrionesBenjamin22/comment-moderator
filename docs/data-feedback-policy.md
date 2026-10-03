# Política de Datos y Feedback — v0.1

## 1. Objetivo

Definir qué significa cada fuente de información recopilada por Butchery Moderation Lab y qué autoridad posee dentro del experimento.

---

# 2. Tres fuentes de información

Para cada comentario existirán potencialmente tres interpretaciones.

## A. Predicción del modelo

Lo que Jev interpreta.

```text
MODEL_PREDICTION
```

Nunca constituye ground truth automáticamente.

## B. Feedback del autor

Lo que la persona que escribió el comentario declara que pretendía expresar.

```text
AUTHOR_FEEDBACK
```

Es la principal señal humana sobre la intención comunicativa.

## C. Observaciones externas

Interpretaciones realizadas por terceros.

```text
THIRD_PARTY_OBSERVATION
```

Son señales secundarias.

Nunca reemplazan el feedback del autor.

---

# 3. Intención vs percepción

Debe conservarse una diferencia fundamental:

**El autor conoce su intención.**

**Los lectores conocen su percepción.**

Ejemplo:

Autor:

> “No intenté ser sarcástico.”

Lectores:

> “Lo interpreté como sarcasmo.”

Ambas observaciones son útiles.

No deben sobrescribirse.

Esto permite posteriormente analizar:

```text
intención del autor
        VS
percepción de terceros
        VS
predicción del modelo
```

---

# 4. Correcciones

Nunca sobrescribir la predicción original.

Incorrecto:

```text
prediction.sarcasm = false

usuario corrige

prediction.sarcasm = true
```

Correcto:

```text
prediction.sarcasm = false

authorFeedback.sarcasm = true
```

De esta forma siempre puede reconstruirse qué respondió realmente cada versión del clasificador.

---

# 5. Feedback parcial

El autor no estará obligado a corregir toda la clasificación.

Puede indicar únicamente:

```text
sarcasm → incorrecto
hostility → incorrecto
```

El resto permanecerá:

```text
NOT_DISPUTED
```

No deberá interpretarse necesariamente como una validación explícita individual de cada dimensión salvo que el usuario haya confirmado toda la clasificación.

---

# 6. Intensidades

Las intensidades humanas serán señales experimentales.

Ejemplo:

```json
{
  "sarcasm": true,
  "sarcasmIntensity": 0.72
}
```

No deberán confundirse:

```text
probabilidad del modelo ≠ intensidad humana
```

Un modelo podría responder:

```text
P(sarcasm) = 0.94
```

mientras el autor indica:

```text
sarcasmIntensity = 0.30
```

Ambos valores describen conceptos diferentes.

---

# 7. Ground truth

Ningún comentario público ingresará automáticamente al dataset validado.

Para incorporarlo deberá atravesar curación.

```text
PENDING
   ↓
revisión
   ├── VERIFIED
   └── REJECTED
```

---

# 8. Ambigüedad

El desacuerdo entre personas no deberá tratarse automáticamente como ruido.

Ejemplo:

```text
Autor:
sarcasm = true

Modelo:
sarcasm = true

5 observadores:
3 → sarcasm
2 → no sarcasm
```

Esto puede indicar que el comentario presenta ambigüedad semántica.

Esa ambigüedad constituye información relevante para evaluar el clasificador.

---

# 9. Protección contra manipulación

Las observaciones de terceros:

- no modificarán datos existentes;
- no modificarán el feedback del autor;
- no modificarán el dataset validado;
- no tendrán efecto automático sobre el clasificador.

Toda modificación del dataset curado requerirá revisión.

---

# 10. Principio de conservación

Debe ser posible reconstruir históricamente:

```text
qué escribió la persona

qué respondió el modelo

qué versión produjo la respuesta

qué corrigió el autor

qué percibieron terceros

qué se decidió durante la curación
```

La información original nunca deberá destruirse para representar una corrección posterior.