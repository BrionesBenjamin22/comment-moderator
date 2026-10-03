Butchery — Moderation Classifier v0.1
1. Objetivo
El clasificador analiza comentarios realizados por alumnos sobre docentes y cátedras de Butchery.
Su responsabilidad no es decidir si un comentario debe publicarse. Su responsabilidad es describir semánticamente el comentario mediante un conjunto de dimensiones independientes.
Comentario
    ↓
Clasificador Jev
    ↓
ModerationClassification
    ↓
Futura política de moderación
    ↓
PUBLICAR / REVISAR / RECHAZAR

Esto permite modificar posteriormente las reglas de moderación sin modificar qué entendemos por insulto, sarcasmo, ataque personal, etc.
2. Contrato de salida
export interface ModerationClassification {
  category: CommentCategory;

  insult: boolean;
  disrespect: boolean;
  personalAttack: boolean;
  mockery: boolean;
  sarcasm: boolean;

  hostility: HostilityLevel;
  academicValue: AcademicValue;
}

export type CommentCategory =
  | "ACADEMIC_EXPERIENCE"
  | "CONSTRUCTIVE_CRITICISM"
  | "PRAISE"
  | "COMPLAINT"
  | "PERSONAL_ATTACK"
  | "IRRELEVANT";

export type HostilityLevel =
  | "NONE"
  | "LOW"
  | "MODERATE"
  | "HIGH"
  | "SEVERE";

export type AcademicValue =
  | "VERY_LOW"
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "VERY_HIGH";

3. category
Representa la intención comunicativa principal del comentario.
ACADEMIC_EXPERIENCE
Describe una experiencia, característica o hecho relacionado con la cursada.
“Hay dos parciales y durante el cuatrimestre tuvimos cuatro trabajos prácticos.”

CONSTRUCTIVE_CRITICISM
Presenta una valoración negativa acompañada de argumentos, hechos, experiencias o elementos académicos concretos.
“Los parciales fueron bastante más difíciles que las prácticas y creo que deberían trabajar ejercicios de ese nivel durante las clases.”

Una crítica puede ser muy dura y continuar perteneciendo a esta categoría.
PRAISE
Su intención principal es realizar una valoración positiva.
“Excelente profesor. Explica los temas con ejemplos y siempre responde las consultas.”

COMPLAINT
Expresa disconformidad sin aportar suficiente explicación académica.
“La cursada fue un desastre.”

PERSONAL_ATTACK
La finalidad predominante es atacar, degradar o desacreditar al docente como persona.
“Es un inútil.”

IRRELEVANT
No aporta información relacionada con el docente, la materia o la experiencia académica.
“Aguante Boca.”

4. insult
Pregunta:
¿Existe un agravio explícito dirigido hacia una persona?

Una palabra vulgar no constituye automáticamente un insulto.
“El parcial estuvo hijo de puta.”

insult = false

“El hijo de puta tomó cosas que nunca explicó.”

insult = true

Además:
Una justificación no neutraliza un insulto.

“Es un pelotudo porque tomó temas que nunca explicó.”

continúa siendo:
insult = true

aunque contenga una crítica académica potencialmente válida.
5. disrespect
Pregunta:
¿El comentario se dirige o refiere al docente de una manera degradante, humillante, discriminatoria, invasiva, despectiva o inapropiada?

Regla fundamental:
INSULT ⊂ DISRESPECT

Por tanto:
insult = true
→
disrespect = true

Pero:
disrespect = true

no implica necesariamente:
insult = true

Por ejemplo:
“Quizás si le interesara un poco enseñar aprenderíamos algo.”

Puede ser falta de respeto sin contener un insulto.
Una crítica dura tampoco constituye automáticamente falta de respeto:
“Dijo que iba a evaluar determinados contenidos y terminó tomando otros completamente diferentes. Los parciales fueron mucho más difíciles que las prácticas y estuvo ensañado con los alumnos.”

Puede clasificarse:
disrespect = false

porque cuestiona su comportamiento académico sin degradarlo como persona.
6. personalAttack
Pregunta:
¿El comentario deja de cuestionar lo que hizo el docente y pasa a desacreditar quién es el docente?

La heurística central será:
LO QUE HIZO
     ↓
crítica académica

QUIÉN ES
     ↓
posible ataque personal

Ejemplo:
“Tomó temas que había dicho que no iba a evaluar.”

personalAttack = false

“Es un inútil.”

personalAttack = true

Sin embargo, una evaluación sobre su capacidad profesional puede estar fundamentada:
“Considero que no está capacitado para dictar esta materia porque durante la cursada confundió repetidamente conceptos fundamentales.”

No debería convertirse automáticamente en ataque personal.
El contexto y la fundamentación importan.
7. mockery
Pregunta:
¿El comentario intenta ridiculizar, humillar o burlarse del docente?

Por ejemplo:
“Un nene de primaria explica mejor.”

mockery = true

No es necesario que exista sarcasmo.
Tampoco es necesario que exista un insulto explícito.
8. sarcasm
Pregunta:
¿El significado pretendido del comentario difiere significativamente de su significado literal mediante ironía o sarcasmo?

Ejemplo:
“Excelente organización, cambiaron la fecha del parcial solamente cuatro veces.”

sarcasm = true

El sarcasmo no implica falta de respeto.
Esto será particularmente importante para expresiones del español argentino:
"Un capo..."
"Un fenómeno..."
"Un distinto..."
"Un crack..."
"Qué máquina..."
"Impecable..."
"Hermosa cursada..."

Estas expresiones no tienen una clasificación fija.
“Un capo, explica todo con ejemplos.”

puede ser elogio genuino.
Mientras:
“Un capo, apareció cinco veces en todo el cuatrimestre.”

puede ser sarcasmo.
Debe interpretarse el enunciado completo.
9. hostility
Representa el grado general de actitud adversarial hacia el docente.
NONE
LOW
MODERATE
HIGH
SEVERE

No debe calcularse simplemente contando insultos o palabras negativas.
NONE
Crítica sin hostilidad.
“Los parciales son considerablemente más difíciles que las prácticas.”

LOW
Existe cierta confrontación o ironía.
“Hermosa organización, cambiaron cuatro veces la fecha del parcial.”

MODERATE
Existe una actitud claramente despectiva, pasivo-agresiva o burlona.
“Quizás si al profesor le interesara enseñar aprenderíamos algo.”

HIGH
Existe degradación o ataque directo.
“Es un inútil y no entiendo cómo puede estar dando clases.”

SEVERE
El ataque domina sustancialmente el comentario mediante una combinación intensa de insultos, degradación, discriminación, humillación u hostilidad.
10. academicValue
Responde:
¿Cuánta información concreta y útil obtiene otro alumno sobre la experiencia de cursar esta materia/cátedra con este docente?

Consideraremos principalmente:
especificidad
+
modalidad de enseñanza
+
modalidad de cursada
+
evaluaciones
+
trabajos prácticos
+
dificultad/exigencia
+
organización
+
experiencia concreta

No depende de si la opinión es positiva o negativa.
VERY_LOW
“Pablo es un capo.”

LOW
“Pablo explica muy bien.”

MEDIUM
“Pablo explica bien la teoría pero las prácticas son bastante más complicadas.”

HIGH
“Pablo explica bien la teoría. Hay dos parciales y cuatro TP obligatorios y los parciales suelen ser más difíciles que las prácticas.”

VERY_HIGH
Comentarios que permiten construir una imagen bastante completa de cómo funciona la cursada: metodología, evaluaciones, dificultad, organización, TP, dinámica docente, etc.
11. Reglas de coherencia v0.1
No todas las combinaciones son imposibles. Sin embargo, tendremos algunas invariantes:
R01
insult = true
→ disrespect = true

Y algunas expectativas, que no deberían imponerse ciegamente:
personalAttack = true
→ hostility probablemente >= MODERATE

mockery = true
→ disrespect probablemente = true

En cambio, quedan expresamente prohibidas como reglas:
sarcasm = true → disrespect = true       ❌

crítica negativa → hostility > NONE      ❌

crítica dura → disrespect = true         ❌

palabra vulgar → insult = true           ❌

academicValue alto → comentario válido   ❌

La última es especialmente importante.
Podemos obtener perfectamente:
{
  "category": "CONSTRUCTIVE_CRITICISM",
  "insult": true,
  "disrespect": true,
  "personalAttack": true,
  "mockery": false,
  "sarcasm": false,
  "hostility": "HIGH",
  "academicValue": "VERY_HIGH"
}

El comentario puede contener información académica excelente y expresarla de una manera completamente inaceptable.
12. Qué construimos ahora
Con esto ya tenemos una primera especificación semántica v0.1. Yo no seguiría agregándole dimensiones por ahora.
El próximo entregable debería ser dataset-v0.1.json, pero no haría 200 comentarios arbitrarios de entrada. Empezaría con unos 40–60 casos diseñados intencionalmente, divididos entre casos obvios, críticas fuertes pero legítimas, insultos, ataques personales, sarcasmo argentino, burla, puteadas que no son insultos y, especialmente, pares contrastivos.
Por ejemplo:
"Es un pelotudo."
vs.
"El parcial estuvo pelotudamente difícil."

"Un capo, explica excelente."
vs.
"Un capo, apareció cinco veces en todo el cuatrimestre."

"No está capacitado."
vs.
"Considero que no está capacitado porque confunde conceptos fundamentales..."

"La materia es una mierda."
vs.
"El profesor es una mierda."
