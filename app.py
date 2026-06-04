import calendar
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Calendario Actividades Oasis",
    page_icon="📅",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
LOCAL_EXCEL_PATH = BASE_DIR / "calendario_iglesia_datos.xlsx"
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


# =========================
# Diseño visual
# =========================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }
    .oasis-title {
        background: linear-gradient(135deg, #0f766e 0%, #0891b2 55%, #2563eb 100%);
        color: #ffffff;
        padding: 1rem 1.4rem;
        border-radius: 1.15rem;
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: .2px;
        box-shadow: 0 10px 30px rgba(15, 118, 110, .18);
        margin-bottom: .75rem;
        text-align: center;
    }
    div[data-testid="stMetric"], .metric-container {
        display: none !important;
    }
    .week-group {
        background: #0f766e;
        color: white;
        font-weight: 850;
        text-align: center;
        padding: 0.55rem;
        border-radius: 0.85rem;
        margin: 0.55rem 0 0.45rem 0;
        font-size: .95rem;
    }
    .date-header {
        font-weight: 900;
        color: #0f172a;
        font-size: .98rem;
        margin-bottom: .35rem;
        padding-bottom: .25rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .outside-month {
        color: #64748b;
    }
    .today-pill {
        display: inline-block;
        background: #fef3c7;
        color: #92400e;
        border-radius: 999px;
        padding: .05rem .35rem;
        font-size: .67rem;
        font-weight: 900;
        margin-left: .25rem;
    }
    .alert-chip {
        display: inline-block;
        background: #fee2e2;
        color: #991b1b;
        border-radius: 0.65rem;
        padding: 0.16rem 0.46rem;
        margin: 0.12rem 0 0.35rem 0;
        font-size: 0.76rem;
        font-weight: 850;
    }
    .activity-chip {
        display: block;
        background: #e0f2fe;
        color: #075985;
        border-radius: 0.65rem;
        padding: 0.22rem 0.48rem;
        margin: 0.16rem 0;
        font-size: 0.78rem;
        font-weight: 750;
        line-height: 1.15rem;
    }
    .activity-title {
        font-weight: 900;
        color: #0f766e;
        margin-top: 0.35rem;
        margin-bottom: 0.15rem;
        font-size: 0.84rem;
    }
    .small-muted {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-top: .25rem;
    }
    .person-line {
        font-size: .83rem;
        line-height: 1.23rem;
        color: #0f172a;
    }
    .source-ok {
        background: #dcfce7;
        color: #166534;
        border-radius: .7rem;
        padding: .5rem .65rem;
        font-size: .82rem;
        font-weight: 750;
    }
    .source-warn {
        background: #fef3c7;
        color: #92400e;
        border-radius: .7rem;
        padding: .5rem .65rem;
        font-size: .82rem;
        font-weight: 750;
    }
    /* Hace más compactos los expanders dentro de cada fecha */
    div[data-testid="stExpander"] details summary p {
        font-size: .82rem !important;
        font-weight: 850 !important;
    }
    div[data-testid="stExpander"] {
        margin-bottom: .18rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# Catálogos base
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


# =========================
# Lectura de datos
# =========================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


@st.cache_data(show_spinner=False, ttl=120)
def load_excel_from_path(path: str) -> dict:
    xls = pd.ExcelFile(path)
    return {sheet: normalize_columns(pd.read_excel(xls, sheet_name=sheet)) for sheet in xls.sheet_names}


@st.cache_data(show_spinner=False, ttl=120)
def load_google_public_excel(spreadsheet_id: str) -> dict:
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx"
    xls = pd.ExcelFile(url)
    return {sheet: normalize_columns(pd.read_excel(xls, sheet_name=sheet)) for sheet in xls.sheet_names}


@st.cache_data(show_spinner=False, ttl=120)
def load_google_private(spreadsheet_id: str, service_account_json: str) -> dict:
    import gspread
    from google.oauth2.service_account import Credentials

    credentials_info = json.loads(service_account_json)
    creds = Credentials.from_service_account_info(credentials_info, scopes=GOOGLE_SCOPES)
    client = gspread.authorize(creds)
    book = client.open_by_key(spreadsheet_id)

    data = {}
    for ws in book.worksheets():
        rows = ws.get_all_values()
        if not rows:
            data[ws.title] = pd.DataFrame()
            continue
        header = [str(c).strip() for c in rows[0]]
        body = rows[1:]
        data[ws.title] = normalize_columns(pd.DataFrame(body, columns=header))
    return data


def get_secret_value(*keys, default=None):
    current = st.secrets
    try:
        for key in keys:
            if hasattr(current, "get"):
                current = current.get(key)
            else:
                current = current[key]
            if current is None:
                return default
        return current
    except Exception:
        return default


def load_data_with_fallback() -> tuple[dict, str, str | None]:
    """Primero intenta Google Sheets. Si falla o no está configurado, usa Excel local."""
    google_enabled = bool(get_secret_value("google_sheets", "enabled", default=False))
    spreadsheet_id = get_secret_value("google_sheets", "spreadsheet_id", default=None)
    google_mode = str(get_secret_value("google_sheets", "mode", default="private")).lower().strip()

    if google_enabled and spreadsheet_id:
        try:
            service_account = get_secret_value("google_service_account", default=None)
            if service_account:
                data = load_google_private(spreadsheet_id, json.dumps(dict(service_account)))
                return data, "Google Sheets privado", None
            if google_mode == "public":
                data = load_google_public_excel(spreadsheet_id)
                return data, "Google Sheets público", None
            raise ValueError("Google Sheets está en modo privado, pero faltan las credenciales de google_service_account en Secrets.")
        except Exception as exc:
            try:
                data = load_excel_from_path(str(LOCAL_EXCEL_PATH))
                return data, "Excel local de respaldo", str(exc)
            except Exception as local_exc:
                st.error(
                    "No pude leer Google Sheets ni el Excel local de respaldo. "
                    f"Error Google: {exc}. Error Excel local: {local_exc}"
                )
                st.stop()

    try:
        data = load_excel_from_path(str(LOCAL_EXCEL_PATH))
        return data, "Excel local", None
    except Exception as exc:
        st.error(f"No pude leer el Excel local: {exc}")
        st.stop()


# =========================
# Preparación de datos
# =========================
def ensure_columns(df: pd.DataFrame, required: list[str], sheet_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"A la hoja '{sheet_name}' le faltan estas columnas: {', '.join(missing)}")
        st.stop()


def parse_date_value(value):
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        # En Google Sheets normalmente llega como texto dd/mm/yyyy o yyyy-mm-dd.
        return pd.to_datetime(value, dayfirst=True, errors="coerce").date()
    except Exception:
        return None


def get_config(config_df: pd.DataFrame) -> dict:
    cfg = {
        "CantidadGrupos": 5,
        "FechaReferenciaSemana": date(2026, 5, 31),
        "GrupoReferencia": 5,
    }

    if config_df is None or config_df.empty:
        return cfg

    ensure_columns(config_df, ["Parametro", "Valor"], "Configuracion")

    params = {}
    for _, row in config_df.iterrows():
        key = str(row.get("Parametro", "")).strip()
        value = row.get("Valor")
        if key:
            params[key] = value

    if pd.notna(params.get("CantidadGrupos")) and str(params.get("CantidadGrupos")).strip() != "":
        cfg["CantidadGrupos"] = int(float(params["CantidadGrupos"]))

    base_date = params.get("FechaBaseRotacion", params.get("FechaReferenciaSemana"))
    parsed_base_date = parse_date_value(base_date)
    if parsed_base_date:
        cfg["FechaReferenciaSemana"] = parsed_base_date

    base_group = params.get("GrupoBaseRotacion", params.get("GrupoReferencia"))
    if pd.notna(base_group) and str(base_group).strip() != "":
        cfg["GrupoReferencia"] = int(float(base_group))

    return cfg


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
    registro["Fecha"] = registro["Fecha"].apply(parse_date_value)
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


# =========================
# Lógica de calendario
# =========================
def start_of_week_sunday(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)


def active_group_for_week(week_start: date, cfg: dict) -> int:
    ref_week = start_of_week_sunday(cfg["FechaReferenciaSemana"])
    weeks_diff = (week_start - ref_week).days // 7
    total_groups = max(int(cfg["CantidadGrupos"]), 1)
    ref_group = int(cfg["GrupoReferencia"])
    return ((ref_group - 1 + weeks_diff) % total_groups) + 1


def month_weeks_full(year: int, month: int) -> list[list[date]]:
    cal = calendar.Calendar(firstweekday=6)
    return cal.monthdatescalendar(year, month)


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


def dia_nombre(d: date) -> str:
    return DIAS_ES[(d.weekday() + 1) % 7]


def render_day_card(d: date, selected_month: int, registro: pd.DataFrame):
    regs = registros_del_dia(registro, d)
    servicios = regs[regs["TipoRegistro"].str.lower() == "servicio"]
    actividades = regs[regs["TipoRegistro"].str.lower() == "actividad"]
    duplicados = detectar_duplicados_dia(regs)

    outside_class = " outside-month" if d.month != selected_month else ""
    today_label = '<span class="today-pill">Hoy</span>' if d == date.today() else ""

    with st.container(border=True):
        st.markdown(
            f'<div class="date-header{outside_class}">{dia_nombre(d)} {d.day:02d}/{d.month:02d}{today_label}</div>',
            unsafe_allow_html=True,
        )

        if not duplicados.empty:
            st.markdown('<span class="alert-chip">⚠ Doble privilegio</span>', unsafe_allow_html=True)

        if not servicios.empty:
            for servicio, group in servicios.groupby("ServicioActividad", sort=False):
                if not str(servicio).strip():
                    continue
                with st.expander(f"{servicio} · {len(group)}", expanded=False):
                    for _, row in group.iterrows():
                        servidor = row["Servidor"] if row["Servidor"] else "Sin servidor asignado"
                        obs = f" — {row['Observaciones']}" if row["Observaciones"] else ""
                        st.markdown(f'<div class="person-line">• {servidor}{obs}</div>', unsafe_allow_html=True)

        if not actividades.empty:
            st.markdown('<div class="activity-title">Actividades</div>', unsafe_allow_html=True)
            for _, row in actividades.iterrows():
                actividad = row["ServicioActividad"] if row["ServicioActividad"] else "Actividad sin nombre"
                estado = f" · {row['Estado']}" if row["Estado"] else ""
                obs = f" — {row['Observaciones']}" if row["Observaciones"] else ""
                st.markdown(
                    f'<span class="activity-chip">{actividad}{estado}{obs}</span>',
                    unsafe_allow_html=True,
                )

        if regs.empty:
            st.markdown('<div class="small-muted">Sin registros</div>', unsafe_allow_html=True)


# =========================
# Interfaz
# =========================
st.markdown('<div class="oasis-title">Calendario Actividades Oasis</div>', unsafe_allow_html=True)

filter_left, filter_mid, filter_right = st.columns([1, 1, 4])
today = date.today()
with filter_left:
    year = st.number_input("Año", min_value=2024, max_value=2035, value=today.year, step=1)
with filter_mid:
    month = st.selectbox(
        "Mes",
        options=list(MESES_ES.keys()),
        index=today.month - 1,
        format_func=lambda m: MESES_ES[m],
    )

with st.spinner("Cargando calendario..."):
    data, data_source, source_error = load_data_with_fallback()
    servidores_df, servicios_df, estados_df, registro_df, cfg = prepare_data(data)

with st.sidebar:
    st.header("📁 Fuente de datos")
    if source_error:
        st.markdown(
            f'<div class="source-warn">Usando respaldo local.<br>Google Sheets no cargó.</div>',
            unsafe_allow_html=True,
        )
        with st.expander("Ver detalle técnico", expanded=False):
            st.write(source_error)
    else:
        st.markdown(f'<div class="source-ok">Leyendo desde:<br>{data_source}</div>', unsafe_allow_html=True)

    st.divider()
    st.header("⚙️ Rotación")
    st.write(f"Cantidad de grupos: **{cfg['CantidadGrupos']}**")
    st.write(f"Semana base: **{cfg['FechaReferenciaSemana'].strftime('%d/%m/%Y')}**")
    st.write(f"Grupo base: **#{cfg['GrupoReferencia']}**")

    current_week_start = start_of_week_sunday(today)
    current_group = active_group_for_week(current_week_start, cfg)
    st.success(f"Esta semana sirve el Grupo #{current_group}")

st.markdown(f"### {MESES_ES[int(month)]} {int(year)}")

weeks = month_weeks_full(int(year), int(month))
for week in weeks:
    week_start = week[0]
    active_group = active_group_for_week(week_start, cfg)
    members = servidores_grupo(servidores_df, active_group)

    week_label, group_members = st.columns([4.4, 1.4])
    with week_label:
        st.markdown(
            f'<div class="week-group">Semana {week_start.strftime("%d/%m/%Y")} al {(week_start + timedelta(days=6)).strftime("%d/%m/%Y")} · Grupo #{active_group} con privilegio</div>',
            unsafe_allow_html=True,
        )
    with group_members:
        with st.expander(f"Servidores Grupo #{active_group}", expanded=False):
            if members:
                for member in members:
                    st.write(f"• {member}")
            else:
                st.info("Aún no hay servidores vinculados a este grupo.")

    day_cols = st.columns(7)
    for i, d in enumerate(week):
        with day_cols[i]:
            render_day_card(d, int(month), registro_df)
