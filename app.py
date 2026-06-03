import calendar
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Calendario de Servicios Iglesia",
    page_icon="📅",
    layout="wide",
)


# =========================
# Configuración visual
# =========================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f766e;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .week-group {
        background: #0f766e;
        color: white;
        font-weight: 800;
        text-align: center;
        padding: 0.45rem;
        border-radius: 0.8rem;
        margin: 0.45rem 0 0.35rem 0;
    }
    .day-card {
        border: 1px solid #dbe4ea;
        border-radius: 0.9rem;
        padding: 0.65rem;
        min-height: 230px;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        overflow-wrap: break-word;
    }
    .day-card-muted {
        border: 1px solid #e5e7eb;
        border-radius: 0.9rem;
        padding: 0.65rem;
        min-height: 230px;
        background: #f8fafc;
        color: #94a3b8;
        overflow-wrap: break-word;
    }
    .day-number {
        font-weight: 900;
        color: #0f172a;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    .section-title {
        font-weight: 800;
        color: #0f766e;
        margin-top: 0.45rem;
        font-size: 0.92rem;
    }
    .person {
        font-size: 0.86rem;
        color: #0f172a;
        line-height: 1.25rem;
    }
    .activity {
        display: inline-block;
        background: #e0f2fe;
        color: #075985;
        border-radius: 0.6rem;
        padding: 0.13rem 0.45rem;
        margin: 0.12rem 0.12rem 0.12rem 0;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .alert-chip {
        display: inline-block;
        background: #fee2e2;
        color: #991b1b;
        border-radius: 0.6rem;
        padding: 0.13rem 0.45rem;
        margin: 0.12rem 0;
        font-size: 0.78rem;
        font-weight: 800;
    }
    .ok-chip {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        border-radius: 0.6rem;
        padding: 0.13rem 0.45rem;
        margin: 0.12rem 0;
        font-size: 0.78rem;
        font-weight: 800;
    }
    .small-muted {
        color: #64748b;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Utilidades
# =========================
MESES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

DIAS_ES = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia espacios en encabezados sin alterar nombres visibles."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


@st.cache_data(show_spinner=False)
def load_excel(file) -> dict:
    xls = pd.ExcelFile(file)
    data = {}
    for sheet in xls.sheet_names:
        data[sheet] = normalize_columns(pd.read_excel(xls, sheet_name=sheet))
    return data


def ensure_columns(df: pd.DataFrame, required: list[str], sheet_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(
            f"A la hoja '{sheet_name}' le faltan estas columnas: {', '.join(missing)}"
        )
        st.stop()


def _parse_config_date(value, default_value: date) -> date:
    """Convierte una fecha desde Excel a date de Python, con respaldo seguro."""
    if pd.isna(value):
        return default_value
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return pd.to_datetime(value).date()


def get_config(config_df: pd.DataFrame) -> dict:
    # La rotación se calcula desde una base fija:
    # semana del 31/05/2026 al 06/06/2026 = Grupo 5.
    cfg = {
        "CantidadGrupos": 5,
        "FechaBaseRotacion": date(2026, 5, 31),
        "GrupoBaseRotacion": 5,
    }

    if config_df is None or config_df.empty:
        cfg["FechaReferenciaSemana"] = cfg["FechaBaseRotacion"]
        cfg["GrupoReferencia"] = cfg["GrupoBaseRotacion"]
        return cfg

    ensure_columns(config_df, ["Parametro", "Valor"], "Configuracion")

    for _, row in config_df.iterrows():
        key = str(row.get("Parametro", "")).strip()
        value = row.get("Valor")

        if key == "CantidadGrupos" and pd.notna(value):
            cfg["CantidadGrupos"] = int(value)

        # Nuevos nombres recomendados
        elif key == "FechaBaseRotacion" and pd.notna(value):
            cfg["FechaBaseRotacion"] = _parse_config_date(value, cfg["FechaBaseRotacion"])
        elif key == "GrupoBaseRotacion" and pd.notna(value):
            cfg["GrupoBaseRotacion"] = int(value)

        # Compatibilidad con versiones anteriores del Excel
        elif key == "FechaReferenciaSemana" and pd.notna(value) and "FechaBaseRotacion" not in config_df["Parametro"].astype(str).tolist():
            cfg["FechaBaseRotacion"] = _parse_config_date(value, cfg["FechaBaseRotacion"])
        elif key == "GrupoReferencia" and pd.notna(value) and "GrupoBaseRotacion" not in config_df["Parametro"].astype(str).tolist():
            cfg["GrupoBaseRotacion"] = int(value)

    # Alias internos para no romper funciones anteriores.
    cfg["FechaReferenciaSemana"] = cfg["FechaBaseRotacion"]
    cfg["GrupoReferencia"] = cfg["GrupoBaseRotacion"]
    return cfg


def start_of_week_sunday(d: date) -> date:
    """Devuelve el domingo de la semana de la fecha recibida."""
    # Python weekday: lunes=0, domingo=6
    return d - timedelta(days=(d.weekday() + 1) % 7)


def active_group_for_week(week_start: date, cfg: dict) -> int:
    ref_week = start_of_week_sunday(cfg["FechaReferenciaSemana"])
    weeks_diff = (week_start - ref_week).days // 7
    total_groups = int(cfg["CantidadGrupos"])
    ref_group = int(cfg["GrupoReferencia"])
    return ((ref_group - 1 + weeks_diff) % total_groups) + 1


def month_weeks(year: int, month: int) -> list[list[date | None]]:
    """Matriz mensual iniciando domingo."""
    cal = calendar.Calendar(firstweekday=6)  # 6 = domingo
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        weeks.append([d if d.month == month else None for d in week])
    return weeks


def prepare_data(data: dict):
    servidores = normalize_columns(data.get("Servidores", pd.DataFrame()))
    servicios = normalize_columns(data.get("Servicios", pd.DataFrame()))
    estados = normalize_columns(data.get("Estados", pd.DataFrame()))
    registro = normalize_columns(data.get("Registro Servicios", pd.DataFrame()))
    config = normalize_columns(data.get("Configuracion", pd.DataFrame()))

    ensure_columns(servidores, ["Servidor", "Grupo"], "Servidores")
    ensure_columns(servicios, ["Servicio", "Categoria"], "Servicios")
    ensure_columns(
        registro,
        ["Fecha", "TipoRegistro", "ServicioActividad", "Servidor", "Estado", "Observaciones"],
        "Registro Servicios",
    )

    registro = registro.copy()
    registro["Fecha"] = pd.to_datetime(registro["Fecha"], errors="coerce").dt.date
    registro["TipoRegistro"] = registro["TipoRegistro"].fillna("").astype(str).str.strip()
    registro["ServicioActividad"] = (
        registro["ServicioActividad"].fillna("").astype(str).str.strip()
    )
    registro["Servidor"] = registro["Servidor"].fillna("").astype(str).str.strip()
    registro["Estado"] = registro["Estado"].fillna("").astype(str).str.strip()
    registro["Observaciones"] = registro["Observaciones"].fillna("").astype(str).str.strip()
    registro = registro[registro["Fecha"].notna()].copy()

    servidores = servidores.copy()
    servidores["Servidor"] = servidores["Servidor"].fillna("").astype(str).str.strip()
    servidores["Grupo"] = pd.to_numeric(servidores["Grupo"], errors="coerce")
    if "Activo" in servidores.columns:
        servidores["Activo"] = servidores["Activo"].fillna("Sí").astype(str).str.strip()
    else:
        servidores["Activo"] = "Sí"

    servicios = servicios.copy()
    servicios["Servicio"] = servicios["Servicio"].fillna("").astype(str).str.strip()
    servicios["Categoria"] = servicios["Categoria"].fillna("").astype(str).str.strip()

    # Validación visual: ServicioActividad debe existir en hoja Servicios.
    servicios_validos = set(servicios["Servicio"].dropna().astype(str).str.strip())
    usados = set(registro["ServicioActividad"].dropna().astype(str).str.strip())
    usados.discard("")
    no_encontrados = sorted(usados - servicios_validos)
    if no_encontrados:
        st.warning(
            "Estos valores de 'ServicioActividad' no existen en la hoja 'Servicios': "
            + ", ".join(no_encontrados)
            + ". Agrégalos a Servicios o corrige el registro."
        )

    cfg = get_config(config)

    return servidores, servicios, estados, registro, cfg


def registros_del_dia(registro: pd.DataFrame, d: date) -> pd.DataFrame:
    return registro[registro["Fecha"] == d].copy()


def detectar_duplicados_dia(regs_day: pd.DataFrame) -> pd.DataFrame:
    servicios_personas = regs_day[
        (regs_day["TipoRegistro"].str.lower() == "servicio")
        & (regs_day["Servidor"].str.strip() != "")
    ].copy()

    if servicios_personas.empty:
        return pd.DataFrame(columns=["Servidor", "Cantidad", "Privilegios"])

    grouped = (
        servicios_personas.groupby("Servidor")
        .agg(
            Cantidad=("ServicioActividad", "count"),
            Privilegios=("ServicioActividad", lambda x: ", ".join(sorted(set(map(str, x))))),
        )
        .reset_index()
    )
    return grouped[grouped["Cantidad"] > 1].copy()


def servidores_grupo(servidores: pd.DataFrame, group_number: int) -> list[str]:
    filtered = servidores[
        (servidores["Grupo"] == group_number)
        & (servidores["Servidor"] != "")
        & (~servidores["Activo"].str.lower().isin(["no", "inactivo", "false", "0"]))
    ]
    return filtered["Servidor"].dropna().astype(str).tolist()


def render_day_card(d: date | None, month: int, registro: pd.DataFrame):
    if d is None:
        st.markdown('<div class="day-card-muted">&nbsp;</div>', unsafe_allow_html=True)
        return

    regs = registros_del_dia(registro, d)
    servicios = regs[regs["TipoRegistro"].str.lower() == "servicio"]
    actividades = regs[regs["TipoRegistro"].str.lower() == "actividad"]
    duplicados = detectar_duplicados_dia(regs)

    html = f'<div class="day-card"><div class="day-number">{d.day}</div>'

    if not duplicados.empty:
        html += '<div class="alert-chip">⚠ Doble privilegio</div>'
    elif not regs.empty:
        html += '<div class="ok-chip">Con registros</div>'

    if not servicios.empty:
        for servicio, group in servicios.groupby("ServicioActividad"):
            if not str(servicio).strip():
                continue
            html += f'<div class="section-title">{servicio}</div>'
            for _, row in group.iterrows():
                servidor = row["Servidor"] if row["Servidor"] else "Sin servidor asignado"
                estado = f" · {row['Estado']}" if row["Estado"] else ""
                html += f'<div class="person">• {servidor}{estado}</div>'

    if not actividades.empty:
        html += '<div class="section-title">Actividades</div>'
        for _, row in actividades.iterrows():
            act = row["ServicioActividad"]
            obs = f": {row['Observaciones']}" if row["Observaciones"] else ""
            html += f'<span class="activity">{act}{obs}</span>'

    if regs.empty:
        html += '<div class="small-muted">Sin registros</div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_selected_day_detail(d: date, registro: pd.DataFrame):
    regs = registros_del_dia(registro, d)
    duplicados = detectar_duplicados_dia(regs)

    st.subheader(f"{DIAS_ES[(d.weekday() + 1) % 7]} {d.day:02d}/{d.month:02d}/{d.year}")

    if regs.empty:
        st.info("Este día todavía no tiene registros.")
        return

    if not duplicados.empty:
        for _, row in duplicados.iterrows():
            st.warning(
                f"⚠ {row['Servidor']} tiene {int(row['Cantidad'])} privilegios este día: {row['Privilegios']}"
            )

    servicios = regs[regs["TipoRegistro"].str.lower() == "servicio"]
    actividades = regs[regs["TipoRegistro"].str.lower() == "actividad"]

    if not servicios.empty:
        st.markdown("#### Privilegios / servicios")
        for servicio, group in servicios.groupby("ServicioActividad"):
            with st.expander(f"{servicio} ({len(group)} servidor/es)", expanded=True):
                for _, row in group.iterrows():
                    servidor = row["Servidor"] if row["Servidor"] else "Sin servidor asignado"
                    estado = row["Estado"] if row["Estado"] else "Sin estado"
                    obs = f" — {row['Observaciones']}" if row["Observaciones"] else ""
                    st.write(f"• **{servidor}** · {estado}{obs}")

    if not actividades.empty:
        st.markdown("#### Actividades")
        for _, row in actividades.iterrows():
            obs = f" — {row['Observaciones']}" if row["Observaciones"] else ""
            estado = f" · {row['Estado']}" if row["Estado"] else ""
            st.write(f"• **{row['ServicioActividad']}**{estado}{obs}")


# =========================
# Interfaz
# =========================
st.markdown('<div class="main-title">Calendario de Servicios de Iglesia</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Vista mensual dinámica alimentada desde Excel, con grupos semanales, privilegios, actividades y alertas por doble asignación.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("📁 Datos")
    st.caption("Puedes usar el Excel incluido en el repositorio o cargar uno actualizado.")

    uploaded = st.file_uploader(
        "Subir archivo Excel",
        type=["xlsx"],
        help="Debe tener las hojas: Servidores, Servicios, Estados, Registro Servicios y Configuracion.",
    )

    source_file = uploaded if uploaded is not None else "calendario_iglesia_datos.xlsx"

    st.divider()
    st.header("🗓️ Vista")
    today = date.today()
    year = st.number_input("Año", min_value=2024, max_value=2035, value=today.year, step=1)
    month = st.selectbox(
        "Mes",
        options=list(MESES_ES.keys()),
        index=today.month - 1,
        format_func=lambda m: MESES_ES[m],
    )

try:
    data = load_excel(source_file)
except FileNotFoundError:
    st.error(
        "No encontré el archivo 'calendario_iglesia_datos.xlsx'. "
        "Súbelo desde el panel izquierdo o colócalo en la misma carpeta que app.py."
    )
    st.stop()
except Exception as e:
    st.error(f"No pude leer el Excel. Revisa que no esté dañado y que sea .xlsx válido. Detalle: {e}")
    st.stop()

servidores_df, servicios_df, estados_df, registro_df, cfg = prepare_data(data)

# Filtrar por mes/año para métricas
first_day = date(int(year), int(month), 1)
last_day = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])
registro_mes = registro_df[
    (registro_df["Fecha"] >= first_day) & (registro_df["Fecha"] <= last_day)
].copy()

duplicados_mes = []
for d in pd.date_range(first_day, last_day, freq="D"):
    dup = detectar_duplicados_dia(registros_del_dia(registro_df, d.date()))
    for _, row in dup.iterrows():
        duplicados_mes.append(
            {
                "Fecha": d.date(),
                "Servidor": row["Servidor"],
                "Cantidad": row["Cantidad"],
                "Privilegios": row["Privilegios"],
            }
        )

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Registros del mes", len(registro_mes))
col_b.metric("Servicios asignados", len(registro_mes[registro_mes["TipoRegistro"].str.lower() == "servicio"]))
col_c.metric("Actividades", len(registro_mes[registro_mes["TipoRegistro"].str.lower() == "actividad"]))
col_d.metric("Alertas doble privilegio", len(duplicados_mes))

if duplicados_mes:
    with st.expander("⚠ Ver alertas de doble privilegio del mes", expanded=False):
        st.dataframe(pd.DataFrame(duplicados_mes), use_container_width=True, hide_index=True)

st.divider()

st.subheader(f"{MESES_ES[int(month)]} {int(year)}")

# Selector de días para expandir
dias_del_mes = [date(int(year), int(month), d) for d in range(1, last_day.day + 1)]
dias_con_texto = {
    d: f"{DIAS_ES[(d.weekday() + 1) % 7]} {d.day:02d}/{d.month:02d}" for d in dias_del_mes
}

selected_days = st.multiselect(
    "Selecciona uno o varios días para expandir privilegios",
    options=dias_del_mes,
    format_func=lambda d: dias_con_texto[d],
)

# Calendario
header_cols = st.columns(7)
for i, day_name in enumerate(DIAS_ES):
    header_cols[i].markdown(f"**{day_name}**")

weeks = month_weeks(int(year), int(month))
for week in weeks:
    visible_dates = [d for d in week if d is not None]
    if visible_dates:
        week_start = start_of_week_sunday(visible_dates[0])
    else:
        week_start = start_of_week_sunday(first_day)

    active_group = active_group_for_week(week_start, cfg)
    members = servidores_grupo(servidores_df, active_group)

    week_label, group_members = st.columns([4, 1.45])
    with week_label:
        st.markdown(
            f'<div class="week-group">Semana {week_start.strftime("%d/%m/%Y")} al {(week_start + timedelta(days=6)).strftime("%d/%m/%Y")} · Grupo #{active_group} con privilegio</div>',
            unsafe_allow_html=True,
        )
    with group_members:
        with st.expander(f"Servidores Grupo #{active_group}", expanded=False):
            if members:
                for m in members:
                    st.write(f"• {m}")
            else:
                st.info("Aún no hay servidores vinculados a este grupo.")

    day_cols = st.columns(7)
    for i, d in enumerate(week):
        with day_cols[i]:
            render_day_card(d, int(month), registro_df)

if selected_days:
    st.divider()
    st.header("Detalle expandido de días seleccionados")
    for d in selected_days:
        render_selected_day_detail(d, registro_df)
        st.divider()

with st.sidebar:
    st.divider()
    st.header("⚙️ Configuración de grupos")
    st.write(f"Cantidad de grupos: **{cfg['CantidadGrupos']}**")
    st.write(f"Base de rotación: **{cfg['FechaBaseRotacion'].strftime('%d/%m/%Y')} · Grupo #{cfg['GrupoBaseRotacion']}**")

    current_week_start = start_of_week_sunday(today)
    current_group = active_group_for_week(current_week_start, cfg)
    st.success(
        f"Esta semana ({current_week_start.strftime('%d/%m/%Y')} al "
        f"{(current_week_start + timedelta(days=6)).strftime('%d/%m/%Y')}) sirve el Grupo #{current_group}"
    )

    st.caption(
        "La app calcula automáticamente el grupo activo cada domingo. "
        "Para cambiar la rotación, edita CantidadGrupos, FechaBaseRotacion y GrupoBaseRotacion en la hoja Configuracion."
    )
