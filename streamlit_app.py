"""
================================================================================
PLATAFORMA DE INTELIGÊNCIA EPIDEMIOLÓGICA E ENTOMOLÓGICA DE ARBOVIROSES - ITAPORÃ / MS
Vigilância Ativa de Casos, Ovitrampas (Conta-Ovos Fiocruz), Clima, Predição e Gestão
DESIGN HIGH-TECH, TEMA ESCURO DE ALTO CONTRASTE, 7 ABAS ANALÍTICAS & MAPA EXPANDIDO
================================================================================
"""

import os
import json
from io import BytesIO
from typing import Optional, List, Dict, Any, Tuple
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium

import etl
import forecasting
import api_services
import auth
import cloud_storage
import unidades_saude

# Configuração Global da Página Streamlit (Otimizada para Celular e Telas Grandes)
st.set_page_config(
    page_title="Inteligência Epidemiológica & Entomológica | Itaporã-MS",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Carregamento de variáveis de ambiente (.env)
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ[_k.strip()] = _v.strip()

DEFAULT_MAPS_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "AIzaSyDoqwDBVxGLuy8HU75MPGqLWu9cWw4mjjw")

# ==============================================================================
# CSS MODERNO: FUNDO PRETO PURO (OLED BLACK), ULTRA-RESPONSIVO PARA CELULAR
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* =========================================================================
       TRAVAMENTO TOTAL DO FUNDO PRETO PURO (OLED #000000 - ZERO FUNDO CLARO)
       Elimina qualquer possibilidade de fundo branco ou texto invisível
       ========================================================================= */
    :root {
        color-scheme: dark !important;
        --background-color: #000000 !important;
        --secondary-background-color: #09090B !important;
        --text-color: #FFFFFF !important;
    }

    html, body, 
    .stApp, 
    .stApp.light, 
    .stApp[data-theme="light"], 
    [data-theme="light"], 
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stBottom"],
    .main,
    section.main {
        background-color: #000000 !important;
        background: #000000 !important;
        color: #FFFFFF !important;
        color-scheme: dark !important;
    }

    /* Barra Lateral (Sidebar) em Preto Ônix */
    section[data-testid="stSidebar"], [data-testid="stSidebar"] > div, [data-testid="stSidebarContent"] {
        background-color: #09090B !important;
        background: #09090B !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* FORÇAR VISIBILIDADE MÁXIMA DE TODOS OS TEXTOS E PARÁGRAFOS */
    p, span, label, div, li, a {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #FFFFFF !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.025em;
        color: #FFFFFF !important;
    }

    /* Forçar inputs, selects, multiselects e caixas de texto no modo escuro */
    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"],
    .stTextInput input,
    .stDateInput input {
        background-color: #141418 !important;
        color: #FFFFFF !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
    }

    /* Menus Dropdown Suspensa */
    ul[data-baseweb="menu"], [data-baseweb="popover"] {
        background-color: #141418 !important;
        color: #FFFFFF !important;
    }
    li[data-baseweb="menu-item"] {
        background-color: #141418 !important;
        color: #FFFFFF !important;
    }

    /* Expander / Acordeões */
    [data-testid="stExpander"] {
        background-color: #0D0D11 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2.5rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 98% !important;
    }

    /* Cabeçalho Tecnológico (Hero Banner) - Preto Ônix */
    .main-header {
        background: linear-gradient(135deg, #09090B 0%, #111114 50%, #18181B 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.4rem 2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.8);
    }
    .main-header h1 {
        font-size: 2.05rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #FFFFFF 0%, #60A5FA 50%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        color: #A1A1AA;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 0.3rem;
        margin-bottom: 0;
    }

    /* Cards de Métricas e Indicadores (Fundo Preto com Borda Fina de Alto Contraste) */
    .kpi-card {
        background: #0D0D11;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-left: 5px solid #3B82F6;
        box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.7);
        margin-bottom: 0.8rem;
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.9);
        border-color: rgba(255, 255, 255, 0.25);
    }
    .kpi-card.red { border-left-color: #EF4444; }
    .kpi-card.orange { border-left-color: #F97316; }
    .kpi-card.yellow { border-left-color: #F59E0B; }
    .kpi-card.green { border-left-color: #10B981; }
    .kpi-card.purple { border-left-color: #818CF8; }
    .kpi-card.blue { border-left-color: #38BDF8; }

    .kpi-title {
        font-family: 'Space Grotesk', sans-serif;
        color: #A1A1AA;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .kpi-value {
        font-family: 'Outfit', sans-serif;
        color: #FFFFFF;
        font-size: 2.15rem;
        font-weight: 800;
        margin: 0.2rem 0;
        letter-spacing: -0.03em;
        line-height: 1.15;
    }
    .kpi-sub {
        font-size: 0.82rem;
        font-weight: 500;
        color: #71717A;
    }
    .kpi-sub.up-bad { color: #F87171; font-weight: 700; }
    .kpi-sub.down-good { color: #34D399; font-weight: 700; }

    /* Badges Semafóricos */
    .badge-pill {
        font-family: 'Space Grotesk', sans-serif;
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-green { background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid #10B981; }
    .badge-yellow { background-color: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid #F59E0B; }
    .badge-orange { background-color: rgba(249, 115, 22, 0.15); color: #FB923C; border: 1px solid #F97316; }
    .badge-red { background-color: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid #EF4444; }

    /* Banners Integrados */
    .glass-card {
        background: #0D0D11;
        border-radius: 14px;
        padding: 1.1rem 1.6rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.7);
        margin-bottom: 1.2rem;
    }

    /* Abas Streamlit em Preto Ônix */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #09090B;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif;
        border-radius: 8px;
        padding: 8px 16px;
        color: #A1A1AA;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: 700;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.5);
    }

    /* Caixa do Boletim Oficial */
    .bulletin-box {
        background: #050507;
        border: 1px solid #27272A;
        border-left: 4px solid #3B82F6;
        border-radius: 12px;
        padding: 1.4rem;
        font-family: 'JetBrains Mono', Courier, monospace;
        font-size: 0.88rem;
        color: #FFFFFF;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.7);
    }

    /* =========================================================================
       RESPONSIVIDADE MOBILE COMPLETA (SMARTPHONES E TELAS PEQUENAS)
       ========================================================================= */
    @media (max-width: 900px) {
        .block-container {
            padding-top: 0.4rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
            max-width: 100% !important;
        }

        /* Banner Hero Compacto para Mobile */
        .main-header {
            padding: 0.85rem 1rem !important;
            border-radius: 12px !important;
            margin-bottom: 0.6rem !important;
        }
        .main-header h1 {
            font-size: 1.22rem !important;
            line-height: 1.2 !important;
        }
        .main-header p {
            font-size: 0.76rem !important;
        }

        /* Abas Deslizáveis Horizontalmente no Celular (Touch Scroll Fluido) */
        .stTabs [data-baseweb="tab-list"] {
            display: flex !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            gap: 6px !important;
            padding: 5px !important;
            border-radius: 10px !important;
        }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }
        .stTabs [data-baseweb="tab"] {
            flex-shrink: 0 !important;
            white-space: nowrap !important;
            padding: 8px 14px !important;
            font-size: 0.82rem !important;
            border-radius: 8px !important;
        }

        /* Colunas Responsivas: ocupação total em celulares estreitos */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.4rem !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Cards de Métricas (KPIs) Otimizados */
        .kpi-card {
            padding: 0.85rem 1rem !important;
            border-radius: 12px !important;
            margin-bottom: 0.45rem !important;
        }
        .kpi-value {
            font-size: 1.6rem !important;
            line-height: 1.15 !important;
        }
        .kpi-title {
            font-size: 0.72rem !important;
        }
        .kpi-sub {
            font-size: 0.76rem !important;
        }

        /* Boletim Oficial e Caixas de Texto */
        .bulletin-box {
            font-size: 0.76rem !important;
            padding: 0.85rem !important;
        }
        .glass-card {
            padding: 0.85rem 1rem !important;
            border-radius: 10px !important;
        }

        /* Mapas com Altura Confortável no Celular */
        iframe[title*="folium"], 
        iframe[title*="google_maps"], 
        .stIFrame,
        [data-testid="stIFrame"] {
            height: 360px !important;
            max-height: 360px !important;
            border-radius: 12px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Forçar Tema Preto Absoluto no DOM da aplicação
components.html("""
<script>
    (function() {
        const forceDark = function() {
            try {
                const doc = window.parent.document;
                if (doc) {
                    doc.documentElement.setAttribute('data-theme', 'dark');
                    doc.documentElement.style.colorScheme = 'dark';
                    doc.documentElement.style.backgroundColor = '#000000';
                    if (doc.body) {
                        doc.body.style.backgroundColor = '#000000';
                        doc.body.style.color = '#FFFFFF';
                        doc.body.classList.add('dark');
                    }
                }
            } catch (e) {}
        };
        forceDark();
        setTimeout(forceDark, 200);
        setTimeout(forceDark, 800);
        setTimeout(forceDark, 2000);
    })();
</script>
""", height=0, width=0)


# ==============================================================================
# CONTROLE DE ACESSO E AUTENTICAÇÃO SEGURA (RBAC)
# ==============================================================================
# Por padrão, permite ACESSO LIVRE (Sem Senha) para consulta pública imediata.
# Se require_auth estiver ativo nos segredos, exige a tela de login.
if not auth.check_authentication():
    if auth.is_auth_required():
        auth.render_login_screen()
        st.stop()
    else:
        auth.login_as_guest()


# ==============================================================================
# CARREGAMENTO E CACHE DOS DADOS (NUVEM / PARQUET + APIS EXTERNAS)
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_base_sinan_data() -> pd.DataFrame:
    """
    Carrega o dataset consolidado .parquet do Supabase Storage ou cache local.
    Se ainda não existir na nuvem, compila a partir dos dados nativos e salva no bucket.
    """
    df, src_msg = cloud_storage.carregar_base_consolidada()
    if df is not None and not df.empty:
        df = unidades_saude.enriquecer_dataframe_com_unidades(df)
        return df

    # Fallback inicial: compilar das planilhas nativas e persistir na nuvem
    df_init = etl.load_initial_data(os.path.dirname(os.path.abspath(__file__)))
    if df_init is not None and not df_init.empty:
        df_init = unidades_saude.enriquecer_dataframe_com_unidades(df_init)
        cloud_storage.salvar_base_consolidada(df_init)
    return df_init


@st.cache_data(ttl=3600, show_spinner=False)
def load_cached_infodengue() -> dict:
    """Busca dados de alerta e Rt na API do InfoDengue (Fiocruz)."""
    return api_services.fetch_infodengue_data()


@st.cache_data(ttl=3600, show_spinner=False)
def load_cached_weather() -> pd.DataFrame:
    """Busca série meteorológica no Open-Meteo (Archive + Forecast)."""
    return api_services.fetch_open_meteo_weather()


@st.cache_data(ttl=3600, show_spinner=False)
def load_cached_contaovos(token: Optional[str] = None) -> dict:
    """Busca dados entomológicos de ovitrampas na API Conta-Ovos Fiocruz."""
    return api_services.fetch_contaovos_data(api_token=token)


# ==============================================================================
# COMPONENTE GOOGLE MAPS PLATFORM (CASOS CLÍNICOS + OVITRAMPAS)
# ==============================================================================
def render_google_maps_html(
    df_map: pd.DataFrame,
    df_traps: Optional[pd.DataFrame] = None,
    api_key: str = "",
    tipo_visualizacao: str = "Ambos (Calor + Marcadores)",
    coord_col_lat: str = "LAT",
    coord_col_lon: str = "LON",
    show_traps_layer: bool = True
) -> str:
    """
    Renderiza aplicação Google Maps JavaScript API com camada dupla: Casos e Ovitrampas.
    Doc: https://developers.google.com/maps/documentation/javascript/overview?utm_campaign=gmp_git_agentskills_v1
    """
    sample = df_map.head(1500) if len(df_map) > 1500 else df_map
    cases_list = []
    for _, row in sample.iterrows():
        lat_v = row.get(coord_col_lat)
        lon_v = row.get(coord_col_lon)
        if pd.isna(lat_v) or pd.isna(lon_v):
            continue
        
        is_conf = row.get("STATUS_CASO") == "Confirmado"
        is_severe = row.get("TEM_SINAL_GRAVE", False) or "Alarme" in str(row.get("CLASSI_FIN_DESC"))
        weight = 5.0 if is_severe else (3.0 if is_conf else 1.0)
        
        cases_list.append({
            "lat": float(lat_v),
            "lng": float(lon_v),
            "weight": weight,
            "notific": str(row.get("NU_NOTIFIC", "")),
            "agravo": str(row.get("AGRAVO_TIPO", "Dengue")),
            "status": str(row.get("STATUS_CASO", "Desconhecido")),
            "classi": str(row.get("CLASSI_FIN_DESC", "")),
            "bairro": str(row.get("NM_BAIRRO_NORM", "N/I")),
            "rua": str(row.get("NM_LOGRADO_NORM", "N/I")),
            "vinculo": str(row.get("TIPO_VINCULO", "Residente Autóctone")),
            "idade": str(round(row["IDADE_ANOS"])) if pd.notna(row.get("IDADE_ANOS")) else "N/I",
            "sexo": str(row.get("SEXO_DESC", "N/I")),
            "data": row["DT_NOTIFIC"].strftime("%d/%m/%Y") if pd.notna(row.get("DT_NOTIFIC")) else "N/I"
        })

    traps_list = []
    if show_traps_layer and df_traps is not None and not df_traps.empty:
        for _, t in df_traps.iterrows():
            ovos = int(t.get("ovos_semana_atual", 0))
            if ovos >= 150:
                t_color = "#EF4444"
            elif ovos >= 80:
                t_color = "#F97316"
            elif ovos >= 40:
                t_color = "#F59E0B"
            else:
                t_color = "#10B981"

            traps_list.append({
                "lat": float(t["lat"]),
                "lng": float(t["lon"]),
                "trap_id": str(t["trap_id"]),
                "bairro": str(t["bairro"]),
                "ovos": ovos,
                "color": t_color
            })

    cases_json = json.dumps(cases_list)
    traps_json = json.dumps(traps_list)

    units_list = []
    for cnes_code, u_info in unidades_saude.UNIDADES_SAUDE_ITAPORA.items():
        n_casos = int((df_map["CNES_UNIDADE"] == cnes_code).sum()) if "CNES_UNIDADE" in df_map.columns else 0
        units_list.append({
            "cnes": cnes_code,
            "nome": u_info["nome"],
            "sigla": u_info["sigla"],
            "tipo": u_info["tipo"],
            "endereco": u_info["endereco_completo"],
            "horario": u_info["horario"],
            "telefones": u_info["telefones"],
            "responsavel": u_info["responsavel"],
            "lat": float(u_info["lat"]),
            "lng": float(u_info["lon"]),
            "casos": n_casos,
            "cor": u_info.get("cor_marcador", "#0284C7")
        })
    units_json = json.dumps(units_list)

    show_heat_init = "true" if ("Calor" in tipo_visualizacao or "Ambos" in tipo_visualizacao) else "false"
    show_markers_init = "true" if ("Marcadores" in tipo_visualizacao or "Ambos" in tipo_visualizacao) else "false"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Google Maps - Vigilância Integrada Itaporã</title>
    <style>
        html, body {{ height: 100%; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0A0F1D; color: #F8FAFC; }}
        #map {{ height: 100%; width: 100%; border-radius: 12px; }}
        .floating-panel {{
            position: absolute; top: 14px; left: 14px; z-index: 5;
            background: rgba(11, 17, 32, 0.94); border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 9px 16px; border-radius: 10px; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5);
            font-size: 13px; display: flex; gap: 8px; align-items: center; backdrop-filter: blur(8px);
            flex-wrap: wrap;
        }}
        .floating-panel button {{
            background: #2563EB; color: #FFFFFF; border: none; padding: 6px 12px;
            border-radius: 6px; font-weight: 700; cursor: pointer; transition: 0.2s ease;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35); font-size: 12px;
        }}
        .floating-panel button:hover {{ background: #1D4ED8; }}
        .gm-style-iw {{ background-color: #111827 !important; color: #F8FAFC !important; border-radius: 10px !important; box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important; padding: 6px !important; border: 1px solid rgba(255,255,255,0.1); }}
        .gm-style-iw-d {{ overflow: auto !important; color: #F8FAFC !important; }}
        .gm-style-iw-tc::after {{ background: #111827 !important; }}
    </style>
</head>
<body>
    <div class="floating-panel">
        <button id="toggleHeat">Calor de Casos</button>
        <button id="toggleMarkers">Casos Clínicos</button>
        <button id="toggleUnits" style="background:#0284C7;">🏥 Unidades de Saúde ({len(units_list)})</button>
        <button id="toggleTraps" style="background:#10B981;">Ovitrampas (Ovos)</button>
        <span style="color: #94A3B8; font-weight: 600; margin-left: 6px;">Casos: <strong style="color: #38BDF8;">{len(cases_list)}</strong> | Armadilhas: <strong style="color: #10B981;">{len(traps_list)}</strong></span>
    </div>
    <div id="map"></div>

    <script>
        let map, heatmap, markers = [], trapMarkers = [], unitMarkers = [];
        const casesData = {cases_json};
        const trapsData = {traps_json};
        const unitsData = {units_json};
        let heatVisible = {show_heat_init};
        let markersVisible = {show_markers_init};
        let trapsVisible = true;
        let unitsVisible = true;

        function initMap() {{
            const itaporaCenter = {{ lat: -22.0803, lng: -54.7892 }};
            map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 14,
                center: itaporaCenter,
                mapTypeId: 'roadmap',
                styles: [
                    {{ "elementType": "geometry", "stylers": [{{ "color": "#111827" }}] }},
                    {{ "elementType": "labels.text.fill", "stylers": [{{ "color": "#94a3b8" }}] }},
                    {{ "elementType": "labels.text.stroke", "stylers": [{{ "color": "#0b1120" }}] }},
                    {{ "featureType": "administrative.locality", "elementType": "labels.text.fill", "stylers": [{{ "color": "#38bdf8" }}] }},
                    {{ "featureType": "poi", "stylers": [{{ "visibility": "off" }}] }},
                    {{ "featureType": "road", "elementType": "geometry", "stylers": [{{ "color": "#1e293b" }}] }},
                    {{ "featureType": "road", "elementType": "geometry.stroke", "stylers": [{{ "color": "#0f172a" }}] }},
                    {{ "featureType": "road.highway", "elementType": "geometry", "stylers": [{{ "color": "#334155" }}] }},
                    {{ "featureType": "water", "elementType": "geometry", "stylers": [{{ "color": "#0a1128" }}] }}
                ]
            }});

            const heatPoints = casesData.map(c => ({{
                location: new google.maps.LatLng(c.lat, c.lng),
                weight: c.weight
            }}));

            heatmap = new google.maps.visualization.HeatmapLayer({{
                data: heatPoints,
                map: heatVisible ? map : null,
                radius: 28,
                opacity: 0.8,
                gradient: [
                    'rgba(0, 255, 255, 0)',
                    'rgba(56, 189, 248, 0.7)',
                    'rgba(16, 185, 129, 0.85)',
                    'rgba(245, 158, 11, 0.95)',
                    'rgba(239, 68, 68, 0.98)',
                    'rgba(220, 38, 38, 1)'
                ]
            }});

            const infoWindow = new google.maps.InfoWindow();

            // Marcadores de Casos Humanos
            casesData.forEach(c => {{
                let pinColor = c.agravo === 'Chikungunya' ? '#818CF8' : '#F43F5E';
                if (c.status === 'Descartado') pinColor = '#64748B';

                const marker = new google.maps.Marker({{
                    position: {{ lat: c.lat, lng: c.lng }},
                    map: markersVisible ? map : null,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 5,
                        fillColor: pinColor,
                        fillOpacity: 0.9,
                        strokeWeight: 1.5,
                        strokeColor: '#FFFFFF'
                    }}
                }});

                marker.addListener('click', () => {{
                    const content = `
                        <div style="font-size:12px; line-height:1.45; font-family:'Plus Jakarta Sans',sans-serif;">
                            <strong style="color:#38BDF8; font-size:13px;">${{c.agravo}} - ${{c.classi}}</strong><br>
                            <b>Ficha:</b> ${{c.notific}} | <b>Data:</b> ${{c.data}}<br>
                            <b>Vínculo:</b> <span style="color:#FDE68A; font-weight:700;">${{c.vinculo}}</span><br>
                            <b>Bairro:</b> ${{c.bairro}}<br>
                            <b>Logradouro:</b> ${{c.rua}}<br>
                            <b>Status:</b> <b>${{c.status}}</b>
                        </div>
                    `;
                    infoWindow.setContent(content);
                    infoWindow.open(map, marker);
                }});
                markers.push(marker);
            }});

            // Marcadores de Unidades de Saúde Notificadoras Oficiais (CNES)
            unitsData.forEach(u => {{
                const uMarker = new google.maps.Marker({{
                    position: {{ lat: u.lat, lng: u.lng }},
                    map: unitsVisible ? map : null,
                    zIndex: 999,
                    title: u.nome,
                    icon: {{
                        path: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-4H7v-2h4V7h2v4h4v2h-4v4z',
                        scale: 1.6,
                        fillColor: u.cor || '#0284C7',
                        fillOpacity: 1.0,
                        strokeWeight: 2.0,
                        strokeColor: '#FFFFFF',
                        anchor: new google.maps.Point(12, 12)
                    }}
                }});

                uMarker.addListener('click', () => {{
                    const content = `
                        <div style="font-size:12px; line-height:1.45; font-family:'Plus Jakarta Sans',sans-serif; min-width:270px; color:#F8FAFC;">
                            <div style="background:#1E3A8A; padding:7px 10px; border-radius:6px; margin-bottom:8px; border:1px solid #3B82F6;">
                                <span style="font-size:10px; text-transform:uppercase; color:#93C5FD; font-weight:700;">🏥 UNIDADE DE SAÚDE • CNES ${{u.cnes}}</span><br>
                                <strong style="color:#FFFFFF; font-size:13px;">${{u.nome}}</strong>
                            </div>
                            <b>Tipo:</b> ${{u.tipo}}<br>
                            <b>Endereço:</b> <span style="color:#FDE68A; font-weight:600;">${{u.endereco}}</span><br>
                            <b>Horário:</b> ${{u.horario}}<br>
                            <b>Telefones:</b> ${{u.telefones}}<br>
                            <b>Responsável:</b> ${{u.responsavel}}<br>
                            <div style="margin-top:8px; padding-top:6px; border-top:1px solid rgba(255,255,255,0.15); color:#94A3B8;">
                                Notificações Registradas: <strong style="color:#38BDF8; font-size:14px;">${{u.casos.toLocaleString('pt-BR')}}</strong> casos
                            </div>
                        </div>
                    `;
                    infoWindow.setContent(content);
                    infoWindow.open(map, uMarker);
                }});
                unitMarkers.push(uMarker);
            }});

            // Marcadores de Ovitrampas (Vigilância Entomológica)
            trapsData.forEach(t => {{
                const trapMarker = new google.maps.Marker({{
                    position: {{ lat: t.lat, lng: t.lng }},
                    map: trapsVisible ? map : null,
                    icon: {{
                        path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                        scale: 5,
                        rotation: 180,
                        fillColor: t.color,
                        fillOpacity: 1.0,
                        strokeWeight: 1.5,
                        strokeColor: '#FFFFFF'
                    }}
                }});

                trapMarker.addListener('click', () => {{
                    const content = `
                        <div style="font-size:12px; line-height:1.45; font-family:'Plus Jakarta Sans',sans-serif;">
                            <strong style="color:#10B981; font-size:13px;">🦟 Ovitrampa: ${{t.trap_id}}</strong><br>
                            <b>Bairro:</b> ${{t.bairro}}<br>
                            <b>Ovos Contados na Semana:</b> <span style="font-size:14px; font-weight:800; color:${{t.color}};">${{t.ovos}} ovos</span><br>
                            <b>Status da Palheta:</b> ${{t.ovos > 0 ? '<span style="color:#EF4444;font-weight:700;">POSITIVA</span>' : '<span style="color:#10B981;font-weight:700;">NEGATIVA</span>'}}<br>
                            <small style="color:#94A3B8;">Fonte: Conta-Ovos Fiocruz</small>
                        </div>
                    `;
                    infoWindow.setContent(content);
                    infoWindow.open(map, trapMarker);
                }});
                trapMarkers.push(trapMarker);
            }});

            document.getElementById('toggleHeat').addEventListener('click', () => {{
                heatVisible = !heatVisible;
                heatmap.setMap(heatVisible ? map : null);
            }});

            document.getElementById('toggleMarkers').addEventListener('click', () => {{
                markersVisible = !markersVisible;
                markers.forEach(m => m.setMap(markersVisible ? map : null));
            }});

            document.getElementById('toggleUnits').addEventListener('click', () => {{
                unitsVisible = !unitsVisible;
                unitMarkers.forEach(m => m.setMap(unitsVisible ? map : null));
                document.getElementById('toggleUnits').style.opacity = unitsVisible ? '1' : '0.4';
            }});

            document.getElementById('toggleTraps').addEventListener('click', () => {{
                trapsVisible = !trapsVisible;
                trapMarkers.forEach(m => m.setMap(trapsVisible ? map : null));
            }});
        }}
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=visualization&callback=initMap"></script>
</body>
</html>"""
    return html


# ==============================================================================
# INICIALIZAÇÃO DE ESTADO E PIPELINE DE DADOS
# ==============================================================================
if "consolidated_df" not in st.session_state:
    st.session_state["consolidated_df"] = load_base_sinan_data()
if "last_upload_info" not in st.session_state:
    st.session_state["last_upload_info"] = None
if "contaovos_token" not in st.session_state:
    st.session_state["contaovos_token"] = ""

df_full = st.session_state["consolidated_df"]

# ==============================================================================
# BARRA LATERAL (INGESTÃO CONTÍNUA, UPSERT & FILTROS GLOBAIS)
# ==============================================================================
with st.sidebar:
    # 1. Identificação do Usuário e Perfil (RBAC)
    auth.render_user_sidebar_status()

    # Indicador de Status da Nuvem
    if cloud_storage.is_cloud_available():
        st.markdown("<p style='font-size:0.75rem; color:#34D399; margin-top:-10px; margin-bottom:12px;'>☁️ <strong>Nuvem Ativa:</strong> Supabase Storage Conectado</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:0.75rem; color:#94A3B8; margin-top:-10px; margin-bottom:12px;'>💻 <strong>Modo Local:</strong> Persistência em Parquet Ativa</p>", unsafe_allow_html=True)

    # 2. Área de Ingestão de Dados (Restrita ao Gestor / Admin)
    if auth.is_admin():
        st.markdown("### 📁 Ingestão & Atualização")
        st.markdown("<p style='font-size:0.82rem; color:#94A3B8;'>Upload de planilhas SINAN com upsert automático e persistência em nuvem.</p>", unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Adicionar Planilhas SINAN",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            help="Arraste novas notificações ou arquivos anuais de Dengue e Chikungunya."
        )

        if uploaded_files:
            if st.button("🚀 Processar e Integrar Arquivos", use_container_width=True):
                with st.spinner("Processando planilhas, persistindo na nuvem e aplicando regras do SINAN..."):
                    # Salva cópia bruta de cada planilha enviada no bucket
                    for up_file in uploaded_files:
                        cloud_storage.salvar_planilha_nuvem(up_file.getvalue(), up_file.name)

                    # Deduplica e atualiza
                    updated_df, added, modified = etl.process_uploaded_files(uploaded_files, st.session_state["consolidated_df"])
                    st.session_state["consolidated_df"] = updated_df
                    st.session_state["last_upload_info"] = {"added": added, "modified": modified, "time": datetime.datetime.now().strftime("%H:%M:%S")}
                    
                    # Salva a base consolidada .parquet atualizada no Supabase Storage
                    cloud_storage.salvar_base_consolidada(updated_df)
                    st.cache_data.clear()
                    st.toast(f"✅ Base persistida na Nuvem! +{added} novos | {modified} atualizados.", icon="☁️")
                    st.rerun()

        if st.session_state["last_upload_info"]:
            u = st.session_state["last_upload_info"]
            st.caption(f"Último upload às {u['time']}: +{u['added']} novos, {u['modified']} alterados.")

        st.markdown(f"**Base Consolidada:** `{len(df_full):,} fichas carregadas`")

        if st.button("🔄 Atualizar e Reprocessar Painel", use_container_width=True):
            st.cache_data.clear()
            st.session_state["consolidated_df"] = load_base_sinan_data()
            st.toast(f"Painel reprocessado! Base consolidada com {len(st.session_state['consolidated_df']):,} casos.", icon="✨")
            st.rerun()
    else:
        st.info("🔒 **Modo Consulta (Visualizador):** Visualização em tempo real das 7 abas e mapas. Upload restrito ao Gestor.")
        st.markdown(f"**Base Consolidada:** `{len(df_full):,} fichas carregadas`")

    st.markdown("---")
    st.markdown("### 🔍 Filtros Globais")

    # 1. Filtro de Agravo
    sel_agravo = st.selectbox(
        "Agravo Epidemiológico",
        ["Todos", "Dengue", "Chikungunya"],
        index=0
    )

    # 2. Filtro de Anos
    anos_disponiveis = sorted(df_full["NU_ANO"].dropna().unique().astype(int)) if not df_full.empty else [2023, 2024, 2025, 2026]
    sel_anos = st.multiselect(
        "Anos Epidemiológicos",
        anos_disponiveis,
        default=anos_disponiveis
    )

    # 3. Filtro de Residência / Vínculo Epidemiológico
    sel_vinculo = st.selectbox(
        "Território & Residência",
        [
            "Residentes em Itaporã (Foco Local)",
            "Notificados em Itaporã",
            "Apenas Residente Autóctone",
            "Visão Geral Consolidada (Todos)"
        ],
        index=0,
        help="Separa munícipes de Itaporã, atendimentos locais e casos importados de outras cidades (ex.: Dourados)."
    )

    # 4. Filtro de Situação do Caso
    sel_status = st.selectbox(
        "Status da Classificação",
        ["Todos", "Apenas Confirmados", "Descartados", "Em Investigação"],
        index=0
    )

    # 5. Faixa de Semanas Epidemiológicas (Slider)
    se_range = st.slider(
        "Semanas Epidemiológicas (SE)",
        min_value=1,
        max_value=53,
        value=(1, 53)
    )

    # 6. Filtro Opcional de Bairro
    bairros_unicos = sorted(df_full["NM_BAIRRO_NORM"].dropna().unique()) if not df_full.empty else []
    sel_bairros = st.multiselect("Bairros Específicos", bairros_unicos, default=[])

    # 7. Filtro por Unidade de Saúde Notificadora (CNES)
    unidades_disponiveis = ["Todas as Unidades"]
    if not df_full.empty and "NM_UNIDADE_NOTIF" in df_full.columns:
        unidades_unicas = sorted(df_full["NM_UNIDADE_NOTIF"].dropna().unique().tolist())
        unidades_disponiveis += unidades_unicas

    sel_unidade = st.selectbox(
        "Unidade Notificadora (CNES)",
        unidades_disponiveis,
        index=0,
        help="Filtra os casos pelo estabelecimento de saúde (Hospital, ESF, Laboratório) onde a notificação foi emitida."
    )

    st.markdown("---")
    with st.expander("🦟 Conexão Conta-Ovos (Fiocruz)", expanded=False):
        c_token = st.text_input("API Token Conta-Ovos", value=st.session_state["contaovos_token"], type="password", help="Chave de acesso à API https://contaovos.com/pt-br/api/")
        if c_token != st.session_state["contaovos_token"]:
            st.session_state["contaovos_token"] = c_token
            st.cache_data.clear()

    with st.expander("⚙️ Configurações de Mapa", expanded=False):
        maps_api_key = st.text_input("Chave Google Maps API", value=DEFAULT_MAPS_KEY, type="password")


# ==============================================================================
# APLICAÇÃO DOS FILTROS NO DATAFRAME PRINCIPAL
# ==============================================================================
df_filtered = df_full.copy()

if sel_agravo != "Todos":
    df_filtered = df_filtered[df_filtered["AGRAVO_TIPO"] == sel_agravo]

if sel_anos:
    df_filtered = df_filtered[df_filtered["NU_ANO"].isin(sel_anos)]

if sel_vinculo == "Residentes em Itaporã (Foco Local)":
    df_filtered = df_filtered[df_filtered["IS_RESIDENTE_ITAPORA"]]
elif sel_vinculo == "Notificados em Itaporã":
    df_filtered = df_filtered[df_filtered["IS_NOTIFIC_ITAPORA"]]
elif sel_vinculo == "Apenas Residente Autóctone":
    df_filtered = df_filtered[df_filtered["TIPO_VINCULO"] == "Residente Autóctone"]

if sel_status == "Apenas Confirmados":
    df_filtered = df_filtered[df_filtered["STATUS_CASO"] == "Confirmado"]
elif sel_status == "Descartados":
    df_filtered = df_filtered[df_filtered["STATUS_CASO"] == "Descartado"]
elif sel_status == "Em Investigação":
    df_filtered = df_filtered[df_filtered["STATUS_CASO"] == "Em Investigação"]

df_filtered = df_filtered[(df_filtered["SE_NUM"] >= se_range[0]) & (df_filtered["SE_NUM"] <= se_range[1])]

if sel_bairros:
    df_filtered = df_filtered[df_filtered["NM_BAIRRO_NORM"].isin(sel_bairros)]

if sel_unidade != "Todas as Unidades" and "NM_UNIDADE_NOTIF" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["NM_UNIDADE_NOTIF"] == sel_unidade]

# Cargas das APIs Externas
infodengue = load_cached_infodengue()
contaovos = load_cached_contaovos(token=st.session_state["contaovos_token"])
df_weather = load_cached_weather()

# ==============================================================================
# CABEÇALHO DA PLATAFORMA (HERO BANNER MODERNO)
# ==============================================================================
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1>🦟 PLATAFORMA DE INTELIGÊNCIA EPIDEMIOLÓGICA E ENTOMOLÓGICA</h1>
            <p>Vigilância de Casos (SINAN) • Ovitrampas (Conta-Ovos Fiocruz) • Modelagem Climática | <strong>Itaporã - MS</strong> (IBGE: 5004301)</p>
        </div>
        <div style="text-align: right; margin-top: 6px;">
            <span class="badge-pill badge-green">Vigilância Ativa Integrada</span><br>
            <span style="color: #94A3B8; font-size: 0.82rem; font-weight: 600;">População: 24.137 hab. | 45 Ovitrampas Fixas</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# ESTRUTURAÇÃO DAS 7 ABAS ANALÍTICAS
# ==============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Cockpit Geral",
    "🗺️ Mapa Territorial & Ovitrampas",
    "🦟 Vigilância Entomológica",
    "📈 Curvas, Canal & Clima",
    "🔮 Modelos Preditivos",
    "🧬 Perfil Clínico & Laboratório",
    "📋 Gestão Operacional & Relatórios"
])


# ==============================================================================
# ABA 1: COCKPIT GERAL DE GESTÃO
# ==============================================================================
with tab1:
    st.markdown("### 📌 Indicadores-Chave e Desempenho Epidemiológico")
    
    total_notific = len(df_filtered)
    casos_conf = len(df_filtered[df_filtered["STATUS_CASO"] == "Confirmado"])
    casos_desc = len(df_filtered[df_filtered["STATUS_CASO"] == "Descartado"])
    casos_invest = len(df_filtered[df_filtered["STATUS_CASO"] == "Em Investigação"])

    taxa_incidencia = (casos_conf / etl.POPULACAO_ITAPORA) * 100000.0
    hospitalizados = int(df_filtered["IS_HOSPITALIZADO"].sum())
    taxa_hosp = (hospitalizados / casos_conf * 100.0) if casos_conf > 0 else 0.0
    obitos = int(df_filtered["IS_OBITO_AGRAVO"].sum())
    taxa_letalidade = (obitos / casos_conf * 100.0) if casos_conf > 0 else 0.0

    ano_max = df_filtered["NU_ANO"].max() if not df_filtered.empty else 2026
    ano_ant = ano_max - 1
    
    df_ano_atual = df_filtered[df_filtered["NU_ANO"] == ano_max]
    df_ano_ant = df_full[
        (df_full["NU_ANO"] == ano_ant) & 
        (df_full["SE_NUM"] >= se_range[0]) & 
        (df_full["SE_NUM"] <= se_range[1])
    ]
    if sel_agravo != "Todos":
        df_ano_ant = df_ano_ant[df_ano_ant["AGRAVO_TIPO"] == sel_agravo]
    
    conf_atual = len(df_ano_atual[df_ano_atual["STATUS_CASO"] == "Confirmado"])
    conf_ant = len(df_ano_ant[df_ano_ant["STATUS_CASO"] == "Confirmado"])
    delta_conf_yoy = ((conf_atual - conf_ant) / conf_ant * 100.0) if conf_ant > 0 else 0.0

    # Linha 1: 5 Cards de KPIs
    col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5)
    with col_k1:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div class="kpi-title">Total Notificado</div>
            <div class="kpi-value">{total_notific:,}</div>
            <div class="kpi-sub">Fichas no recorte ativo</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k2:
        yoy_class = "up-bad" if delta_conf_yoy > 0 else "down-good"
        yoy_arrow = "▲" if delta_conf_yoy > 0 else "▼"
        st.markdown(f"""
        <div class="kpi-card red">
            <div class="kpi-title">Casos Confirmados</div>
            <div class="kpi-value">{casos_conf:,}</div>
            <div class="kpi-sub {yoy_class}">{yoy_arrow} {abs(delta_conf_yoy):.1f}% vs {ano_ant}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k3:
        if taxa_incidencia >= 300:
            inc_cls, inc_cor = "red", "#EF4444"
            inc_txt = "Alta Incidência (Epidemia)"
        elif taxa_incidencia >= 100:
            inc_cls, inc_cor = "orange", "#F59E0B"
            inc_txt = "Média Incidência"
        else:
            inc_cls, inc_cor = "green", "#10B981"
            inc_txt = "Baixa Incidência"
        st.markdown(f"""
        <div class="kpi-card {inc_cls}">
            <div class="kpi-title">Taxa de Incidência</div>
            <div class="kpi-value">{taxa_incidencia:.1f}</div>
            <div class="kpi-sub" style="color: {inc_cor}; font-weight:700;">{inc_txt} (/100k hab)</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k4:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div class="kpi-title">Hospitalizações</div>
            <div class="kpi-value">{hospitalizados:,}</div>
            <div class="kpi-sub">{taxa_hosp:.1f}% dos confirmados</div>
        </div>
        """, unsafe_allow_html=True)
    with col_k5:
        st.markdown(f"""
        <div class="kpi-card orange">
            <div class="kpi-title">Óbitos Confirmados</div>
            <div class="kpi-value">{obitos}</div>
            <div class="kpi-sub">Taxa Letalidade: {taxa_letalidade:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Linha 2: Status das APIs (InfoDengue + Conta-Ovos Ovitrampas)
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown(f"""
        <div class="glass-card" style="border-left: 5px solid {infodengue['badge_color']};">
            <div style="font-family: 'Space Grotesk'; color: #94A3B8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">
                🏛️ Alerta Oficial InfoDengue (Fiocruz) | {infodengue['municipio']}
            </div>
            <div style="margin-top: 0.4rem; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                <span style="background-color: {infodengue['badge_color']}; color: #FFFFFF; font-weight: 700; padding: 0.3rem 0.8rem; border-radius: 999px; font-size: 0.85rem; font-family: 'Space Grotesk';">
                    Nível {infodengue['latest_level']} - {infodengue['level_desc']}
                </span>
                <span style="color: #F8FAFC; font-size: 0.95rem;">
                    Taxa Rt: <strong style="color: #38BDF8; font-family: 'Outfit'; font-size: 1.15rem;">{infodengue['latest_rt']}</strong>
                </span>
            </div>
            <div style="color: #94A3B8; font-size: 0.82rem; margin-top: 0.4rem;">
                {infodengue['interpretation']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_stat2:
        st.markdown(f"""
        <div class="glass-card" style="border-left: 5px solid {contaovos['risco_cor']};">
            <div style="font-family: 'Space Grotesk'; color: #94A3B8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">
                🦟 Vigilância Entomológica Ovitrampas (Conta-Ovos Fiocruz) | SE {contaovos['latest_se']}/{contaovos['latest_ano']}
            </div>
            <div style="margin-top: 0.4rem; display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.78rem; color: #94A3B8;">IPO (Positividade):</span>
                    <strong style="color: {contaovos['risco_cor']}; font-family: 'Outfit'; font-size: 1.25rem;"> {contaovos['latest_ipo']}%</strong>
                </div>
                <div>
                    <span style="font-size: 0.78rem; color: #94A3B8;">IDO (Densidade):</span>
                    <strong style="color: #F8FAFC; font-family: 'Outfit'; font-size: 1.25rem;"> {contaovos['latest_ido']} ovos/arm.</strong>
                </div>
                <span style="background-color: {contaovos['risco_cor']}; color: #FFFFFF; font-weight: 700; padding: 0.25rem 0.7rem; border-radius: 999px; font-size: 0.78rem; font-family: 'Space Grotesk';">
                    {contaovos['risco_entomologico']}
                </span>
            </div>
            <div style="color: #94A3B8; font-size: 0.82rem; margin-top: 0.4rem;">
                {contaovos['interpretacao']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Linha 3: Gráficos Executivos Ampliados
    cg1, cg2, cg3 = st.columns(3)
    with cg1:
        st.markdown("#### 🍩 Status de Encerramento (CLASSI_FIN)")
        if not df_filtered.empty:
            cf_counts = df_filtered["CLASSI_FIN_DESC"].value_counts().reset_index()
            cf_counts.columns = ["Classificação", "Casos"]
            fig_pie = px.pie(
                cf_counts,
                names="Classificação",
                values="Casos",
                hole=0.55,
                color_discrete_sequence=["#EF4444", "#F97316", "#10B981", "#F59E0B", "#818CF8"]
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, font=dict(size=11))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sem dados para o filtro aplicado.")

    with cg2:
        st.markdown("#### 🧪 Critério de Confirmação")
        if not df_filtered.empty:
            crit_counts = df_filtered["CRITERIO_DESC"].value_counts().reset_index()
            crit_counts.columns = ["Critério", "Casos"]
            fig_crit = px.bar(
                crit_counts,
                x="Casos",
                y="Critério",
                orientation="h",
                color="Critério",
                color_discrete_sequence=["#38BDF8", "#10B981", "#F59E0B", "#64748B"]
            )
            fig_crit.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=380,
                showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Volume de Casos"),
                yaxis=dict(title="")
            )
            st.plotly_chart(fig_crit, use_container_width=True)
        else:
            st.info("Sem dados para o filtro aplicado.")

    with cg3:
        st.markdown("#### ⏱️ Oportunidade da Notificação (Dias)")
        df_oport = df_filtered.dropna(subset=["TEMPO_SINTOMA_NOTIF"])
        if not df_oport.empty:
            mediana_oport = df_oport["TEMPO_SINTOMA_NOTIF"].median()
            fig_hist = px.histogram(
                df_oport,
                x="TEMPO_SINTOMA_NOTIF",
                nbins=25,
                color_discrete_sequence=["#10B981"]
            )
            fig_hist.add_vline(
                x=mediana_oport,
                line_dash="dash",
                line_color="#EF4444",
                annotation_text=f"Mediana: {mediana_oport:.0f} dias",
                annotation_position="top right",
                annotation_font=dict(family="Space Grotesk", color="#F87171", size=12)
            )
            fig_hist.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=380,
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Dias entre Sintoma e Notificação"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Notificações")
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Sem datas válidas para cálculo de oportunidade.")


# ==============================================================================
# ABA 2: MAPA TERRITORIAL & GEORREFERENCIAMENTO DE PRECISÃO (CASOS + OVITRAMPAS)
# ==============================================================================
with tab2:
    st.markdown("### 🗺️ Georreferenciamento de Precisão: Casos Humanos & Rede de Ovitrampas")
    
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns([1.3, 1.3, 1.3, 1.1, 1.0])
    with m_col1:
        map_mode = st.selectbox(
            "Mecanismo de Mapa",
            ["Google Maps Interativo", "Folium (OpenStreetMap)"],
            index=0
        )
    with m_col2:
        view_type = st.selectbox(
            "Visualização de Casos",
            ["Ambos (Calor + Marcadores)", "Mapa de Calor (Densidade)", "Marcadores Detalhados"],
            index=0
        )
    with m_col3:
        loc_perspective = st.selectbox(
            "Camada de Localidade",
            ["Local de Residência (Domicílios)", "Unidade Notificadora / Hospital"],
            index=0
        )
    with m_col4:
        show_traps_toggle = st.checkbox("Exibir Ovitrampas (Ovos)", value=True, help="Exibe os 45 pontos de armadilhas da Conta-Ovos com escala de cor pelo volume de ovos.")
    with m_col5:
        map_screen = st.selectbox("Formato da Tela", ["🖥️ Monitor (720p)", "📱 Celular (460p)"], index=0, help="Adapta a altura do mapa para navegação touch no celular.")
        map_h = 460 if "Celular" in map_screen else 720

    coord_lat = "LAT" if "Residência" in loc_perspective else "LAT_NOTIF"
    coord_lon = "LON" if "Residência" in loc_perspective else "LON_NOTIF"
    df_map_valid = df_filtered.dropna(subset=[coord_lat, coord_lon])

    if map_mode == "Google Maps Interativo":
        html_gmaps = render_google_maps_html(
            df_map_valid,
            df_traps=contaovos["df_traps"],
            api_key=maps_api_key,
            tipo_visualizacao=view_type,
            coord_col_lat=coord_lat,
            coord_col_lon=coord_lon,
            show_traps_layer=show_traps_toggle
        )
        components.html(html_gmaps, height=map_h, scrolling=False)
    else:
        fmap = folium.Map(
            location=[-22.0803, -54.7892],
            zoom_start=14,
            tiles="cartodbdark_matter"
        )
        sample_folium = df_map_valid.head(1500)
        
        if "Calor" in view_type or "Ambos" in view_type:
            heat_data = [[row[coord_lat], row[coord_lon], 1.0] for _, row in sample_folium.iterrows()]
            HeatMap(heat_data, radius=18, blur=20, min_opacity=0.35).add_to(fmap)

        if "Marcadores" in view_type or "Ambos" in view_type:
            cluster = MarkerCluster().add_to(fmap)
            for _, r in sample_folium.iterrows():
                cor_m = "red" if r["AGRAVO_TIPO"] == "Dengue" else "purple"
                if r["STATUS_CASO"] == "Descartado":
                    cor_m = "gray"
                folium.CircleMarker(
                    location=[r[coord_lat], r[coord_lon]],
                    radius=5,
                    color=cor_m,
                    fill=True,
                    fill_color=cor_m,
                    fill_opacity=0.8,
                    popup=folium.Popup(f"<b>{r['AGRAVO_TIPO']}</b><br>Bairro: {r['NM_BAIRRO_NORM']}<br>Rua: {r['NM_LOGRADO_NORM']}", max_width=250)
                ).add_to(cluster)

        # Camada de Ovitrampas em Folium
        if show_traps_toggle and not contaovos["df_traps"].empty:
            for _, t in contaovos["df_traps"].iterrows():
                ovos = int(t.get("ovos_semana_atual", 0))
                cor_t = "#EF4444" if ovos >= 150 else ("#F97316" if ovos >= 80 else ("#F59E0B" if ovos >= 40 else "#10B981"))
                folium.RegularPolygonMarker(
                    location=[t["lat"], t["lon"]],
                    number_of_sides=3,
                    radius=8,
                    color=cor_t,
                    fill_color=cor_t,
                    fill_opacity=0.9,
                    popup=folium.Popup(f"<b>🦟 Ovitrampa: {t['trap_id']}</b><br>Bairro: {t['bairro']}<br>Ovos contados: <b>{ovos}</b>", max_width=250)
                ).add_to(fmap)

        # Camada de Unidades de Saúde Notificadoras Oficiais de Itaporã
        for cnes_u, info_u in unidades_saude.UNIDADES_SAUDE_ITAPORA.items():
            qtd_cnes = int((df_filtered["CNES_UNIDADE"] == cnes_u).sum()) if "CNES_UNIDADE" in df_filtered.columns else 0
            u_popup = f"""
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:12px; line-height:1.45; color:#F8FAFC; min-width:260px; background:#0B1120; padding:10px; border-radius:8px;">
                <div style="background:#1E3A8A; padding:6px 8px; border-radius:6px; margin-bottom:6px; border:1px solid #3B82F6;">
                    <span style="font-size:10px; color:#93C5FD; font-weight:700;">🏥 UNIDADE DE SAÚDE • CNES {cnes_u}</span><br>
                    <b style="font-size:13px; color:#FFFFFF;">{info_u['nome']}</b>
                </div>
                <b>Tipo:</b> {info_u['tipo']}<br>
                <b>Endereço:</b> <span style="color:#FDE68A; font-weight:600;">{info_u['endereco_completo']}</span><br>
                <b>Horário:</b> {info_u['horario']}<br>
                <b>Telefone:</b> {info_u['telefones']}<br>
                <b>Responsável:</b> {info_u['responsavel']}<br>
                <div style="margin-top:6px; padding-top:6px; border-top:1px solid rgba(255,255,255,0.15); color:#94A3B8;">
                    Notificações no filtro: <strong style="color:#38BDF8; font-size:14px;">{qtd_cnes:,}</strong> casos
                </div>
            </div>
            """
            folium.Marker(
                location=[info_u["lat"], info_u["lon"]],
                icon=folium.Icon(color="blue", icon="plus-sign", prefix="glyphicon"),
                tooltip=f"🏥 {info_u['sigla']} (CNES: {cnes_u})",
                popup=folium.Popup(u_popup, max_width=320)
            ).add_to(fmap)

        st_folium(fmap, height=map_h, width=None, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🚨 Microanálise de Bairros & Logradouros Críticos")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("##### 🏆 Top 15 Bairros com Maior Carga Viral")
        bairros_rank = df_filtered[df_filtered["STATUS_CASO"] == "Confirmado"]["NM_BAIRRO_NORM"].value_counts().head(15).reset_index()
        bairros_rank.columns = ["Bairro", "Casos Confirmados"]
        fig_bairros = px.bar(
            bairros_rank,
            x="Casos Confirmados",
            y="Bairro",
            orientation="h",
            color="Casos Confirmados",
            color_continuous_scale="Reds"
        )
        fig_bairros.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", size=11, color="#E2E8F0"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=460,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
        )
        st.plotly_chart(fig_bairros, use_container_width=True)

    with col_t2:
        st.markdown("##### 📍 Top 15 Ruas / Logradouros Críticos")
        ruas_rank = df_filtered[
            (df_filtered["STATUS_CASO"] == "Confirmado") & 
            (df_filtered["NM_LOGRADO_NORM"] != "LOGRADOURO NÃO INFORMADO")
        ]["NM_LOGRADO_NORM"].value_counts().head(15).reset_index()
        ruas_rank.columns = ["Logradouro", "Casos Confirmados"]
        fig_ruas = px.bar(
            ruas_rank,
            x="Casos Confirmados",
            y="Logradouro",
            orientation="h",
            color="Casos Confirmados",
            color_continuous_scale="Purples"
        )
        fig_ruas.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", size=11, color="#E2E8F0"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=460,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
        )
        st.plotly_chart(fig_ruas, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏥 Rede de Unidades de Saúde Notificadoras (CNES & Endereços)")
    st.caption("Cadastro Oficial da Gerência Municipal de Saúde de Itaporã/MS: Endereços, Horários de Funcionamento, Telefones, Responsáveis e Distribuição de Notificações SINAN.")

    # KPIs de Unidades de Saúde
    total_unid_itapora = len(unidades_saude.UNIDADES_SAUDE_ITAPORA)
    unid_counts = df_filtered["NM_UNIDADE_NOTIF"].value_counts() if not df_filtered.empty and "NM_UNIDADE_NOTIF" in df_filtered.columns else pd.Series()
    top_unid_nome = unid_counts.index[0] if not unid_counts.empty else "Nenhuma"
    top_unid_casos = int(unid_counts.iloc[0]) if not unid_counts.empty else 0
    top_unid_pct = (top_unid_casos / len(df_filtered) * 100.0) if len(df_filtered) > 0 else 0.0

    casos_hosp = int((df_filtered["CNES_UNIDADE"] == "2651505").sum()) if "CNES_UNIDADE" in df_filtered.columns else 0
    casos_esf = int(len(df_filtered) - casos_hosp)

    u_k1, u_k2, u_k3, u_k4 = st.columns(4)
    with u_k1:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div class="kpi-title">Rede Municipal Oficial</div>
            <div class="kpi-value">{total_unid_itapora}</div>
            <div class="kpi-sub">Unidades Cadastradas CNES</div>
        </div>
        """, unsafe_allow_html=True)
    with u_k2:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div class="kpi-title">Principal Notificadora</div>
            <div class="kpi-value">{top_unid_casos:,}</div>
            <div class="kpi-sub" title="{top_unid_nome}">{top_unid_pct:.1f}% ({top_unid_nome[:18]}...)</div>
        </div>
        """, unsafe_allow_html=True)
    with u_k3:
        st.markdown(f"""
        <div class="kpi-card red">
            <div class="kpi-title">Hospital Municipal (24h)</div>
            <div class="kpi-value">{casos_hosp:,}</div>
            <div class="kpi-sub">Urgência & Emergência</div>
        </div>
        """, unsafe_allow_html=True)
    with u_k4:
        st.markdown(f"""
        <div class="kpi-card green">
            <div class="kpi-title">Atenção Básica (ESFs)</div>
            <div class="kpi-value">{casos_esf:,}</div>
            <div class="kpi-sub">Estratégia Saúde da Família</div>
        </div>
        """, unsafe_allow_html=True)

    col_unid_g, col_unid_t = st.columns([1.2, 1.8])
    with col_unid_g:
        st.markdown("##### 📊 Volume de Casos por Estabelecimento Notificador")
        if not df_filtered.empty and "NM_UNIDADE_NOTIF" in df_filtered.columns:
            unid_rank = df_filtered["NM_UNIDADE_NOTIF"].value_counts().head(10).reset_index()
            unid_rank.columns = ["Unidade de Saúde", "Notificações"]
            fig_unid = px.bar(
                unid_rank,
                x="Notificações",
                y="Unidade de Saúde",
                orientation="h",
                color="Notificações",
                color_continuous_scale="Blues"
            )
            fig_unid.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=11, color="#E2E8F0"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=420,
                yaxis=dict(autorange="reversed"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
            )
            st.plotly_chart(fig_unid, use_container_width=True)
        else:
            st.info("Sem notificações para o filtro aplicado.")

    with col_unid_t:
        st.markdown("##### 📋 Cadastro Oficial de Unidades de Saúde de Itaporã / MS")
        cat_df = unidades_saude.obter_catalogo_unidades_itapora_df()
        if "CNES_UNIDADE" in df_filtered.columns:
            counts_dict = df_filtered["CNES_UNIDADE"].value_counts().to_dict()
            cat_df["Casos no Recorte"] = cat_df["CNES"].map(lambda c: counts_dict.get(str(c), 0))
        else:
            cat_df["Casos no Recorte"] = 0

        tabela_view = cat_df[[
            "CNES", "Unidade", "Endereço", "Bairro", "CEP",
            "Horário de Atendimento", "Telefones", "Responsável", "Casos no Recorte"
        ]].sort_values("Casos no Recorte", ascending=False)

        st.dataframe(
            tabela_view,
            use_container_width=True,
            height=420,
            hide_index=True
        )


# ==============================================================================
# ABA 3: VIGILÂNCIA ENTOMOLÓGICA (CONTA-OVOS FIOCRUZ) [NOVA ABA DEDICADA]
# ==============================================================================
with tab3:
    st.markdown("### 🦟 Monitoramento Entomológico de Ovitrampas (Conta-Ovos Fiocruz)")
    st.caption("Acompanhamento contínuo da densidade de postura de fêmeas grávidas de *Aedes aegypti* através da rede municipal de 45 ovitrampas de Itaporã/MS.")

    df_ento = contaovos["df_weekly"].copy()
    df_ento_traps = contaovos["df_traps"].copy()

    # Métricas Entomológicas de Destaque
    ce1, ce2, ce3, ce4 = st.columns(4)
    with ce1:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div class="kpi-title">Armadilhas Inspecionadas</div>
            <div class="kpi-value">{contaovos['df_traps'].shape[0]}</div>
            <div class="kpi-sub">Rede ativa municipal fixa</div>
        </div>
        """, unsafe_allow_html=True)
    with ce2:
        st.markdown(f"""
        <div class="kpi-card { 'red' if contaovos['latest_ipo'] >= 40 else ('orange' if contaovos['latest_ipo'] >= 20 else 'green') }">
            <div class="kpi-title">IPO (% Positividade)</div>
            <div class="kpi-value">{contaovos['latest_ipo']}%</div>
            <div class="kpi-sub">Limiar de Alerta: ≥ 40.0%</div>
        </div>
        """, unsafe_allow_html=True)
    with ce3:
        st.markdown(f"""
        <div class="kpi-card { 'red' if contaovos['latest_ido'] >= 80 else ('orange' if contaovos['latest_ido'] >= 40 else 'green') }">
            <div class="kpi-title">IDO (Densidade Ovos)</div>
            <div class="kpi-value">{contaovos['latest_ido']}</div>
            <div class="kpi-sub">Ovos por armadilha positiva</div>
        </div>
        """, unsafe_allow_html=True)
    with ce4:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div class="kpi-title">Total de Ovos Coletados</div>
            <div class="kpi-value">{contaovos['latest_ovos']:,}</div>
            <div class="kpi-sub">Semana Epidemiológica SE {contaovos['latest_se']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Gráfico 1: Séries Temporais de IPO e IDO com Linhas de Alerta
    st.markdown("---")
    st.markdown("#### 📊 Evolução Temporal dos Índices Entomológicos (IPO & IDO)")
    
    df_ento["SE_Label"] = df_ento["NU_ANO"].astype(str) + "-SE" + df_ento["SE_NUM"].astype(str)
    
    fig_ento = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Barra de Total de Ovos (Fundo)
    fig_ento.add_trace(
        go.Bar(
            x=df_ento["SE_Label"],
            y=df_ento["total_ovos"],
            name="Total de Ovos Coletados",
            marker_color="rgba(129, 140, 248, 0.25)"
        ),
        secondary_y=False
    )
    # Linha do IPO (%)
    fig_ento.add_trace(
        go.Scatter(
            x=df_ento["SE_Label"],
            y=df_ento["IPO"],
            mode="lines+markers",
            name="IPO (% Positividade)",
            line=dict(color="#EF4444", width=3)
        ),
        secondary_y=True
    )
    # Linha do IDO (Densidade)
    fig_ento.add_trace(
        go.Scatter(
            x=df_ento["SE_Label"],
            y=df_ento["IDO"],
            mode="lines",
            name="IDO (Ovos/Positiva)",
            line=dict(color="#F59E0B", width=2.5, dash="dot")
        ),
        secondary_y=False
    )
    # Linha de Alerta IPO (40%)
    fig_ento.add_hline(y=40, line_dash="dash", line_color="#EF4444", secondary_y=True, annotation_text="Limiar Crítico IPO (40%)")

    fig_ento.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
        margin=dict(t=20, b=20, l=10, r=10),
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    fig_ento.update_yaxes(title_text="Total Ovos / IDO", secondary_y=False, gridcolor="rgba(255,255,255,0.06)")
    fig_ento.update_yaxes(title_text="IPO (%)", secondary_y=True, range=[0, 100])
    st.plotly_chart(fig_ento, use_container_width=True)

    # Gráfico 2: Antecipação Biológica dos Ovos vs. Casos Clínicos Humanos
    st.markdown("---")
    st.markdown("#### ⏳ Antecipação Biológica: Ovos Coletados vs. Casos Notificados SINAN (Lag de 2 a 4 Semanas)")
    st.caption("O pico de fêmeas ovipositando nas ovitrampas antecipa o surgimento de sintomas clínicos em aproximadamente 14 a 28 dias, permitindo intervenção preventiva de bloqueio.")

    df_casos_se = df_filtered.groupby(["NU_ANO", "SE_NUM"]).size().reset_index(name="Casos_SINAN")
    df_lag_comp = pd.merge(df_ento, df_casos_se, on=["NU_ANO", "SE_NUM"], how="inner").sort_values(by=["NU_ANO", "SE_NUM"])

    if not df_lag_comp.empty:
        fig_lag = make_subplots(specs=[[{"secondary_y": True}]])
        fig_lag.add_trace(
            go.Scatter(
                x=df_lag_comp["SE_Label"],
                y=df_lag_comp["total_ovos"],
                mode="lines+markers",
                name="Postura de Ovos (Conta-Ovos)",
                line=dict(color="#10B981", width=3)
            ),
            secondary_y=False
        )
        fig_lag.add_trace(
            go.Scatter(
                x=df_lag_comp["SE_Label"],
                y=df_lag_comp["Casos_SINAN"],
                mode="lines+markers",
                name="Casos Clínicos Notificados (SINAN)",
                line=dict(color="#EF4444", width=3.5)
            ),
            secondary_y=True
        )
        fig_lag.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
            margin=dict(t=20, b=20, l=10, r=10),
            height=440,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        fig_lag.update_yaxes(title_text="Ovos de Aedes aegypti", secondary_y=False, gridcolor="rgba(255,255,255,0.06)")
        fig_lag.update_yaxes(title_text="Casos Humanos Notificados", secondary_y=True)
        st.plotly_chart(fig_lag, use_container_width=True)

    # Bairros mais infestados na semana recente
    st.markdown("---")
    st.markdown("#### 🚨 Bairros com Maior Infestação de Fêmeas Grávidas (Semana Recente)")
    bairros_ovos = df_ento_traps.groupby("bairro")["ovos_semana_atual"].sum().reset_index().sort_values(by="ovos_semana_atual", ascending=False)
    fig_b_ovos = px.bar(
        bairros_ovos,
        x="ovos_semana_atual",
        y="bairro",
        orientation="h",
        color="ovos_semana_atual",
        color_continuous_scale="Viridis",
        labels={"ovos_semana_atual": "Ovos Coletados", "bairro": "Bairro"}
    )
    fig_b_ovos.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=11, color="#E2E8F0"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=360,
        yaxis=dict(autorange="reversed"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
    )
    st.plotly_chart(fig_b_ovos, use_container_width=True)


# ==============================================================================
# ABA 4: CURVAS EPIDÊMICAS, CANAL ENDÊMICO & CLIMA (TRÍADE EPIDEMIOLÓGICA)
# ==============================================================================
with tab4:
    st.markdown("### 📈 Curvas de Incidência, Diagrama de Controle & Clima")
    
    # 1. Curva Comparativa Multianual (Semanas 1 a 53)
    st.markdown("#### 📊 Curva Epidêmica Comparativa Multianual (Semanas 1 a 53)")
    df_curva = df_filtered[df_filtered["STATUS_CASO"] == "Confirmado"].groupby(["NU_ANO", "SE_NUM"]).size().reset_index(name="Casos")
    
    if not df_curva.empty:
        fig_multi = px.line(
            df_curva,
            x="SE_NUM",
            y="Casos",
            color="NU_ANO",
            markers=True,
            color_discrete_sequence=["#10B981", "#F59E0B", "#F97316", "#EF4444"],
            labels={"SE_NUM": "Semana Epidemiológica (SE)", "Casos": "Casos Confirmados", "NU_ANO": "Ano"}
        )
        fig_multi.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
            margin=dict(t=20, b=20, l=10, r=10),
            height=450,
            xaxis=dict(tickmode="linear", dtick=2, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)")
        )
        st.plotly_chart(fig_multi, use_container_width=True)

    # 2. Canal Endêmico
    st.markdown("---")
    st.markdown("#### 🛡️ Canal Endêmico (Diagrama de Controle Histórico)")
    target_year_canal = st.selectbox("Ano de Avaliação do Canal", anos_disponiveis, index=len(anos_disponiveis)-1)
    df_canal = forecasting.calculate_endemic_channel(df_filtered, target_year=target_year_canal)
    
    fig_canal = go.Figure()
    fig_canal.add_trace(go.Scatter(x=df_canal["SE"], y=df_canal["Limiar_Epidemico_Superior"], mode="lines", line=dict(color="#EF4444", width=2, dash="dash"), name="Limiar Epidêmico"))
    fig_canal.add_trace(go.Scatter(x=df_canal["SE"], y=df_canal["Media_Historica"], mode="lines", line=dict(color="#F59E0B", width=2), name="Média Histórica"))
    fig_canal.add_trace(go.Scatter(x=df_canal["SE"], y=df_canal["Limite_Inferior_Exito"], mode="lines", line=dict(color="#10B981", width=2, dash="dot"), name="Limite de Segurança"))
    fig_canal.add_trace(go.Scatter(x=df_canal["SE"], y=df_canal["Casos_Observados"], mode="lines+markers", line=dict(color="#38BDF8", width=3.5), name=f"Casos em {target_year_canal}"))
    fig_canal.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
        margin=dict(t=20, b=20, l=10, r=10),
        height=450,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Semana Epidemiológica (SE)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Volume de Casos")
    )
    st.plotly_chart(fig_canal, use_container_width=True)

    # 3. Tríade Epidemiológica Integrada (Clima + Postura de Ovos + Casos)
    st.markdown("---")
    st.markdown("#### 🌪️ Tríade Epidemiológica Integrada: Chuva/Temperatura + Ovos de Aedes + Casos Humanos")
    st.caption("Cruzamento direto das 3 séries temporais: Precipitação (Open-Meteo), Ovos em Ovitrampas (Conta-Ovos Fiocruz) e Casos Confirmados (SINAN).")

    if not df_weather.empty and not df_curva.empty:
        df_triade = pd.merge(df_weather, df_ento, on=["NU_ANO", "SE_NUM"], how="inner")
        df_triade = pd.merge(df_triade, df_curva, on=["NU_ANO", "SE_NUM"], how="inner").sort_values(by=["NU_ANO", "SE_NUM"])

        if not df_triade.empty:
            df_triade["SE_Label"] = df_triade["NU_ANO"].astype(str) + "-SE" + df_triade["SE_NUM"].astype(str)
            fig_triade = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_triade.add_trace(
                go.Bar(
                    x=df_triade["SE_Label"],
                    y=df_triade["chuva_acumulada_mm"],
                    name="Chuva Acumulada (mm)",
                    marker_color="rgba(56, 189, 248, 0.35)"
                ),
                secondary_y=False
            )
            fig_triade.add_trace(
                go.Scatter(
                    x=df_triade["SE_Label"],
                    y=df_triade["total_ovos"],
                    mode="lines",
                    name="Ovos nas Ovitrampas",
                    line=dict(color="#10B981", width=2.5, dash="dash")
                ),
                secondary_y=True
            )
            fig_triade.add_trace(
                go.Scatter(
                    x=df_triade["SE_Label"],
                    y=df_triade["Casos"],
                    mode="lines+markers",
                    name="Casos Notificados (SINAN)",
                    line=dict(color="#EF4444", width=3.5)
                ),
                secondary_y=False
            )
            fig_triade.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=460,
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            fig_triade.update_yaxes(title_text="Chuva (mm) / Casos", secondary_y=False, gridcolor="rgba(255,255,255,0.06)")
            fig_triade.update_yaxes(title_text="Ovos Contados", secondary_y=True)
            st.plotly_chart(fig_triade, use_container_width=True)


# ==============================================================================
# ABA 5: MODELOS PREDITIVOS & ALERTAS ANTECIPADOS
# ==============================================================================
with tab5:
    st.markdown("### 🔮 Projeções Epidemiológicas & Confronto Fiocruz")
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        st.markdown("#### 📈 Projeção da Curva de Contágio (4 a 8 Semanas à Frente)")
        steps = st.slider("Horizonte de Previsão (Semanas)", 4, 8, 6)
        
        forecast_res = forecasting.forecast_cases(df_filtered, steps_ahead=steps)
        hist_df = forecast_res["historical"]
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=hist_df["Label"], y=hist_df["Casos"], mode="lines+markers", name="Casos Reais SINAN", line=dict(color="#38BDF8", width=2.5)))
        fig_pred.add_trace(go.Scatter(
            x=forecast_res["forecast_labels"] + forecast_res["forecast_labels"][::-1],
            y=forecast_res["upper_95"] + forecast_res["lower_95"][::-1],
            fill="toself",
            fillcolor="rgba(244, 63, 94, 0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Intervalo de Confiança (95%)"
        ))
        fig_pred.add_trace(go.Scatter(x=forecast_res["forecast_labels"], y=forecast_res["forecast_values"], mode="lines+markers", name=f"Projeção ({forecast_res['model_name']})", line=dict(color="#F43F5E", width=3, dash="dash")))
        fig_pred.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
            margin=dict(t=20, b=20, l=10, r=10),
            height=450,
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Semanas Epidemiológicas"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Notificações Previstas")
        )
        st.plotly_chart(fig_pred, use_container_width=True)

    with col_p2:
        st.markdown("#### 🚦 Semáforo de Aceleração Semanal (Δ SE)")
        recent_cases = hist_df["Casos"].tail(4).tolist() if len(hist_df) >= 4 else [0, 0, 0, 0]
        if len(recent_cases) >= 2 and recent_cases[-2] > 0:
            delta_se = ((recent_cases[-1] - recent_cases[-2]) / recent_cases[-2]) * 100.0
        else:
            delta_se = 0.0

        if delta_se > 30:
            sem_cor, sem_status, sem_msg = "#EF4444", "ALERTA MÁXIMO (SURTO ACELERADO)", "Crescimento explosivo de contágio semanal. Recomenda-se acionar plano de contingência."
        elif delta_se > 0:
            sem_cor, sem_status, sem_msg = "#F59E0B", "ATENÇÃO (EXPANSÃO MODERADA)", "Tendência de subida de casos. Intensificar visitas domiciliares de agentes."
        else:
            sem_cor, sem_status, sem_msg = "#10B981", "ESTÁVEL / DESCENDENTE", "Transmissão contida ou em desaceleração no município."

        st.markdown(f"""
        <div style="background: #111827; border-radius: 14px; padding: 1.4rem; border: 1px solid rgba(255,255,255,0.08); border-left: 6px solid {sem_cor}; box-shadow: 0 4px 16px -2px rgba(0,0,0,0.4); margin-top: 10px;">
            <div style="font-family: 'Space Grotesk'; color: #94A3B8; font-size: 0.82rem; font-weight: 700; text-transform: uppercase;">VARIAÇÃO SEMANAL (Δ SE)</div>
            <div style="font-family: 'Outfit'; color: {sem_cor}; font-size: 2.3rem; font-weight: 800; margin: 0.2rem 0;">{delta_se:+.1f}%</div>
            <div style="font-family: 'Outfit'; color: #F8FAFC; font-weight: 700; font-size: 1rem;">{sem_status}</div>
            <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.5rem; line-height: 1.45;">{sem_msg}</p>
        </div>
        """, unsafe_allow_html=True)

    # Confronto Local SINAN vs InfoDengue Fiocruz
    st.markdown("---")
    st.markdown("#### ⚔️ Confronto Direto: Dados SINAN Municipal vs. Modelagem InfoDengue (Fiocruz)")
    if infodengue["status"] == "success" and not infodengue["df"].empty:
        df_fiocruz = infodengue["df"]
        df_sinan_se = df_filtered.groupby(["NU_ANO", "SE_NUM"]).size().reset_index(name="Casos_SINAN")
        df_comp = pd.merge(df_fiocruz, df_sinan_se, on=["NU_ANO", "SE_NUM"], how="inner").sort_values(by=["NU_ANO", "SE_NUM"])

        if not df_comp.empty:
            df_comp["Label"] = df_comp["NU_ANO"].astype(str) + "-SE" + df_comp["SE_NUM"].astype(str)
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatter(x=df_comp["Label"], y=df_comp["Casos_SINAN"], mode="lines+markers", name="SINAN Municipal (Itaporã)", line=dict(color="#38BDF8", width=3.5)))
            fig_comp.add_trace(go.Scatter(x=df_comp["Label"], y=df_comp["casos_est"], mode="lines", name="Casos Estimados Fiocruz", line=dict(color="#F59E0B", width=2.5, dash="dash")))
            fig_comp.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=430,
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Semana Epidemiológica"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Volume de Notificações")
            )
            st.plotly_chart(fig_comp, use_container_width=True)


# ==============================================================================
# ABA 6: PERFIL CLÍNICO, LABORATÓRIO & POPULAÇÕES VULNERÁVEIS
# ==============================================================================
with tab6:
    st.markdown("### 🧬 Vigilância Laboratorial, Sorotipos & Grupos de Risco")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("#### 🧪 Distribuição dos Exames Laboratoriais")
        tests_data = {
            "NS1": df_filtered["NS1_DESC"].value_counts().to_dict(),
            "Sorologia IgM": df_filtered["SORO_DESC"].value_counts().to_dict(),
            "RT-PCR": df_filtered["PCR_DESC"].value_counts().to_dict(),
        }
        test_rows = []
        for test_name, counts in tests_data.items():
            for res_name, count in counts.items():
                if res_name != "Não Realizado":
                    test_rows.append({"Exame": test_name, "Resultado": res_name, "Total": count})
        
        if test_rows:
            df_tests = pd.DataFrame(test_rows)
            fig_test = px.bar(
                df_tests,
                x="Exame",
                y="Total",
                color="Resultado",
                barmode="group",
                color_discrete_map={"Reagente": "#EF4444", "Não Reagente": "#10B981", "Inconclusivo": "#F59E0B"}
            )
            fig_test.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=380,
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)")
            )
            st.plotly_chart(fig_test, use_container_width=True)
        else:
            st.info("Nenhum exame laboratorial registrado no recorte.")

    with col_l2:
        st.markdown("#### 🧬 Sorotipos DENV Circulantes")
        df_soro = df_filtered[df_filtered["SOROTIPO_DESC"] != "Não Identificado"]
        if not df_soro.empty:
            soro_counts = df_soro["SOROTIPO_DESC"].value_counts().reset_index()
            soro_counts.columns = ["Sorotipo", "Casos"]
            fig_soro = px.pie(
                soro_counts,
                names="Sorotipo",
                values="Casos",
                hole=0.45,
                color="Sorotipo",
                color_discrete_map={"DENV-1": "#38BDF8", "DENV-2": "#EF4444", "DENV-3": "#F59E0B", "DENV-4": "#10B981"}
            )
            fig_soro.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12, color="#E2E8F0"),
                margin=dict(t=20, b=20, l=10, r=10),
                height=380
            )
            st.plotly_chart(fig_soro, use_container_width=True)
        else:
            st.info("Sem isolamento viral de sorotipo registrado no recorte ativo.")

    st.markdown("---")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("#### 👥 Pirâmide Etária por Sexo")
        df_demo = df_filtered[df_filtered["STATUS_CASO"] == "Confirmado"].dropna(subset=["FAIXA_ETARIA"])
        if not df_demo.empty:
            demo_grouped = df_demo.groupby(["FAIXA_ETARIA", "SEXO_DESC"]).size().reset_index(name="Casos")
            order_fx = ["< 1 ano", "1 a 4 anos", "5 a 9 anos", "10 a 14 anos", "15 a 19 anos", "20 a 29 anos", "30 a 39 anos", "40 a 49 anos", "50 a 59 anos", "60 a 69 anos", "70 a 79 anos", "80+ anos"]
            demo_grouped["FAIXA_ETARIA"] = pd.Categorical(demo_grouped["FAIXA_ETARIA"], categories=order_fx, ordered=True)
            demo_grouped = demo_grouped.sort_values("FAIXA_ETARIA")

            fig_pyr = px.bar(
                demo_grouped,
                x="Casos",
                y="FAIXA_ETARIA",
                color="SEXO_DESC",
                orientation="h",
                barmode="group",
                color_discrete_map={"Feminino": "#F472B6", "Masculino": "#38BDF8", "Ignorado": "#64748B"}
            )
            fig_pyr.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=11, color="#E2E8F0"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=440,
                yaxis_title="Faixa Etária",
                legend_title="Sexo",
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
            )
            st.plotly_chart(fig_pyr, use_container_width=True)

    with col_d2:
        st.markdown("#### 🩺 Monitoramento de Sintomas & Sinais Clínicos")
        sintomas_list = [c for c in df_filtered.columns if c.startswith("SINTOMA_")]
        sint_counts = []
        for s in sintomas_list:
            nome = s.replace("SINTOMA_", "").title()
            qtd = df_filtered[s].sum()
            if qtd > 0:
                sint_counts.append({"Sintoma": nome, "Ocorrências": int(qtd), "Frequência (%)": round(qtd / len(df_filtered) * 100, 1)})
        
        if sint_counts:
            df_sint = pd.DataFrame(sint_counts).sort_values("Ocorrências", ascending=False).head(10)
            fig_sint = px.bar(
                df_sint,
                x="Frequência (%)",
                y="Sintoma",
                orientation="h",
                color="Frequência (%)",
                color_continuous_scale="Viridis"
            )
            fig_sint.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=11, color="#E2E8F0"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=440,
                yaxis=dict(autorange="reversed"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)")
            )
            st.plotly_chart(fig_sint, use_container_width=True)


# ==============================================================================
# ABA 7: GESTÃO OPERACIONAL, EXPORTAÇÃO & RELATÓRIO INTEGRADO
# ==============================================================================
with tab7:
    st.markdown("### 📋 Gestão Operacional, Exportação & Boletim Integrado")
    
    st.markdown("#### 📝 Boletim Epidemiológico & Entomológico Semanal Integrado")
    st.caption("Síntese executiva oficial gerada dinamicamente cruzando dados do SINAN e da Rede de Ovitrampas (Conta-Ovos Fiocruz).")

    data_hoje = datetime.date.today().strftime("%d/%m/%Y")
    se_recente = df_filtered["SE_NUM"].max() if not df_filtered.empty else 1
    ano_recente = df_filtered["NU_ANO"].max() if not df_filtered.empty else 2026
    
    bairros_top3 = df_filtered[df_filtered["STATUS_CASO"] == "Confirmado"]["NM_BAIRRO_NORM"].value_counts().head(3).index.tolist()
    bairros_top3_str = ", ".join(bairros_top3) if bairros_top3 else "Sem concentração identificada"

    # Síntese das Unidades Notificadoras
    unid_top3 = df_filtered["NM_UNIDADE_NOTIF"].value_counts().head(4) if not df_filtered.empty and "NM_UNIDADE_NOTIF" in df_filtered.columns else pd.Series()
    unid_top_str = "\n".join([f"   - {nome}: {qtd:,} notificações (CNES associado)" for nome, qtd in unid_top3.items()]) if not unid_top3.empty else "   - Nenhuma notificação registrada"

    boletim_texto = f"""BOLETIM SEMANAL DE VIGILÂNCIA EPIDEMIOLÓGICA E ENTOMOLÓGICA
MUNICÍPIO DE ITAPORÃ / MS (CÓDIGO IBGE: 5004301)
Data de Emissão: {data_hoje} | Semana Epidemiológica de Referência: SE {se_recente:02d}/{ano_recente}
=========================================================================================

1. SITUAÇÃO EPIDEMIOLÓGICA (DENGUE & CHIKUNGUNYA - SINAN):
   - Total de Notificações Registradas: {total_notific:,}
   - Casos Confirmados: {casos_conf:,}
   - Casos Descartados: {casos_desc:,}
   - Casos em Investigação: {casos_invest:,}
   - Taxa de Incidência Acumulada: {taxa_incidencia:.1f} casos / 100 mil hab. ({inc_txt})
   - Internações Hospitalares: {hospitalizados} pacientes ({taxa_hosp:.1f}% dos confirmados)
   - Óbitos Confirmados: {obitos} (Letalidade: {taxa_letalidade:.2f}%)
   - Vínculo Territorial: {len(df_filtered[df_filtered['TIPO_VINCULO'] == 'Residente Autóctone']):,} autóctones | {len(df_filtered[df_filtered['TIPO_VINCULO'] == 'Residente Notificado Fora']):,} notificados fora

2. VIGILÂNCIA ENTOMOLÓGICA (REDE DE OVITRAMPAS - CONTA-OVOS FIOCRUZ):
   - Rede de Armadilhas Inspecionadas: 45 ovitrampas fixas
   - Índice de Positividade de Ovitrampas (IPO): {contaovos['latest_ipo']}% (Limiar de Alerta: ≥ 40.0%)
   - Índice de Densidade de Ovos (IDO): {contaovos['latest_ido']} ovos por armadilha positiva
   - Total de Ovos Coletados na Semana: {contaovos['latest_ovos']:,} ovos
   - Avaliação de Risco Entomológico: {contaovos['risco_entomologico']}

3. MONITORAMENTO CLIMÁTICO & ALERTA INFODENGUE (FIOCRUZ):
   - Nível de Alerta InfoDengue: {infodengue['level_desc']}
   - Taxa de Reprodução Efetiva: Rt = {infodengue['latest_rt']}
   - Correlação Biológica: A postura de ovos observada antecipa a curva de casos em 14 a 28 dias.

4. DIRETRIZES OPERACIONAIS PARA CAMPO (AGENTES DE COMBATE ÀS ENDEMIAS - ACE):
   - Bairros de Maior Incidência e Postura: {bairros_top3_str}
   - Ações Prioritárias: Intensificação de visitas domiciliares focais, eliminação mecânica
     de criadouros e bloqueio químico/UBV costal nas ruas prioritárias apontadas na Aba 2.

5. PRINCIPAIS UNIDADES DE SAÚDE NOTIFICADORAS (GERÊNCIA DE SAÚDE DE ITAPORÃ):
{unid_top_str}
=========================================================================================
Secretaria Municipal de Saúde • Vigilância em Saúde Pública de Itaporã/MS
"""

    st.markdown(f'<div class="bulletin-box">{boletim_texto}</div>', unsafe_allow_html=True)
    st.download_button(
        "📄 Baixar Boletim Integrado (.txt)",
        data=boletim_texto,
        file_name=f"boletim_epidemiologico_entomologico_itapora_se{se_recente}_{ano_recente}.txt",
        mime="text/plain",
        use_container_width=False
    )

    st.markdown("---")
    st.markdown("#### 📥 Exportação de Dados para Equipes de Campo")
    
    col_exp1, col_exp2 = st.columns([3, 1])
    with col_exp1:
        cols_export_view = [
            "NU_NOTIFIC", "NU_ANO", "SE_NUM", "DT_NOTIFIC", "AGRAVO_TIPO",
            "STATUS_CASO", "CLASSI_FIN_DESC", "CNES_UNIDADE", "NM_UNIDADE_NOTIF",
            "ENDERECO_UNIDADE", "TELEFONE_UNIDADE", "RESPONSAVEL_UNIDADE",
            "TIPO_VINCULO", "NM_BAIRRO_NORM", "NM_LOGRADO_NORM", "IDADE_ANOS",
            "SEXO_DESC", "IS_HOSPITALIZADO"
        ]
        cols_presentes = [c for c in cols_export_view if c in df_filtered.columns]
        st.dataframe(
            df_filtered[cols_presentes].head(100),
            use_container_width=True,
            height=320
        )
    with col_exp2:
        st.markdown("**Downloads Rápidos:**")
        csv_data = df_filtered.to_csv(index=False, sep=";").encode("utf-8-sig")
        st.download_button(
            "📥 Baixar CSV Completo",
            data=csv_data,
            file_name=f"sinan_itapora_filtrado_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df_filtered.to_excel(writer, index=False, sheet_name="SINAN_Itapora")
            cat_unid = unidades_saude.obter_catalogo_unidades_itapora_df()
            cat_unid.to_excel(writer, index=False, sheet_name="Unidades_Saude_CNES")
            if not contaovos["df_weekly"].empty:
                contaovos["df_weekly"].to_excel(writer, index=False, sheet_name="ContaOvos_Ovitrampas")
        excel_data = excel_buffer.getvalue()

        st.download_button(
            "📊 Baixar Planilha Excel (.xlsx)",
            data=excel_data,
            file_name=f"vigilancia_integrada_itapora_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# Rodapé Tecnológico
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.82rem; font-family: 'Space Grotesk', sans-serif;">
    Plataforma de Inteligência Epidemiológica & Entomológica | Itaporã - MS | SINAN • Conta-Ovos Fiocruz • InfoDengue • Open-Meteo • Google Maps Platform
</div>
""", unsafe_allow_html=True)
