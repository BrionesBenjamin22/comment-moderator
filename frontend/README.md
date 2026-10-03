# Frontend — primera milestone

Next.js App Router y TypeScript estricto. `/` introduce el laboratorio; no incluye todavía análisis, explorador o feedback. No hay autenticación ni llamadas al clasificador.

## Desarrollo y validación

Desde `frontend/`, con Node.js 22:

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Abrir `http://localhost:3000`. Verificar:

```powershell
npm run lint
npm run typecheck
npm run build
npm start
```

Docker usa `npm ci`, salida `standalone` y ejecución sin privilegios. `package-lock.json` fija dependencias. La página no requiere conexión al backend.

## Vistas, componentes y contratos

`layout.tsx` define idioma `es-AR` y metadata. `page.tsx` es un Server Component sin estado ni efectos. `globals.css` contiene estilos responsive mínimos, tipografía del sistema y estructura semántica. No hay fuentes externas.

Esta página estática se valida con lint, tipos, build y comprobación HTTP. Los tests de interacción se incorporarán junto con los formularios; no se crean tests que repliquen texto estático.

`NEXT_PUBLIC_API_BASE_URL` reserva la URL pública FastAPI; no se consume todavía ni contiene secretos. Next.js incorpora variables públicas en build: cambiarla requiere recompilar. `NEXT_TELEMETRY_DISABLED=1` deshabilita telemetría durante la ejecución documentada y Docker.

Services, tipos, hooks y validaciones se agregarán con el flujo que los necesite, respetando schemas backend. La futura corrección enviará dimensiones cuestionadas e intensidades 0–100, sin editar registros originales.

Paginación visible pertenece al frontend; backend prevé límites configurables 12/50, sin máximo arquitectónico de 9. No existen permisos individuales. Feedback pertenece al flujo original de análisis; explorador futuro de lectura.

## Aviso de dependencias

La auditoría inicial detectó cinco avisos altos derivados de una sola vulnerabilidad en `braces`, transitiva de `eslint-config-next`. No hay versión corregida publicada en el [aviso GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm). Pertenece a herramientas de desarrollo; la imagen runtime copia solamente la salida standalone. No se aplica el downgrade incompatible sugerido por `npm audit fix --force`. Revisar el aviso al actualizar las herramientas de lint.

## Resultado de verificación inicial

El 2026-10-03 aprobaron `npm run lint`, `npm run typecheck` y `npm run build`. También se construyó y arrancó la imagen Docker standalone. HTTP `/` devolvió 200. Chrome instalado verificó viewports 1280×800 y 390×844, sin desbordamiento horizontal ni excepciones JavaScript; se inspeccionaron las capturas. No se instalaron dependencias de navegador.
