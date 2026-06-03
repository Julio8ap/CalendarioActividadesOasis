# Calendario de Servicios de Iglesia

Aplicación en Python con Streamlit para visualizar un calendario mensual de servicios, actividades y grupos de servidores de la iglesia.

## Archivos del proyecto

- `app.py`: aplicación principal.
- `calendario_iglesia_datos.xlsx`: base de datos en Excel.
- `requirements.txt`: librerías necesarias para Streamlit Cloud.
- `README.md`: instrucciones.

## Cómo funciona

La app lee directamente el archivo `calendario_iglesia_datos.xlsx`. No se muestra opción pública para subir archivos desde la página, porque la administración se realiza editando el Excel y subiendo los cambios al repositorio de GitHub.

## Hojas principales del Excel

- `Lista Servidores`: listado oficial de nombres.
- `Servidores`: vincula cada servidor con su grupo de servicio.
- `Servicios`: catálogo de servicios o privilegios disponibles.
- `Estados`: estados para actividades.
- `Registro Servicios`: alimenta el calendario.
- `Configuracion`: controla la rotación semanal de grupos.

## Registro Servicios

Cada fila representa un servicio o actividad.

Columnas esperadas:

- `Fecha`
- `TipoRegistro`: usar `Servicio` o `Actividad`
- `ServicioActividad`
- `Servidor`
- `Estado`
- `Observaciones`

Notas:

- Para `Servicio`, la app muestra la etiqueta del servicio dentro del día y permite expandirla para ver servidores.
- Para `Actividad`, la app muestra la actividad directamente dentro del día y conserva el estado.
- El estado ya no se muestra en los servicios; queda únicamente para actividades.
- Si una persona aparece en dos servicios el mismo día, se muestra alerta de doble privilegio.

## Rotación de grupos

La app usa la hoja `Configuracion` con estos parámetros:

- `CantidadGrupos`: 5
- `FechaReferenciaSemana`: 31/05/2026
- `GrupoReferencia`: 5

Con esta base, cada domingo la app calcula automáticamente el grupo activo y lo cicla del 1 al 5.

## Cómo ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo actualizar la app después de cambiar código o Excel

1. Guarda los cambios en `app.py` o en `calendario_iglesia_datos.xlsx`.
2. Abre VS Code en la carpeta del proyecto.
3. Abre la terminal.
4. Ejecuta:

```bash
git status
git add .
git commit -m "Actualizar calendario de servicios"
git push
```

Streamlit Community Cloud detectará el cambio en GitHub y actualizará la app publicada.

## Recomendación

Cuando solo cambies datos del calendario, edita únicamente `calendario_iglesia_datos.xlsx`, guarda el archivo y súbelo con `git add .`, `git commit` y `git push`.
