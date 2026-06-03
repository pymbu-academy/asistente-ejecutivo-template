# GWS — Google Workspace CLI

CLI para que el asistente lea y opere tu Google Workspace (Gmail, Drive, Sheets, Calendar, Docs, Tasks).

## Instalación
```bash
npm install -g @googleworkspace/cli      # o lo hace setup.sh
gws --version
```

## Autenticación (con TU cuenta de Google)
La auth es **personal** y queda guardada en tu computadora (keyring local), nunca en el repo.
```bash
gws auth setup --login    # 1ª vez: configura proyecto Google Cloud + login (requiere gcloud)
gws auth login            # login OAuth si ya tenés cliente configurado
gws auth status           # ver estado
```
- **Scopes:** Calendar, Docs, Drive, Gmail, Sheets, Tasks (y Cloud Platform si usás `--full`).
- Podés limitar servicios en el login: `gws auth login -s drive,gmail,sheets`.
- Doc oficial: https://github.com/googleworkspace/cli

## Sintaxis general
Los comandos usan `--params` con JSON:
```bash
gws <servicio> <recurso> <método> --params '{"param": "valor"}'
```
> Tip: dentro del JSON, escapá las comillas dobles o evitá comillas simples anidadas.

## Ejemplos frecuentes

### Drive — buscar archivos
```bash
gws drive files list --params "{\"q\": \"name contains 'reporte'\", \"supportsAllDrives\": true, \"includeItemsFromAllDrives\": true, \"corpora\": \"allDrives\"}"
```

### Sheets — leer valores de una hoja
```bash
gws sheets spreadsheets values get --params "{\"spreadsheetId\": \"TU_ID\", \"range\": \"Hoja1!A1:Z100\"}"
```

### Gmail — listar mensajes
```bash
gws gmail users messages list --params "{\"userId\": \"me\", \"q\": \"subject:factura\"}"
```

### Calendar — listar eventos
```bash
gws calendar events list --params "{\"calendarId\": \"primary\", \"timeMin\": \"2026-01-01T00:00:00Z\", \"timeMax\": \"2026-01-31T23:59:59Z\"}"
```

### Docs — crear / editar
```bash
gws docs documents batchUpdate --params "{\"documentId\":\"TU_ID\"}" --json "{\"requests\":[ ... ]}"
```

## Opciones útiles
- `--format table` · `--format csv` — salida legible / exportable.
- `--page-all` — auto-paginación.
- `--dry-run` — previsualizar sin ejecutar.
- `-o archivo.json` — guardar resultado.

## Skills relacionadas
Si instalaste las skills `gws-*` (ver `tools.md`), el asistente ya sabe usar Gmail/Drive/Sheets/Calendar/Docs/Tasks sin que recuerdes la sintaxis exacta.

---
_Anotá acá los IDs de tus planillas/carpetas más usadas a medida que las uses._
