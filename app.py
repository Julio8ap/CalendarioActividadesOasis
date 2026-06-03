import calendar
import os
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
    .block-container {
        padding-top: 1.1rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
        max-width: 100%;
    }
    .main-title {
        font-size: 1.7rem;
        font-weight: 850;
        color: #0f766e;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        color: #475569;
        margin-bottom: 0.5rem;
        font-size: 0.92rem;
    }
    .top-selector-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.85rem;
        padding: 0.7rem 0.85rem 0.2rem 0.85rem;
        margin-bottom: 0.7rem;
    }
    .week-group {
        background: #0f766e;
        color: white;
        font-weight: 850;
        text-align: center;
        padding: 0.38rem;
        border-radius: 0.75rem;
        margin: 0.35rem 0 0.2rem 0;
        font-size: 0.9rem;
    }
    .day-header {
        font-weight: 900;
        color: #0f172a;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
        line-height: 1.15rem;
    }
    .day-header-muted {
        font-weight: 800;
        color: #94a3b8;
        font-size: 0.86rem;
        margin-bottom: 0.2rem;
    }
    .section-title {
        font-weight: 850;
        color: #0f766e;
        margin-top: 0.35rem;
        font-size: 0.82rem;
    }
    .person {
        font-size: 0.80rem;
        color: #0f172a;
        line-height: 1.1rem;
    }
    .activity {
        display: inline-block;
        background: #e0f2fe;
        color: #075985;
        border-radius: 0.5rem;
        padding: 0.10rem 0.35rem;
        margin: 0.08rem 0.08rem 0.08rem 0;
        font-size: 0.72rem;
        font-weight: 750;
    }
    .alert-chip {
        display: inline-block;
        background: #fee2e2;
        color: #991b1b;
        border-radius: 0.5rem;
        padding: 0.10rem 0.35rem;
        margin: 0.08rem 0;
        font-size: 0.72rem;
        font-weight: 850;
    }
    .ok-chip {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        border-radius: 0.5rem;
        padding: 0.10rem 0.35rem;
        margin: 0.08rem 0;
        font-size: 0.72rem;
        font-weight: 850;
    }
    .small-muted {
        color: #64748b;
        font-size: 0.76rem;
    }
    .day-name-head {
        text-align: center;
        font-weight: 850;
        color: #334155;
        font-size: 0.86rem;
        padding-bottom: 0.15rem;
    }
    .stExpander details {
        border-radius: 0.55rem !important;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 0.45rem 0.65rem;
        border-radius: 0.75rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.15rem;
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


def day_name_es(d: date) -> str:
    # Python weekday: lunes=0, domingo=6
    return DIAS_ES[(d.weekday() + 1) % 7]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


@st.cache_data(show_spinner=False)
def load_excel(path: str, modified_time: float) -> dict:
    # modified_time se usa para que Streamlit recargue el Excel cuando el archivo cambie.
    xls = pd.ExcelFile(path)
    data = {}
    for sheet in xls.sheet_names:
        data[sheet] = normalize_columns(pd.read_excel(xls, sheet_name=sheet))
    return data


def ensure_columns(df: pd.DataFrame, required: list[str], sheet_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"A la hoja '{sheet_name}' le faltan estas columnas: {', '.join(missing)}")
        st.stop()


def get_config(config_df: pd.DataFrame) -> dict:
    cfg = {
        "CantidadGrupos": 5,
        "FechaReferenciaSemana": date(2026, 5, 31),
        "GrupoReferencia": 5,
    }

    if config_df is None or config_df.empty:
        return cfg

    ensure_columns(config_df, ["Parametro", "Valor"], "Configuracion")

    for _, row in config_df.iterrows():
        key = str(row.get("Parametro", "")).strip()
        value = row.get("Valor")
        if key == "CantidadGrupos" and pd.notna(value):
            cfg[key] = int(value)
        elif key == "GrupoReferencia" and pd.notna(value):
            cfg[key] = int(value)
        elif key == "FechaReferenciaSemana" and pd.notna(value):
            if isinstance(value, pd.Timestamp):
                cfg[key] = value.date()
            elif isinstance(value, datetime):
                cfg[key] = value.date()
            elif isinstance(value, date):
                cfg[key] = value
            else:
                cfg[key] = pd.to_datetime(value).date()

    return cfg


def start_of_week_sunday(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)


def active_group_for_week(week_start: date, cfg: dict) -> int:
    ref_week = start_of_week_sunday(cfg["FechaReferenciaSemana"])
    weeks_diff = (week_start - ref_week).days // 7
    total_groups = int(cfg["CantidadGrupos"])
    ref_group = int(cfg["GrupoReferencia"])
    return ((ref_group - 1 + weeks_diff) % total_groups) + 1


def month_weeks(year: int, month: int) -> list[list[date | None]]:
    cal = calendar.Calendar(firstweekday=6)  # domingo
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
    registro["ServicioActividad"] = registro["ServicioActividad"].fillna("").astype(str).str.strip()
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


def render_service_expanders(servicios_dia: pd.DataFrame):
    for servicio, group in servicios_dia.groupby("ServicioActividad", sort=False):
        if not str(servicio).strip():
            continue
        with st.expander(f"{servicio} ({len(group)})", expanded=False):
            for _, row in group.iterrows():
                servidor = row["Servidor"] if row["Servidor"] else "Sin servidor asignado"
                obs = f" — {row['Observaciones']}" if row["Observaciones"] else ""
                st.markdown(f'<div class="person">• <b>{servidor}</b>{obs}</div>', unsafe_allow_html=True)


def render_activities(actividades_dia: pd.DataFrame):
    if actividades_dia.empty:
        return
    st.markdown('<div class="section-title">Actividades</div>', unsafe_allow_html=True)
    for _, row in actividades_dia.iterrows():
        act = row["ServicioActividad"]
        estado = f" · {row['Estado']}" if row["Estado"] else ""
        obs = f" · {row['Observaciones']}" if row["Observaciones"] else ""
        st.markdown(f'<span class="activity">{act}{estado}{obs}</span>', unsafe_allow_html=True)


def render_day_card(d: date | None, registro: pd.DataFrame):
    with st.container(border=True):
        if d is None:
            st.markdown('<div class="day-header-muted">&nbsp;</div>', unsafe_allow_html=True)
            st.markdown('<div class="small-muted">&nbsp;</div>', unsafe_allow_html=True)
            return

        regs = registros_del_dia(registro, d)
        servicios_dia = regs[regs["TipoRegistro"].str.lower() == "servicio"]
        actividades_dia = regs[regs["TipoRegistro"].str.lower() == "actividad"]
        duplicados = detectar_duplicados_dia(regs)

        st.markdown(
            f'<div class="day-header">{day_name_es(d)} {d.day:02d}</div>',
            unsafe_allow_html=True,
        )

        if not duplicados.empty:
            nombres = ", ".join(duplicados["Servidor"].astype(str).tolist())
            st.markdown(f'<span class="alert-chip">⚠ Doble privilegio: {nombres}</span>', unsafe_allow_html=True)
        elif not regs.empty:
            st.markdown('<span class="ok-chip">Con registros</span>', unsafe_allow_html=True)

        if not servicios_dia.empty:
            render_service_expanders(servicios_dia)

        render_activities(actividades_dia)

        if regs.empty:
            st.markdown('<div class="small-muted">Sin registros</div>', unsafe_allow_html=True)


# =========================
# Interfaz
# =========================
st.markdown('<div class="main-title">Calendario de Servicios de Iglesia</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Vista mensual alimentada desde Excel, con grupos semanales, servicios expandibles, actividades y alertas por doble asignación.</div>',
    unsafe_allow_html=True,
)

source_file = "calendario_iglesia_datos.xlsx"

try:
    modified_time = os.path.getmtime(source_file)
    data = load_excel(source_file, modified_time)
except FileNotFoundError:
    st.error(
        "No encontré el archivo 'calendario_iglesia_datos.xlsx'. "
        "Debe estar en la misma carpeta que app.py."
    )
    st.stop()
except Exception as e:
    st.error(f"No pude leer el Excel. Revisa que no esté dañado y que sea .xlsx válido. Detalle: {e}")
    st.stop()

servidores_df, servicios_df, estados_df, registro_df, cfg = prepare_data(data)

today = date.today()

with st.sidebar:
    st.header("📌 Información")
    st.write("La app lee los datos desde el archivo:")
    st.code(source_file)
    st.caption("Para actualizar servicios o actividades, edita el Excel y sube los cambios a GitHub.")

    st.divider()
    st.header("⚙️ Rotación de grupos")
    st.write(f"Cantidad de grupos: **{cfg['CantidadGrupos']}**")
    st.write(f"Semana referencia: **{cfg['FechaReferenciaSemana'].strftime('%d/%m/%Y')}**")
    st.write(f"Grupo referencia: **#{cfg['GrupoReferencia']}**")

    current_week_start = start_of_week_sunday(today)
    current_group = active_group_for_week(current_week_start, cfg)
    st.success(f"Esta semana sirve el Grupo #{current_group}")
    st.caption("Para cambiar la rotación, edita la hoja 'Configuracion' del Excel.")

# Selector compacto arriba
with st.container():
    st.markdown('<div class="top-selector-card">', unsafe_allow_html=True)
    sel_col1, sel_col2, sel_col3, sel_col4 = st.columns([1.1, 0.9, 1.2, 4.8])
    with sel_col1:
        month = st.selectbox(
            "Mes",
            options=list(MESES_ES.keys()),
            index=today.month - 1,
            format_func=lambda m: MESES_ES[m],
            label_visibility="visible",
        )
    with sel_col2:
        year = st.number_input("Año", min_value=2024, max_value=2035, value=today.year, step=1)
    with sel_col3:
        st.write("")
        st.write(f"**{MESES_ES[int(month)]} {int(year)}**")
    with sel_col4:
        st.write("")
        st.caption("Haz clic en cada etiqueta de servicio dentro del día para ver las personas asignadas.")
    st.markdown('</div>', unsafe_allow_html=True)

first_day = date(int(year), int(month), 1)
last_day = date(int(year), int(month), calendar.monthrange(int(year), int(month))[1])
registro_mes = registro_df[(registro_df["Fecha"] >= first_day) & (registro_df["Fecha"] <= last_day)].copy()

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

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Registros", len(registro_mes))
metric_col2.metric("Servicios", len(registro_mes[registro_mes["TipoRegistro"].str.lower() == "servicio"]))
metric_col3.metric("Actividades", len(registro_mes[registro_mes["TipoRegistro"].str.lower() == "actividad"]))
metric_col4.metric("Alertas", len(duplicados_mes))

if duplicados_mes:
    with st.expander("⚠ Alertas de doble privilegio del mes", expanded=False):
        st.dataframe(pd.DataFrame(duplicados_mes), use_container_width=True, hide_index=True)

# Encabezado de días
header_cols = st.columns(7)
for i, day_name in enumerate(DIAS_ES):
    header_cols[i].markdown(f'<div class="day-name-head">{day_name}</div>', unsafe_allow_html=True)

weeks = month_weeks(int(year), int(month))
for week in weeks:
    visible_dates = [d for d in week if d is not None]
    week_start = start_of_week_sunday(visible_dates[0]) if visible_dates else start_of_week_sunday(first_day)
    active_group = active_group_for_week(week_start, cfg)
    members = servidores_grupo(servidores_df, active_group)

    week_label, group_members = st.columns([4.5, 1.2])
    with week_label:
        st.markdown(
            f'<div class="week-group">Semana {week_start.strftime("%d/%m/%Y")} al {(week_start + timedelta(days=6)).strftime("%d/%m/%Y")} · Grupo #{active_group}</div>',
            unsafe_allow_html=True,
        )
    with group_members:
        with st.expander(f"Grupo #{active_group}", expanded=False):
            if members:
                for m in members:
                    st.write(f"• {m}")
            else:
                st.info("Sin servidores vinculados.")

    day_cols = st.columns(7)
    for i, d in enumerate(week):
        with day_cols[i]:
            render_day_card(d, registro_df)
