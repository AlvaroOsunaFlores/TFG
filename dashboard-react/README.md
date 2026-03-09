# Dashboard React

Frontend principal del TFG para visualizar:
- resumen de métricas por `run_id`,
- análisis de umbrales,
- matriz de confusión,
- trazabilidad de mensajes,
- metadatos de entrenamiento.

## Requisitos
- Node.js 18+.
- API FastAPI activa.
- `X-API-Key` configurada en el entorno del frontend.

## Configuración
1. Copia `.env.example` a `.env`:
```powershell
Copy-Item .env.example .env
```

2. Ajusta:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=<API_KEY>
```

## Ejecución
```powershell
npm install
npm run dev
```

## Build
```powershell
npm run build
npm run preview
```
