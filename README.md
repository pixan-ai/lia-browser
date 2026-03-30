# lia-browser 🎭

Servicio de scraping con Playwright para Lia. Corre como servicio independiente en Railway.

## Endpoints

- `GET /health` — Status del servicio
- `POST /scrape/divya` — Reporte de ventas Divya
- `POST /scrape/raw` — Scraping genérico de cualquier URL

## Variables de entorno

| Variable | Descripción |
|---|---|
| `LIA_BROWSER_KEY` | API Key para autenticación |
| `DIVYA_USER` | Usuario POS Divya |
| `DIVYA_PASSWORD` | Password POS Divya |
| `PORT` | Puerto (Railway lo asigna automáticamente) |

## Uso

```bash
# Health check
curl https://tu-servicio.railway.app/health

# Reporte Divya
curl -X POST https://tu-servicio.railway.app/scrape/divya \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-key" \
  -d '{"from": "2026-03-24", "until": "2026-03-30"}'
```
