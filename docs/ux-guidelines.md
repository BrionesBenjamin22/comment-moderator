# UX Guidelines — v0.1

## 1. Principio

La interacción debe sentirse como explorar cómo una IA interpretó un comentario, no como completar una encuesta.

Objetivos:

- mínima fricción;
- comprensión inmediata;
- feedback rápido;
- interacción táctil;
- buena experiencia móvil;
- visualización clara de incertidumbre.

---

# 2. Flujo

```text
ESCRIBIR
   ↓
ANALIZAR
   ↓
DESCUBRIR
   ↓
CONFIRMAR / CORREGIR
   ↓
CONTRIBUCIÓN COMPLETADA
```

Evitar cambios de página innecesarios.

---

# 3. Análisis

Una vez recibida la clasificación, las métricas aparecerán progresivamente.

Orden recomendado:

1. categoría;
2. dimensiones semánticas;
3. hostilidad;
4. valor académico;
5. feedback.

Las transiciones deberán ser suaves.

---

# 4. Representación

Utilizar:

- barras;
- gradientes;
- badges;
- sliders;
- microanimaciones;
- expansión y colapso;
- transiciones de estado.

No depender únicamente del color.

Cada métrica deberá mostrar también su nombre y valor.

---

# 5. Modo lectura

Inicialmente las métricas no serán editables.

Ejemplo:

```text
Sarcasmo

█████████░ 91%

Detectamos un uso probablemente sarcástico.
```

---

# 6. Modo corrección

Al seleccionar:

`Quiero corregir algo`

la interfaz pasará suavemente a modo edición.

Mensaje:

> Ajustá solamente aquello que consideres que interpretamos mal.

---

# 7. Sliders

Cuando resulte semánticamente apropiado:

```text
Nada                         Mucho
 |────────────────────────────|
                ●
```

Ejemplos:

- sarcasmo percibido;
- burla percibida;
- hostilidad pretendida.

Los sliders deberán funcionar correctamente tanto mediante touch como teclado.

---

# 8. Feedback categórico

Las dimensiones que necesiten una corrección categórica deberán permitir seleccionar explícitamente el valor correcto.

Ejemplo:

```text
¿Considerás que fue un ataque personal?

[ No ] [ Sí ]
```

El slider no reemplazará esta clasificación.

---

# 9. Comparación

Cuando el usuario corrija algo se podrá mostrar:

```text
MODELO                    VOS

Sarcasmo                  Sarcasmo

91%                       60%

█████████░                ██████░░░░
```

Esto permitirá comprender inmediatamente dónde existe desacuerdo.

---

# 10. Confirmación

Después del envío:

> Gracias. Tu interpretación nos ayuda a entender dónde se equivoca el clasificador.

Acciones:

`Probar otro comentario`

`Ver otros comentarios`

---

# 11. Explorador

Los comentarios públicos deberán presentarse de forma sencilla.

Cada entrada podrá mostrar:

- comentario;
- clasificación resumida;
- fecha;
- indicación de feedback confirmado.

El detalle podrá expandirse.

---

# 12. Observaciones

Dentro del detalle:

**¿Lo interpretaste de otra manera?**

El participante podrá agregar una observación.

Debe quedar visualmente claro:

> Tu observación no modifica la interpretación declarada por el autor.

---

# 13. Mobile first

La mayor parte del flujo deberá poder realizarse cómodamente con una mano.

Priorizar:

- controles grandes;
- sliders táctiles;
- textarea cómodo;
- botones claros;
- ausencia de tablas;
- ausencia de modales complejos;
- scroll vertical natural.

---

# 14. Movimiento

Utilizar movimiento para comunicar cambios de estado.

Ejemplos:

```text
textarea
   ↓
loading
   ↓
categoría aparece
   ↓
métricas se completan
   ↓
feedback aparece
```

Evitar animaciones decorativas que retrasen la interacción.

Respetar:

```text
prefers-reduced-motion
```

---

# 15. Lenguaje

Evitar terminología técnica frente al participante.

En lugar de:

`personalAttack = 0.73`

mostrar:

> **Ataque personal — 73%**

En lugar de:

`academicValue = HIGH`

mostrar:

> **Valor académico — Alto**

El formato técnico permanecerá disponible únicamente internamente.

---

# 16. Principio final

La interfaz deberá permitir responder tres preguntas en pocos segundos:

> ¿Qué entendió la IA?

> ¿Coincide con lo que quise decir?

> Si no coincide, ¿dónde se equivocó?