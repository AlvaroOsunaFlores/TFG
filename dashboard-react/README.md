# Dashboard React (Fase 4/5)

Frontend principal del TFG para visualizar:
- resumen de metricas por `run_id`,
- analisis de umbrales (precision/recall/F1),
- matriz de confusion,
- trazabilidad de mensajes,
- metadata de entrenamiento.

## Requisitos
- Node.js 18+.
- API FastAPI activa (`/api/v1/...`).

## Configuracion
1. Copia `.env.example` a `.env`:
```bash
cp .env.example .env
```

2. Ajusta la URL:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Ejecucion
```bash
npm install
npm run dev
```

## Build
```bash
npm run build
npm run preview
```
