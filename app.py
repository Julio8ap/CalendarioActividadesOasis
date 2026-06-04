import calendar
import html
from datetime import date, datetime, timedelta
from urllib.parse import quote

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Calendario Actividades Oasis",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# Estilos visuales
# =========================
st.markdown(
    """
    <style>
    :root {
        --oasis-bg: #ffffff;
        --oasis-card: #ffffff;
        --oasis-card-alt: #f8fafc;
        --oasis-text: #0f172a;
        --oasis-muted: #64748b;
        --oasis-border: #dbe4ea;
        --oasis-soft-border: #e2e8f0;
        --oasis-primary: #0f766e;
        --oasis-primary-2: #14b8a6;
        --oasis-primary-soft: #ccfbf1;
        --oasis-blue-soft: #e0f2fe;
        --oasis-blue-text: #075985;
        --oasis-alert-bg: #fee2e2;
        --oasis-alert-text: #991b1b;
        --oasis-activity-bg: #fef3c7;
        --oasis-activity-text: #92400e;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --oasis-bg: #0b1220;
            --oasis-card: #111827;
            --oasis-card-alt: #0f172a;
            --oasis-text: #f8fafc;
            --oasis-muted: #cbd5e1;
            --oasis-border: #334155;
            --oasis-soft-border: #475569;
            --oasis-primary: #5eead4;
            --oasis-primary-2: #2dd4bf;
            --oasis-primary-soft: #134e4a;
            --oasis-blue-soft: #0c4a6e;
            --oasis-blue-text: #bae6fd;
            --oasis-alert-bg: #7f1d1d;
            --oasis-alert-text: #fecaca;
            --oasis-activity-bg: #713f12;
            --oasis-activity-text: #fde68a;
        }
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    .oasis-title-wrap {
        border-radius: 1.2rem;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.75rem;
        background: linear-gradient(135deg, rgba(20,184,166,0.16), rgba(14,165,233,0.14));
        border: 1px solid var(--oasis-border);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    .oasis-main-title {
        font-size: clamp(1.7rem, 2.6vw, 2.45rem);
        font-weight: 900;
        letter-spacing: -0.02em;
        color: var(--oasis-text);
        line-height: 1.05;
        margin: 0;
    }

    .oasis-main-title span {
        color: var(--oasis-primary);
    }

    .month-heading {
        font-size: 1.28rem;
        font-weight: 900;
        color: var(--oasis-text);
        margin: 0.6rem 0 0.25rem 0;
    }

    .week-group {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(210px, 0.36fr);
        gap: 0.6rem;
        margin: 0.95rem 0 0.35rem 0;
        align-items: stretch;
    }

    .week-label, .week-members {
        border-radius: 0.95rem;
        border: 1px solid var(--oasis-border);
        background: var(--oasis-card);
        color: var(--oasis-text);
        padding: 0.62rem 0.75rem;
    }

    .week-label {
        font-weight: 900;
        background: linear-gradient(135deg, rgba(15,118,110,0.94), rgba(20,184,166,0.82));
        color: #ffffff;
        text-align: center;
    }

    .week-members details summary {
        cursor: pointer;
        color: var(--oasis-primary);
        font-weight: 900;
        list-style: none;
    }
    .week-members details summary::-webkit-details-marker {display:none;}

    .members-list {
        margin-top: 0.35rem;
        color: var(--oasis-text);
        font-size: 0.84rem;
        line-height: 1.35;
    }

    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 0.55rem;
        align-items: stretch;
    }

    .day-card {
        min-height: 255px;
        height: 100%;
        border: 1px solid var(--oasis-border);
        border-radius: 1rem;
        padding: 0.65rem;
        background: var(--oasis-card);
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        overflow-wrap: anywhere;
        color: var(--oasis-text);
    }

    .day-card.outside-month {
        background: var(--oasis-card-alt);
        opacity: 0.82;
    }

    .day-date {
        font-weight: 950;
        color: var(--oasis-text);
        font-size: 0.98rem;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.4rem;
    }

    .day-date .month-tag {
        color: var(--oasis-muted);
        font-size: 0.72rem;
        font-weight: 800;
        white-space: nowrap;
    }

    .alert-chip {
        display: inline-block;
        background: var(--oasis-alert-bg);
        color: var(--oasis-alert-text);
        border-radius: 999px;
        padding: 0.13rem 0.5rem;
        margin: 0.08rem 0 0.28rem 0;
        font-size: 0.75rem;
        font-weight: 900;
    }

    .service-details {
        margin: 0.28rem 0;
        border: 1px solid var(--oasis-soft-border);
        border-radius: 0.75rem;
        background: rgba(20,184,166,0.07);
        overflow: hidden;
    }

    .service-details summary {
        cursor: pointer;
        padding: 0.35rem 0.45rem;
        list-style: none;
        color: var(--oasis-primary);
        font-weight: 900;
        font-size: 0.85rem;
    }
    .service-details summary::-webkit-details-marker {display:none;}
    .service-details summary:before { content: "▸ "; color: var(--oasis-primary-2); }
    .service-details[open] summary:before { content: "▾ "; }

    .person-list {
        padding: 0 0.55rem 0.45rem 0.75rem;
        color: var(--oasis-text);
        font-size: 0.82rem;
        line-height: 1.32;
    }

    .person-line {
        margin: 0.1rem 0;
    }

    .activity-section {
        margin-top: 0.38rem;
        color: var(--oasis-text);
        font-size: 0.82rem;
    }

    .activity-title {
        color: var(--oasis-primary);
        font-weight: 900;
        margin-bottom: 0.2rem;
        font-size: 0.84rem;
    }

    .activity-chip {
        display: block;
        background: var(--oasis-activity-bg);
        color: var(--oasis-activity-text);
        border-radius: 0.62rem;
        padding: 0.25rem 0.42rem;
        margin: 0.16rem 0;
        font-weight: 800;
    }

    .activity-status {
        opacity: 0.85;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .empty-text {
        color: var(--oasis-muted);
        font-size: 0.82rem;
        margin-top: 0.35rem;
    }

    @media (max-width: 1200px) {
        .calendar-grid { gap: 0.42rem; }
        .day-card { padding: 0.52rem; min-height: 230px; }
        .week-group { grid-template-columns: 1fr; }
    }

    @media (max-width: 760px) {
        .calendar-grid { grid-template-columns: 1fr; }
        .day-card { min-height: auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Constantes
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
SHEETS = [
    "Lista Servidores",
    "Servidores",
    "Servicios",
    "Estados",
    "Meses",
    "Registro Servicios",
    "Configuracion",
]
LOCAL_EXCEL = "calendario_iglesia_datos.xlsx"


# =========================
# Carga de datos
# =========================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _empty_if_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.loc[:, [not str(c).startswith("Unnamed") for c in df.columns]]
    return df


@st.cache_data(show_spinner=False, ttl=180)
def load_local_excel(path: str) -> dict:
    xls = pd.ExcelFile(path)
    data = {}
    for sheet in xls.sheet_names:
        data[sheet] = _empty_if_unnamed(normalize_columns(pd.read_excel(xls, sheet_name=sheet)))
    return data


@st.cache_data(show_spinner=False, ttl=180)
def load_public_google_sheet(spreadsheet_id: str) -> dict:
    data = {}
    for sheet in SHEETS:
        url = (
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?"
            f"tqx=out:csv&sheet={quote(sheet)}"
        )
        data[sheet] = _empty_if_unnamed(normalize_columns(pd.read_csv(url)))
    return data


@st.cache_data(show_spinner=False, ttl=180)
def load_private_google_sheet(spreadsheet_id: str, service_account_info: dict) -> dict:
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    client = gspread.authorize(credentials)
    workbook = client.open_by_key(spreadsheet_id)

    data = {}
    for sheet in SHEETS:
        ws = workbook.worksheet(sheet)
        values = ws.get_all_records()
        data[sheet] = _empty_if_unnamed(normalize_columns(pd.DataFrame(values)))
    return data


def load_data_with_fallback() -> tuple[dict, str]:
    gs_cfg = st.secrets.get("google_sheets", {}) if hasattr(st, "secrets") else {}
    enabled = bool(gs_cfg.get("enabled", False))
    spreadsheet_id = str(gs_cfg.get("spreadsheet_id", "")).strip()
    mode = str(gs_cfg.get("mode", "public")).strip().lower()

    if enabled and spreadsheet_id:
        try:
            if mode == "private":
                service_account = dict(st.secrets.get("google_service_account", {}))
                if not service_account:
                    raise ValueError("Faltan las credenciales google_service_account en Secrets.")
                return load_private_google_sheet(spreadsheet_id, service_account), "Google Sheets privado"
            return load_public_google_sheet(spreadsheet_id), "Google Sheets público"
        except Exception as exc:
            st.sidebar.warning(
                "No se pudo leer Google Sheets. Usando Excel local como respaldo. "
                f"Detalle: {exc}"
            )

    return load_local_excel(LOCAL_EXCEL), "Excel local de respaldo"


# =========================
# Preparación de datos
# =========================
def ensure_columns(df: pd.DataFrame, required: list[str], sheet_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"A la hoja '{sheet_name}' le faltan estas columnas: {', '.join(missing)}")
        st.stop()


def parse_date_value(value, default: date) -> date:
    if pd.isna(value):
        return default
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return pd.to_datetime(value).date()


def get_config(config_df: pd.DataFrame) -> dict:
    cfg = {
        "CantidadGrupos": 5,
        "FechaBaseRotacion": date(2026, 5, 31),
        "GrupoBaseRotacion": 5,
    }
    if config_df is None or config_df.empty:
        return cfg

    ensure_columns(config_df, ["Parametro", "Valor"], "Configuracion")
    params = {}
    for _, row in config_df.iterrows():
        key = str(row.get("Parametro", "")).strip()
        if key:
            params[key] = row.get("Valor")

    if pd.notna(params.get("CantidadGrupos")):
        cfg["CantidadGrupos"] = int(float(params.get("CantidadGrupos")))

    # Nombres actuales y compatibilidad con versiones anteriores
    date_value = params.get("FechaBaseRotacion", params.get("FechaReferenciaSemana"))
    group_value = params.get("GrupoBaseRotacion", params.get("GrupoReferencia"))

    if date_value is not None and pd.notna(date_value):
        cfg["FechaBaseRotacion"] = parse_date_value(date_value, cfg["FechaBaseRotacion"])
    if group_value is not None and pd.notna(group_value):
        cfg["GrupoBaseRotacion"] = int(float(group_value))

    return cfg


def start_of_week_sunday(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)


def active_group_for_week(week_start: date, cfg: dict) -> int:
    ref_week = start_of_week_sunday(cfg["FechaBaseRotacion"])
    weeks_diff = (week_start - ref_week).days // 7
    total_groups = max(1, int(cfg["CantidadGrupos"]))
    ref_group = int(cfg["GrupoBaseRotacion"])
    return ((ref_group - 1 + weeks_diff) % total_groups) + 1


def month_weeks_full(year: int, month: int) -> list[list[date]]:
    cal = calendar.Calendar(firstweekday=6)
    return cal.monthdatescalendar(year, month)


def prepare_data(data: dict):
    servidores = normalize_columns(data.get("Servidores", pd.DataFrame()))
    servicios = normalize_columns(data.get("Servicios", pd.DataFrame()))
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
    for col in ["TipoRegistro", "ServicioActividad", "Servidor", "Estado", "Observaciones"]:
        registro[col] = registro[col].fillna("").astype(str).str.strip()
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

    return servidores, servicios, registro, get_config(config)


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


def e(value) -> str:
    return html.escape(str(value))


def day_name(d: date) -> str:
    return DIAS_ES[(d.weekday() + 1) % 7]


def render_day_card_html(d: date, selected_month: int, registro: pd.DataFrame) -> str:
    regs = registros_del_dia(registro, d)
    servicios = regs[regs["TipoRegistro"].str.lower() == "servicio"]
    actividades = regs[regs["TipoRegistro"].str.lower() == "actividad"]
    duplicados = detectar_duplicados_dia(regs)
    outside = " outside-month" if d.month != selected_month else ""
    month_tag = MESES_ES[d.month][:3]

    parts = [f'<div class="day-card{outside}">']
    parts.append(
        f'<div class="day-date"><span>{e(day_name(d))} {d.day:02d}/{d.month:02d}</span><span class="month-tag">{e(month_tag)}</span></div>'
    )

    if not duplicados.empty:
        alerts = "; ".join(
            f"{row['Servidor']} ({int(row['Cantidad'])})" for _, row in duplicados.iterrows()
        )
        parts.append(f'<div class="alert-chip" title="{e(alerts)}">⚠ Doble privilegio</div>')

    if not servicios.empty:
        for servicio, group in servicios.groupby("ServicioActividad", sort=False):
            servicio = str(servicio).strip()
            if not servicio:
                continue
            parts.append('<details class="service-details">')
            parts.append(f'<summary>{e(servicio)}</summary>')
            parts.append('<div class="person-list">')
            for _, row in group.iterrows():
                servidor = row["Servidor"] if row["Servidor"] else "Sin servidor asignado"
                obs = f" — {row['Observaciones']}" if row["Observaciones"] else ""
                parts.append(f'<div class="person-line">• {e(servidor)}{e(obs)}</div>')
            parts.append('</div></details>')

    if not actividades.empty:
        parts.append('<div class="activity-section"><div class="activity-title">Actividades</div>')
        for _, row in actividades.iterrows():
            act = row["ServicioActividad"] if row["ServicioActividad"] else "Actividad"
            obs = f" — {row['Observaciones']}" if row["Observaciones"] else ""
            estado = f'<div class="activity-status">{e(row["Estado"])}</div>' if row["Estado"] else ""
            parts.append(f'<div class="activity-chip">{e(act)}{e(obs)}{estado}</div>')
        parts.append('</div>')

    if regs.empty:
        parts.append('<div class="empty-text">Sin registros</div>')

    parts.append('</div>')
    return "".join(parts)


def render_week(week: list[date], month: int, registro: pd.DataFrame, servidores: pd.DataFrame, cfg: dict) -> None:
    week_start = start_of_week_sunday(week[0])
    active_group = active_group_for_week(week_start, cfg)
    members = servidores_grupo(servidores, active_group)
    member_html = "".join(f"<div>• {e(m)}</div>" for m in members) or "<div>Sin servidores vinculados.</div>"

    st.markdown(
        f"""
        <div class="week-group">
            <div class="week-label">Semana {week_start.strftime('%d/%m/%Y')} al {(week_start + timedelta(days=6)).strftime('%d/%m/%Y')} · Grupo #{active_group} con privilegio</div>
            <div class="week-members">
                <details>
                    <summary>Servidores Grupo #{active_group}</summary>
                    <div class="members-list">{member_html}</div>
                </details>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cards = "".join(render_day_card_html(d, month, registro) for d in week)
    st.markdown(f'<div class="calendar-grid">{cards}</div>', unsafe_allow_html=True)


# =========================
# Interfaz
# =========================
st.markdown(
    '<div class="oasis-title-wrap"><h1 class="oasis-main-title">Calendario Actividades <span>Oasis</span></h1></div>',
    unsafe_allow_html=True,
)

try:
    data, source_label = load_data_with_fallback()
except FileNotFoundError:
    st.error("No encontré el archivo de respaldo 'calendario_iglesia_datos.xlsx'. Colócalo junto a app.py.")
    st.stop()
except Exception as exc:
    st.error(f"No pude cargar los datos. Revisa Google Sheets o el Excel local. Detalle: {exc}")
    st.stop()

servidores_df, servicios_df, registro_df, cfg = prepare_data(data)

today = date.today()
filter_col_1, filter_col_2, filter_col_3 = st.columns([0.65, 0.85, 4.5])
with filter_col_1:
    year = st.number_input("Año", min_value=2024, max_value=2035, value=today.year, step=1)
with filter_col_2:
    month = st.selectbox(
        "Mes",
        options=list(MESES_ES.keys()),
        index=today.month - 1,
        format_func=lambda m: MESES_ES[m],
    )
with filter_col_3:
    st.markdown(f'<div class="month-heading">{MESES_ES[int(month)]} {int(year)}</div>', unsafe_allow_html=True)
    st.caption(f"Fuente de datos activa: {source_label}")

weeks = month_weeks_full(int(year), int(month))
for week in weeks:
    render_week(week, int(month), registro_df, servidores_df, cfg)

with st.sidebar:
    st.header("⚙️ Configuración")
    st.write(f"Fuente activa: **{source_label}**")
    st.write(f"Cantidad de grupos: **{cfg['CantidadGrupos']}**")
    st.write(f"Semana base: **{cfg['FechaBaseRotacion'].strftime('%d/%m/%Y')}**")
    st.write(f"Grupo base: **#{cfg['GrupoBaseRotacion']}**")
    current_week_start = start_of_week_sunday(today)
    current_group = active_group_for_week(current_week_start, cfg)
    st.success(f"Esta semana sirve el Grupo #{current_group}")
    st.caption("Los datos se administran desde Google Sheets o desde el Excel local de respaldo.")
