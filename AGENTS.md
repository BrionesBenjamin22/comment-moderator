# Instrucciones operativas del proyecto

Las fuentes de verdad funcionales y técnicas están en `docs/`. Respetar el alcance autorizado y las decisiones actuales de `docs/ARCHITECTURE.md`.

## Commits al finalizar una tarea

- Utilizar la skill [commit-work](.agents/skills/commit-work/SKILL.md) para cada bloque de commits al finalizar una tarea. Leer sus instrucciones antes de aplicarla.
- Dividir el trabajo en commits locales atómicos, con Conventional Commits: `tipo(scope opcional): descripción breve`.
- Validar cada bloque antes de crear su commit, con los controles relevantes para el cambio. No instalar herramientas innecesarias.
- Revisar `git status`, `git diff` y `git diff --cached`. Agregar solo las rutas o hunks correspondientes al bloque; mantener archivos ajenos fuera del commit.
- Respetar siempre `.gitignore`. Nunca usar `git add -f`, `git add --force` ni otros mecanismos para agregar archivos o directorios ignorados, salvo indicación explícita del usuario.
- No realizar push. La autorización para commits locales no autoriza publicar cambios.
- Informar hashes, mensajes, alcance y validaciones de los commits, y cualquier cambio que quede pendiente.

Esta política reemplaza la convención anterior de entregar únicamente mensajes sugeridos sin ejecutar commits.

## Catálogo de skills del proyecto

Consultar [.agents/skills/README.md](.agents/skills/README.md). La skill `commit-work` está instalada en `.agents/skills/commit-work/`.
