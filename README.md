# Calendario Actividades Oasis

Aplicación web en Streamlit para visualizar el calendario mensual de servicios, actividades y grupos de servicio de la iglesia.

## Archivos principales

- `app.py`: aplicación Streamlit.
- `calendario_iglesia_datos.xlsx`: respaldo local de datos.
- `requirements.txt`: librerías necesarias.
- `README.md`: instrucciones.

## Hojas necesarias en Google Sheets o Excel

La estructura debe mantenerse igual:

- `Lista Servidores`
- `Servidores`
- `Servicios`
- `Estados`
- `Meses`
- `Registro Servicios`
- `Configuracion`

## Opción intermedia de datos

La app intenta leer primero desde Google Sheets. Si Google Sheets no está configurado o falla, usa el archivo local `calendario_iglesia_datos.xlsx` como respaldo.

## Configuración de Google Sheets privado

### 1. Subir el Excel a Google Drive

1. Entra a Google Drive.
2. Sube `calendario_iglesia_datos.xlsx`.
3. Ábrelo con Google Sheets.
4. Revisa que las pestañas tengan exactamente los mismos nombres.

### 2. Crear una cuenta de servicio en Google Cloud

1. Entra a Google Cloud Console.
2. Crea o selecciona un proyecto.
3. Activa Google Sheets API.
4. Crea una Service Account.
5. Genera una clave JSON.
6. Copia el correo de la Service Account.
7. Comparte tu Google Sheets con ese correo como lector.

### 3. Agregar Secrets en Streamlit Community Cloud

En tu app publicada:

1. Entra a Manage app.
2. Abre Settings.
3. Entra a Secrets.
4. Agrega esta estructura:

```toml
[google_sheets]
enabled = true
spreadsheet_id = "PEGA_AQUI_EL_ID_DEL_GOOGLE_SHEETS"
mode = "private"

[google_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

El `spreadsheet_id` es la parte del enlace que aparece entre `/d/` y `/edit`.

Ejemplo:

```text
https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
```

## Opción Google Sheets público

Si quieres una configuración más rápida, puedes compartir el Google Sheets como lectura pública y usar:

```toml
[google_sheets]
enabled = true
spreadsheet_id = "PEGA_AQUI_EL_ID_DEL_GOOGLE_SHEETS"
mode = "public"
```

En este modo no necesitas `[google_service_account]`, pero cualquier persona con el enlace del Sheet podría verlo.

## Modo respaldo local

Si no configuras Secrets, la app usará automáticamente:

```text
calendario_iglesia_datos.xlsx
```

Este archivo debe estar en la misma carpeta que `app.py`.

## Actualizar el repositorio

Después de reemplazar archivos en VS Code:

```bash
git status
git add .
git commit -m "Actualizar calendario Oasis"
git push
```

Streamlit actualizará la app desde GitHub.

## Cambios visuales incluidos

- Título superior: `Calendario Actividades Oasis`.
- Filtros compactos de año y mes en la parte superior.
- Sin descripción inicial.
- Sin métricas de resumen.
- Sin selector de días.
- Sin fila independiente con nombres de días.
- Cada fecha muestra su día y fecha dentro del recuadro.
- Las fechas fuera del mes se muestran para mantener una cuadrícula completa y simétrica.
- Los servicios aparecen como etiquetas expandibles dentro de cada fecha.
- El estado se muestra únicamente en actividades.
- Se mantiene la alerta de doble privilegio.
- Se mantiene la rotación semanal de grupos.
