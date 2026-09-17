"""
Módulo de ETL, Padronização e Georreferenciamento SINAN - Arboviroses Itaporã/MS
Controle de:
- Autoctonia e Separação Notificação vs. Residência (TIPO_VINCULO)
- Painel Laboratorial (NS1, Sorologia IgM, PCR e Sorotipos DENV 1 a 4)
- Sinais de Gravidade e Choque (GRAV_HIPOT, GRAV_PULSO, Sinais de Alarme)
- Oportunidade da Notificação e Digitação (TEMPO_SINTOMA_NOTIF)
- Georreferenciamento de Precisão e Upsert Contínuo por NU_NOTIFIC
"""

import os
import re
import json
import hashlib
import unicodedata
from typing import Tuple, List, Optional, Union, Dict, Any
import numpy as np
import pandas as pd

POPULACAO_ITAPORA = 24137
COORD_CENTRAL_ITAPORA = (-22.0803, -54.7892)

# Códigos IBGE de Itaporã e cidades vizinhas relevantes
CODIGOS_ITAPORA = {"500450", "500430", "5004502", "5004301", 500450, 500430, 5004502, 5004301}
CODIGOS_DOURADOS = {"500370", "500270", "5003702", "5002704", 500370, 500270, 5003702, 5002704}

# Carregamento do Geocache de Bairros de Itaporã
_GEOCACHE_PATH = os.path.join(os.path.dirname(__file__), "geocache.json")
if os.path.exists(_GEOCACHE_PATH):
    try:
        with open(_GEOCACHE_PATH, "r", encoding="utf-8") as f:
            GEOCACHE = json.load(f)
    except Exception:
        GEOCACHE = {
            "_municipio_default": {"lat": -22.0803, "lon": -54.7892},
            "bairros": {"CENTRO": {"lat": -22.0785, "lon": -54.7895, "tipo": "Urbano"}},
            "aliases": {},
            "enderecos": {}
        }
else:
    GEOCACHE = {
        "_municipio_default": {"lat": -22.0803, "lon": -54.7892},
        "bairros": {"CENTRO": {"lat": -22.0785, "lon": -54.7895, "tipo": "Urbano"}},
        "aliases": {},
        "enderecos": {}
    }


def normalize_string(text: Optional[str]) -> str:
    """Remove acentos, pontuações e padroniza texto em maiúsculas."""
    if text is None or pd.isna(text):
        return ""
    text = str(text).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().upper()
    return text


def decode_sinan_age(val: Union[int, float, str]) -> Optional[float]:
    """
    Decodifica a variável NU_IDADE_N do SINAN:
    - 4000+ : Idade em anos (ex.: 4025 -> 25 anos)
    - 3000+ : Idade em meses (ex.: 3006 -> 0.5 anos)
    - 2000+ : Idade em dias
    - 1000+ : Idade em horas
    """
    if pd.isna(val):
        return None
    try:
        v = int(float(val))
        if v >= 4000:
            return float(v - 4000)
        elif v >= 3000:
            return round((v - 3000) / 12.0, 2)
        elif v >= 2000:
            return round((v - 2000) / 365.0, 2)
        elif v >= 1000:
            return round((v - 1000) / (365.0 * 24.0), 2)
        elif 0 <= v < 120:
            return float(v)
    except (ValueError, TypeError):
        pass
    return None


def get_age_group(age: Optional[float]) -> str:
    """Classifica idade em faixas etárias epidemiológicas padrão."""
    if age is None or pd.isna(age):
        return "Não Informado"
    if age < 1:
        return "< 1 ano"
    elif age < 5:
        return "1 a 4 anos"
    elif age < 10:
        return "5 a 9 anos"
    elif age < 15:
        return "10 a 14 anos"
    elif age < 20:
        return "15 a 19 anos"
    elif age < 30:
        return "20 a 29 anos"
    elif age < 40:
        return "30 a 39 anos"
    elif age < 50:
        return "40 a 49 anos"
    elif age < 60:
        return "50 a 59 anos"
    elif age < 70:
        return "60 a 69 anos"
    elif age < 80:
        return "70 a 79 anos"
    else:
        return "80+ anos"


def get_epi_week(sem_pri, sem_not, dt_sin_pri=None, dt_notific=None) -> int:
    """Extrai o número da semana epidemiológica (1 a 53)."""
    for val in [sem_pri, sem_not]:
        if pd.notna(val):
            try:
                s = str(int(float(val)))
                if len(s) >= 2:
                    week = int(s[-2:])
                    if 1 <= week <= 53:
                        return week
            except (ValueError, TypeError):
                pass
    for dt in [dt_sin_pri, dt_notific]:
        if pd.notna(dt) and hasattr(dt, "isocalendar"):
            try:
                return int(dt.isocalendar().week)
            except Exception:
                pass
    return 1


def resolve_bairro(raw_bairro: str) -> Tuple[str, float, float]:
    """Resolve o bairro canônico e suas coordenadas básicas a partir do geocache."""
    norm = normalize_string(raw_bairro)
    if not norm:
        default = GEOCACHE.get("_municipio_default", {"lat": -22.0803, "lon": -54.7892})
        return "NÃO INFORMADO", default["lat"], default["lon"]

    canonical = GEOCACHE.get("aliases", {}).get(norm, norm)
    bairros_dict = GEOCACHE.get("bairros", {})

    if canonical in bairros_dict:
        coords = bairros_dict[canonical]
        return canonical, coords["lat"], coords["lon"]

    for b_name, coords in bairros_dict.items():
        if b_name in norm or norm in b_name:
            return b_name, coords["lat"], coords["lon"]

    default = GEOCACHE.get("_municipio_default", {"lat": -22.0803, "lon": -54.7892})
    return canonical, default["lat"], default["lon"]


def calculate_deterministic_jitter(notific_id: str, numero: str, rua: str, is_rural: bool = False) -> Tuple[float, float]:
    """Gera um deslocamento determinístico por hash MD5 para dispersão visual fiel."""
    seed_str = f"{notific_id}_{numero}_{rua}"
    hash_int = int(hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:8], 16)
    np.random.seed(hash_int)
    
    scale = 0.005 if is_rural else 0.0016
    lat_jitter = float(np.random.normal(0, scale))
    lon_jitter = float(np.random.normal(0, scale))
    return lat_jitter, lon_jitter


def classify_vinculo_epidemiologico(row: pd.Series) -> Tuple[str, bool, bool, bool]:
    """
    Separação Notificação vs. Residência vs. Autoctonia:
    Retorna: (TIPO_VINCULO, IS_RESIDENTE_ITAPORA, IS_NOTIFIC_ITAPORA, IS_AUTOCTONE)
    """
    resi_raw = row.get("ID_MN_RESI")
    mun_raw = row.get("ID_MUNICIP")
    autocto_raw = row.get("TPAUTOCTO")

    def clean_code(c):
        if pd.isna(c):
            return ""
        return str(c).split(".")[0].strip()

    resi = clean_code(resi_raw)
    mun = clean_code(mun_raw)
    autocto = clean_code(autocto_raw)

    is_resi_itapora = resi in CODIGOS_ITAPORA or resi == "500450" or resi == "500430"
    is_notif_itapora = mun in CODIGOS_ITAPORA or mun == "500450" or mun == "500430"

    # Autoctonia: 1 = Sim, 2 = Não, 3 = Indeterminado
    is_autoctone = (autocto == "1")

    if is_resi_itapora:
        if autocto == "1":
            tipo = "Residente Autóctone"
        elif autocto == "2":
            tipo = "Residente com Infecção Fora"
        elif not is_notif_itapora:
            tipo = "Residente Notificado Fora"
        else:
            tipo = "Residente Autóctone"  # Padrão vigilância para residente sem infecção confirmada fora
            is_autoctone = True
    else:
        if is_notif_itapora:
            tipo = "Importado / Flutuante"
        else:
            tipo = "Não Residente Notificado Fora"

    return tipo, is_resi_itapora, is_notif_itapora, is_autoctone


def clean_sinan_df(df: pd.DataFrame, source_filename: str = "") -> pd.DataFrame:
    """
    Aplica todas as regras de decodificação, padronização, painel laboratorial e enriquecimento SINAN.
    """
    df = df.copy()
    
    # 1. Padronização de Colunas Essenciais
    if "NU_NOTIFIC" not in df.columns:
        df["NU_NOTIFIC"] = [f"SYNTH_{i}" for i in range(len(df))]
    else:
        df["NU_NOTIFIC"] = df["NU_NOTIFIC"].astype(str).str.split(".").str[0].str.strip()

    # 2. Identificação de Agravo
    filename_lower = source_filename.lower()
    if "ID_AGRAVO" in df.columns:
        def map_agravo(val):
            val_str = str(val).upper().strip()
            if "A92" in val_str or "CHIK" in val_str:
                return "Chikungunya"
            elif "A90" in val_str or "DENG" in val_str:
                return "Dengue"
            elif "chikun" in filename_lower:
                return "Chikungunya"
            return "Dengue"
        df["AGRAVO_TIPO"] = df["ID_AGRAVO"].apply(map_agravo)
    else:
        df["AGRAVO_TIPO"] = "Chikungunya" if "chikun" in filename_lower else "Dengue"

    # 3. Tratamento de Datas
    date_cols = ["DT_NOTIFIC", "DT_SIN_PRI", "DT_DIGITA", "DT_NASC", "DT_INTERNA", "DT_OBITO", "DT_SORO", "DT_NS1", "DT_PCR"]
    for c in date_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
        else:
            df[c] = pd.NaT

    # 4. Ano Epidemiológico (NU_ANO)
    if "NU_ANO" in df.columns:
        df["NU_ANO"] = pd.to_numeric(df["NU_ANO"], errors="coerce")
        df["NU_ANO"] = df["NU_ANO"].fillna(df["DT_NOTIFIC"].dt.year).fillna(df["DT_SIN_PRI"].dt.year)
    else:
        df["NU_ANO"] = df["DT_NOTIFIC"].dt.year.fillna(df["DT_SIN_PRI"].dt.year)
    df["NU_ANO"] = df["NU_ANO"].fillna(2024).astype(int)

    # 5. Semana Epidemiológica
    sem_pri_col = df["SEM_PRI"] if "SEM_PRI" in df.columns else pd.Series(index=df.index, dtype=object)
    sem_not_col = df["SEM_NOT"] if "SEM_NOT" in df.columns else pd.Series(index=df.index, dtype=object)
    
    se_list = []
    for idx, row in df.iterrows():
        sp = sem_pri_col.get(idx)
        sn = sem_not_col.get(idx)
        dsp = row["DT_SIN_PRI"]
        dn = row["DT_NOTIFIC"]
        se_list.append(get_epi_week(sp, sn, dsp, dn))
    df["SE_NUM"] = se_list

    # 6. Oportunidade da Notificação e Digitação (em dias)
    diff_sint = (df["DT_NOTIFIC"] - df["DT_SIN_PRI"]).dt.days
    df["TEMPO_SINTOMA_NOTIF"] = np.where((diff_sint >= 0) & (diff_sint <= 180), diff_sint, np.nan)
    
    diff_dig = (df["DT_DIGITA"] - df["DT_NOTIFIC"]).dt.days
    df["TEMPO_NOTIF_DIGITA"] = np.where((diff_dig >= 0) & (diff_dig <= 180), diff_dig, np.nan)

    # 7. Vínculo Epidemiológico (Notificação vs. Residência vs. Autoctonia)
    vinculos = df.apply(classify_vinculo_epidemiologico, axis=1)
    df["TIPO_VINCULO"] = [v[0] for v in vinculos]
    df["IS_RESIDENTE_ITAPORA"] = [v[1] for v in vinculos]
    df["IS_NOTIFIC_ITAPORA"] = [v[2] for v in vinculos]
    df["IS_AUTOCTONE"] = [v[3] for v in vinculos]

    # 8. Classificação Final (CLASSI_FIN) & Status do Caso
    def decode_classi_fin(row):
        cf = row.get("CLASSI_FIN")
        agravo = row.get("AGRAVO_TIPO", "Dengue")
        try:
            cf_val = int(float(cf))
        except (ValueError, TypeError):
            cf_val = None

        if agravo == "Dengue":
            if cf_val == 10:
                return "Dengue Clássica", "Confirmado"
            elif cf_val == 11:
                return "Dengue com Sinais de Alarme", "Confirmado"
            elif cf_val == 12:
                return "Dengue Grave", "Confirmado"
            elif cf_val == 5:
                return "Descartado", "Descartado"
            elif cf_val == 8:
                return "Inconclusivo / Em Investigação", "Em Investigação"
            else:
                return "Em Investigação", "Em Investigação"
        else:  # Chikungunya
            if cf_val == 13:
                return "Chikungunya", "Confirmado"
            elif cf_val == 5:
                return "Descartado", "Descartado"
            else:
                return "Em Investigação", "Em Investigação"

    classi_res = df.apply(decode_classi_fin, axis=1)
    df["CLASSI_FIN_DESC"] = [r[0] for r in classi_res]
    df["STATUS_CASO"] = [r[1] for r in classi_res]

    # 9. Critério de Confirmação (CRITERIO)
    crit_map = {1: "Laboratorial", 2: "Clínico-Epidemiológico", 3: "Em Investigação"}
    def decode_criterio(val):
        try:
            return crit_map.get(int(float(val)), "Em Investigação / Não Informado")
        except:
            return "Em Investigação / Não Informado"
    if "CRITERIO" in df.columns:
        df["CRITERIO_DESC"] = df["CRITERIO"].apply(decode_criterio)
    else:
        df["CRITERIO_DESC"] = "Não Informado"

    # 10. Painel Laboratorial (NS1, Sorologia IgM, RT-PCR, Sorotipo)
    lab_map = {1: "Reagente", 2: "Não Reagente", 3: "Inconclusivo", 4: "Não Realizado"}
    
    def decode_lab_test(val):
        try:
            v = int(float(val))
            return lab_map.get(v, "Não Realizado")
        except:
            return "Não Realizado"

    df["NS1_DESC"] = df["RESUL_NS1"].apply(decode_lab_test) if "RESUL_NS1" in df.columns else "Não Realizado"
    df["SORO_DESC"] = df["RESUL_SORO"].apply(decode_lab_test) if "RESUL_SORO" in df.columns else "Não Realizado"
    df["PCR_DESC"] = df["RESUL_PCR_"].apply(decode_lab_test) if "RESUL_PCR_" in df.columns else "Não Realizado"

    # Sorotipo DENV (1=DENV-1, 2=DENV-2, 3=DENV-3, 4=DENV-4)
    sorotipo_map = {1: "DENV-1", 2: "DENV-2", 3: "DENV-3", 4: "DENV-4"}
    def decode_sorotipo(val):
        try:
            v = int(float(val))
            return sorotipo_map.get(v, "Não Identificado")
        except:
            return "Não Identificado"
    df["SOROTIPO_DESC"] = df["SOROTIPO"].apply(decode_sorotipo) if "SOROTIPO" in df.columns else "Não Identificado"

    # Flags laboratoriais integradas
    df["TEM_EXAME_LAB"] = (df["NS1_DESC"] != "Não Realizado") | (df["SORO_DESC"] != "Não Realizado") | (df["PCR_DESC"] != "Não Realizado")
    df["LAB_POSITIVO"] = (df["NS1_DESC"] == "Reagente") | (df["SORO_DESC"] == "Reagente") | (df["PCR_DESC"] == "Reagente")

    # 11. Gravidade, Choque e Sinais de Alarme
    grav_cols = [c for c in df.columns if c.startswith("GRAV_")]
    def check_gravidade(row):
        for gc in grav_cols:
            val = str(row.get(gc, "")).strip()
            if val.startswith("1"):
                return True
        # Checa sinais de alarme pela classificação final
        if row.get("CLASSI_FIN") in [11, 12, "11", "12"]:
            return True
        return False
    df["TEM_SINAL_GRAVE"] = df.apply(check_gravidade, axis=1)

    # Hipotensão e Choque
    df["SINAL_HIPOTENSAO"] = df["GRAV_HIPOT"].apply(lambda v: True if str(v).strip().startswith("1") else False) if "GRAV_HIPOT" in df.columns else False
    df["SINAL_PULSO_DEBIL"] = df["GRAV_PULSO"].apply(lambda v: True if str(v).strip().startswith("1") else False) if "GRAV_PULSO" in df.columns else False

    # 12. Desfecho e Hospitalização
    evol_map = {1: "Cura", 2: "Óbito pelo Agravo", 3: "Óbito por Outras Causas", 4: "Óbito em Investigação", 9: "Ignorado"}
    df["EVOLUCAO_DESC"] = df["EVOLUCAO"].apply(lambda v: evol_map.get(int(float(v)), "Em Acompanhamento / Ignorado") if pd.notna(v) else "Ignorado") if "EVOLUCAO" in df.columns else "Ignorado"
    df["IS_OBITO_AGRAVO"] = df["EVOLUCAO"].apply(lambda v: True if str(v).strip().startswith("2") else False) if "EVOLUCAO" in df.columns else False

    hosp_map = {1: "Sim", 2: "Não", 9: "Ignorado"}
    df["HOSPITALIZ_DESC"] = df["HOSPITALIZ"].apply(lambda v: hosp_map.get(int(float(v)), "Ignorado") if pd.notna(v) else "Ignorado") if "HOSPITALIZ" in df.columns else "Ignorado"
    df["IS_HOSPITALIZADO"] = df["HOSPITALIZ"].apply(lambda v: True if str(v).strip().startswith("1") else False) if "HOSPITALIZ" in df.columns else False

    # 13. Variáveis Demográficas (Sexo, Idade, Faixa Etária, Gestante, Idoso)
    sexo_map = {"M": "Masculino", "F": "Feminino", "I": "Ignorado"}
    df["SEXO_DESC"] = df["CS_SEXO"].astype(str).str.upper().map(sexo_map).fillna("Ignorado") if "CS_SEXO" in df.columns else "Ignorado"
    df["IDADE_ANOS"] = df["NU_IDADE_N"].apply(decode_sinan_age) if "NU_IDADE_N" in df.columns else None
    df["FAIXA_ETARIA"] = df["IDADE_ANOS"].apply(get_age_group)
    df["IS_IDOSO"] = df["IDADE_ANOS"].apply(lambda a: a is not None and a >= 60)

    if "CS_GESTANT" in df.columns:
        df["IS_GESTANTE"] = df["CS_GESTANT"].apply(lambda v: True if str(v).strip() in ["1", "2", "3", "4"] else False)
    else:
        df["IS_GESTANTE"] = False

    # 14. Sintomas Clínicos
    sintomas_dict = {
        "FEBRE": "Febre",
        "MIALGIA": "Mialgia",
        "CEFALEIA": "Cefaleia",
        "EXANTEMA": "Exantema",
        "VOMITO": "Vômito",
        "NAUSEA": "Náusea",
        "DOR_COSTAS": "Dor nas Costas",
        "CONJUNTVIT": "Conjuntivite",
        "ARTRITE": "Artrite",
        "ARTRALGIA": "Artralgia",
        "PETEQUIA_N": "Petéquias",
        "PETEQUIAS": "Petéquias",
        "LEUCOPENIA": "Leucopenia",
        "LACO": "Prova do Laço",
        "DOR_RETRO": "Dor Retroorbital"
    }
    for col, label in sintomas_dict.items():
        if col in df.columns:
            df[f"SINTOMA_{col}"] = df[col].apply(lambda v: True if str(v).strip().startswith("1") else False)

    # 15. Geocodificação Territorial (Residência do Paciente)
    bairros_raw = df["NM_BAIRRO"].astype(str) if "NM_BAIRRO" in df.columns else pd.Series([""] * len(df))
    logrados_raw = df["NM_LOGRADO"].astype(str) if "NM_LOGRADO" in df.columns else pd.Series([""] * len(df))
    numeros_raw = df["NU_NUMERO"].astype(str) if "NU_NUMERO" in df.columns else pd.Series([""] * len(df))

    bairros_norm = []
    logrados_norm = []
    lats = []
    lons = []

    # Coordenadas da Unidade Notificadora (Hospital Municipal / UBS Central)
    lat_notif_base = -22.0835
    lon_notif_base = -54.7865

    for b_raw, l_raw, n_raw, notif_id in zip(bairros_raw, logrados_raw, numeros_raw, df["NU_NOTIFIC"]):
        b_canonical, lat_base, lon_base = resolve_bairro(b_raw)
        l_clean = normalize_string(l_raw)
        bairros_norm.append(b_canonical)
        logrados_norm.append(l_clean if l_clean else "LOGRADOURO NÃO INFORMADO")

        is_rural = b_canonical in ["ZONA RURAL", "CANHADAO", "SANTA TERRA"]
        lat_jit, lon_jit = calculate_deterministic_jitter(notif_id, n_raw, l_clean, is_rural)
        lats.append(round(lat_base + lat_jit, 6))
        lons.append(round(lon_base + lon_jit, 6))

    df["NM_BAIRRO_NORM"] = bairros_norm
    df["NM_LOGRADO_NORM"] = logrados_norm
    df["LAT"] = lats
    df["LON"] = lons
    
    # Coordenadas da Unidade de Notificação (com pequeno jitter de dispersão)
    df["LAT_NOTIF"] = [round(lat_notif_base + (i % 10 - 5) * 0.0002, 6) for i in range(len(df))]
    df["LON_NOTIF"] = [round(lon_notif_base + (i % 10 - 5) * 0.0002, 6) for i in range(len(df))]

    return df


def upsert_data(base_df: Optional[pd.DataFrame], new_df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int]:
    """
    Realiza o merge inteligente usando NU_NOTIFIC como chave primária única.
    Retorna: (DataFrame consolidado, novos_adicionados, atualizados_sobrescritos)
    """
    if base_df is None or base_df.empty:
        new_clean = new_df.drop_duplicates(subset=["NU_NOTIFIC"], keep="last")
        return new_clean, len(new_clean), 0

    base_df["NU_NOTIFIC"] = base_df["NU_NOTIFIC"].astype(str).str.strip()
    new_df["NU_NOTIFIC"] = new_df["NU_NOTIFIC"].astype(str).str.strip()

    existing_keys = set(base_df["NU_NOTIFIC"])
    new_keys = set(new_df["NU_NOTIFIC"])

    intersection = existing_keys.intersection(new_keys)
    added_keys = new_keys - existing_keys

    base_filtered = base_df[~base_df["NU_NOTIFIC"].isin(intersection)]
    consolidated = pd.concat([base_filtered, new_df], ignore_index=True)
    consolidated = consolidated.drop_duplicates(subset=["NU_NOTIFIC"], keep="last")

    return consolidated, len(added_keys), len(intersection)


def load_initial_data(data_dir: str = ".") -> pd.DataFrame:
    """
    Carrega automaticamente todas as bases nativas no diretório:
    dengue-2023-novo.xlsx, dengue-2024.xlsx, dengue-2025.xlsx, dengue-2026.xlsx,
    chikun-2024.xlsx, chikun-2025.xlsx, chikun-2026.xlsx.
    """
    expected_files = [
        "dengue-2023-novo.xlsx",
        "dengue-2024.xlsx",
        "chikun-2024.xlsx",
        "dengue-2025.xlsx",
        "chikun-2025.xlsx",
        "dengue-2026.xlsx",
        "chikun-2026.xlsx",
    ]
    
    consolidated_df = None
    for fname in expected_files:
        fpath = os.path.join(data_dir, fname)
        if os.path.exists(fpath):
            try:
                raw_df = pd.read_excel(fpath)
                clean_df = clean_sinan_df(raw_df, source_filename=fname)
                consolidated_df, _, _ = upsert_data(consolidated_df, clean_df)
            except Exception as e:
                print(f"Aviso ao carregar {fname}: {e}")

    if consolidated_df is None:
        consolidated_df = pd.DataFrame()

    return consolidated_df


def process_uploaded_files(uploaded_files, current_df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int]:
    """Processa múltiplos arquivos subidos via st.file_uploader e atualiza a base."""
    consolidated = current_df.copy() if current_df is not None else pd.DataFrame()
    total_added = 0
    total_updated = 0

    for file in uploaded_files:
        filename = file.name
        try:
            if filename.endswith(".csv"):
                raw_df = pd.read_csv(file, encoding="latin1", sep=None, engine="python")
            else:
                raw_df = pd.read_excel(file)
            
            clean_df = clean_sinan_df(raw_df, source_filename=filename)
            consolidated, added, updated = upsert_data(consolidated, clean_df)
            total_added += added
            total_updated += updated
        except Exception as e:
            print(f"Erro ao processar upload {filename}: {e}")

    return consolidated, total_added, total_updated
