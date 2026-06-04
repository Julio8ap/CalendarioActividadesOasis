# Calendario Actividades Oasis

Aplicación web en Python + Streamlit para visualizar el calendario mensual de actividades, servicios, servidores asignados y grupo semanal activo de Iglesia Oasis.

## Archivos principales

```text
app.py
requirements.txt
calendario_iglesia_datos.xlsx
README.md
```

## Fuente de datos

La app trabaja con dos fuentes:

1. **Google Sheets**, como fuente principal si está configurado en Streamlit Secrets.
2. **calendario_iglesia_datos.xlsx**, como respaldo local si Google Sheets falla o no está configurado.

## Hojas necesarias

El archivo de datos debe conservar estas hojas:

```text
Lista Servidores
Servidores
Servicios
Estados
Meses
Registro Servicios
Configuracion
```

## Visualización

La vista muestra:

- Título principal: Calendario Actividades Oasis.
- Filtros compactos de año y mes.
- Calendario mensual en cuadrícula completa de domingo a sábado.
- Días del mes anterior o siguiente cuando se necesiten para completar la cuadrícula.
- Nombre del día y fecha dentro de cada tarjeta.
- Servicios expandibles dentro de cada día.
- Actividades visibles directamente.
- Estado solo para actividades.
- Alerta visual si una persona tiene doble privilegio el mismo día.
- Grupo semanal activo y listado expandible de servidores del grupo.

## Configuración de Google Sheets público

En Streamlit Community Cloud entra a tu app y abre:

```text
Settings > Secrets
```

Agrega:

```toml
[google_sheets]
enabled = true
spreadsheet_id = "PEGA_AQUI_EL_ID_DEL_GOOGLE_SHEETS"
mode = "public"
```

El Google Sheets debe tener permisos de lectura por enlace.

## Configuración de Google Sheets privado

En Secrets agrega:

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

Luego comparte el Google Sheets con el correo `client_email` de la service account como lector.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Subir cambios a GitHub

Después de reemplazar archivos o modificar el Excel de respaldo:

```bash
git status
git add .
git commit -m "Actualizar calendario visual"
git push
```

Streamlit actualizará la app conectada al repositorio.

## Actualizar solo datos

Si ya usas Google Sheets, solo edita el Google Sheets y recarga la app.

Si cambias el Excel local de respaldo, guarda el archivo y súbelo al repositorio:

```bash
git add calendario_iglesia_datos.xlsx
git commit -m "Actualizar datos de respaldo"
git push
```
