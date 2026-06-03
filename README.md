# Calendario de Servicios de Iglesia

Aplicación web en Python con Streamlit para visualizar un calendario mensual de servicios, actividades, grupos semanales y alertas cuando una persona tiene más de un privilegio el mismo día.

## Archivos incluidos

- `app.py`: aplicación principal.
- `calendario_iglesia_datos.xlsx`: base de datos en Excel.
- `requirements.txt`: librerías necesarias para ejecutar la app.

## Estructura del Excel

### 1. Lista Servidores

Aquí debes escribir los nombres oficiales de todos los servidores.

Columnas:

- `Nombre servidor`
- `Activo`
- `Notas`

Esta hoja alimenta las listas desplegables de:

- `Servidores > Servidor`
- `Registro Servicios > Servidor`

La idea es que no tengas que escribir los nombres manualmente en cada hoja y así evitar errores como nombres repetidos con diferente escritura.

### 2. Servidores

Aquí relacionas cada servidor con su grupo de servicio.

Columnas obligatorias:

- `Servidor`: se selecciona desde `Lista Servidores`.
- `Grupo`: número de grupo, del 1 al 5.
- `Activo`: Sí o No.
- `Notas`.

Ejemplo:

| Servidor | Grupo | Activo | Notas |
|---|---:|---|---|
| Julio Ochoa | 1 | Sí | |
| Libni De O. | 1 | Sí | |

### 3. Servicios

Aquí defines los privilegios y actividades que podrán usarse en el registro.

Columnas obligatorias:

- `Servicio`
- `Categoria`
- `Mostrar en calendario`

En `Categoria` usa:

- `Servicio`: cuando el registro lleva servidor y se puede expandir.
- `Actividad`: cuando solo quieres mostrar una actividad general, sin servidor obligatorio.

La columna `Registro Servicios > ServicioActividad` toma su lista desplegable desde esta hoja.

### 4. Estados

Columna obligatoria:

- `Estado`

Ejemplos: Pendiente, Confirmado, Cambio solicitado, Cancelado.

### 5. Registro Servicios

Esta es la hoja principal que alimenta el calendario.

Columnas obligatorias:

- `Fecha`
- `TipoRegistro`
- `ServicioActividad`
- `Servidor`
- `Estado`
- `Observaciones`

Reglas:

- En `TipoRegistro` escribe `Servicio` cuando sea un privilegio con servidor.
- En `TipoRegistro` escribe `Actividad` cuando sea una actividad general de la iglesia.
- `ServicioActividad` se selecciona desde la hoja `Servicios`.
- `Servidor` se selecciona desde la hoja `Lista Servidores`.
- En actividades puedes dejar `Servidor` vacío.
- Si una persona aparece 2 o más veces en la misma fecha con `TipoRegistro = Servicio`, la app mostrará alerta de doble privilegio. Sí se permite, pero queda visible para revisión.

Ejemplo:

| Fecha | TipoRegistro | ServicioActividad | Servidor | Estado | Observaciones |
|---|---|---|---|---|---|
| 2026-06-01 | Servicio | Multimedia | Julio Ochoa | Confirmado | |
| 2026-06-01 | Servicio | Alabanza | Clara | Pendiente | |
| 2026-06-01 | Actividad | Post | | Confirmado | Publicación Santa Cena |

### 6. Configuracion

Columnas obligatorias:

- `Parametro`
- `Valor`

Parámetros principales:

| Parametro | Valor |
|---|---|
| CantidadGrupos | 5 |
| FechaBaseRotacion | 2026-05-31 |
| GrupoBaseRotacion | 5 |
| InicioSemana | Domingo |
| FechaSemanaActual | Fórmula automática |
| GrupoActivoActual | Fórmula automática |

La rotación se calcula así:

- Semana del 31 de mayo al 6 de junio de 2026 = Grupo #5.
- La siguiente semana será Grupo #1.
- Luego Grupo #2, Grupo #3, Grupo #4, Grupo #5, y se repite el ciclo.

En Excel, `FechaSemanaActual` y `GrupoActivoActual` tienen fórmulas para verse dinámicos al abrir/recalcular el archivo. En la app, el cálculo también se hace automáticamente con Python, por lo que no depende de que Excel recalcule fórmulas.

## Ejecutar localmente en Windows

1. Instala Python desde https://www.python.org/downloads/
2. Abre la carpeta del proyecto.
3. En la barra de dirección del Explorador de Windows escribe `cmd` y presiona Enter.
4. Crea un entorno virtual:

```bash
python -m venv venv
```

5. Activa el entorno virtual:

```bash
venv\Scripts\activate
```

6. Instala las dependencias:

```bash
pip install -r requirements.txt
```

7. Ejecuta la app:

```bash
streamlit run app.py
```

## Publicar gratis en Streamlit Community Cloud

1. Crea un repositorio en GitHub, por ejemplo: `calendario-servicios-iglesia`.
2. Sube estos archivos al repositorio:
   - `app.py`
   - `requirements.txt`
   - `calendario_iglesia_datos.xlsx`
3. Entra a https://share.streamlit.io
4. Inicia sesión con GitHub.
5. Haz clic en **New app**.
6. Selecciona:
   - Repository: tu repositorio.
   - Branch: `main`.
   - Main file path: `app.py`.
7. Haz clic en **Deploy**.
8. Streamlit te dará un enlace para abrirlo desde la tablet.

## Cómo actualizar los datos

Opción sencilla:

1. Edita el Excel en tu computadora.
2. Súbelo nuevamente a GitHub con el mismo nombre: `calendario_iglesia_datos.xlsx`.
3. Streamlit Community Cloud actualizará la app cuando detecte el cambio.

Opción rápida dentro de la app:

- Usa el botón lateral **Subir archivo Excel**.
- Esto carga temporalmente ese Excel mientras la app está abierta.
- Para dejarlo fijo para todos, actualiza el archivo en GitHub.
