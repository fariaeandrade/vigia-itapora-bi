"""
================================================================================
MÓDULO DE PERSISTÊNCIA EM NUVEM (CLOUD STORAGE) - ITAPORÃ / MS
Integração REST Nativa com Supabase Storage / S3 com Fallback Local Resiliente
================================================================================
"""

import os
import io
import json
import datetime
from typing import Optional, Dict, Any, Tuple
import requests
import pandas as pd

# Arquivos locais padrão de cache
_LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
_LOCAL_PARQUET = os.path.join(_LOCAL_DIR, "dataset_consolidado.parquet")
_LOCAL_GEOCACHE = os.path.join(_LOCAL_DIR, "geocache.json")


def get_supabase_config() -> Dict[str, str]:
    """
    Obtém as credenciais do Supabase a partir de st.secrets ou variáveis de ambiente.
    """
    url = ""
    key = ""
    bucket = "arboviroses-itapora"

    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "supabase" in st.secrets:
                url = str(st.secrets["supabase"].get("url", "")).strip()
                key = str(st.secrets["supabase"].get("key", "")).strip()
                bucket = str(st.secrets["supabase"].get("bucket", bucket)).strip()
            elif "supabase_url" in st.secrets:
                url = str(st.secrets.get("supabase_url", "")).strip()
                key = str(st.secrets.get("supabase_key", "")).strip()
                bucket = str(st.secrets.get("supabase_bucket", bucket)).strip()
    except Exception:
        pass

    if not url:
        url = os.environ.get("SUPABASE_URL", "").strip()
    if not key:
        key = os.environ.get("SUPABASE_KEY", "").strip()
    if os.environ.get("SUPABASE_BUCKET"):
        bucket = os.environ.get("SUPABASE_BUCKET", bucket).strip()

    # Normalizar URL sem barra final
    if url.endswith("/"):
        url = url[:-1]

    return {
        "url": url,
        "key": key,
        "bucket": bucket,
        "is_configured": bool(url and key)
    }


def is_cloud_available() -> bool:
    """Verifica se a persistência em nuvem (Supabase) está ativa e configurada."""
    cfg = get_supabase_config()
    return cfg["is_configured"]


def _get_headers(key: str, content_type: str = "application/octet-stream") -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {key}",
        "apikey": key,
        "Content-Type": content_type,
        "x-upsert": "true"
    }


def _sanitizar_df_para_parquet(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante que colunas do tipo object não contenham tipos mistos (ex: float NaN e string),
    evitando falhas de conversão de tipos do PyArrow durante a gravação em Parquet.
    """
    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].dtype == "object":
            df_clean[col] = df_clean[col].apply(lambda x: "" if pd.isna(x) else str(x))
    return df_clean


# ==============================================================================
# 1. PERSISTÊNCIA DA BASE CONSOLIDADA (PARQUET)
# ==============================================================================
def salvar_base_consolidada(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Exporta a base consolidada e deduplicada para Parquet compactado (Snappy).
    Salva localmente e, se configurado, sincroniza com o Supabase Storage.
    """
    if df is None or df.empty:
        return False, "Dataframe vazio ou nulo."

    try:
        # Sanitizar colunas para garantir compatibilidade com PyArrow
        df_pronto = _sanitizar_df_para_parquet(df)

        # 1. Salvar cópia local em Parquet
        buffer = io.BytesIO()
        df_pronto.to_parquet(buffer, index=False, engine="pyarrow", compression="snappy")
        parquet_bytes = buffer.getvalue()

        with open(_LOCAL_PARQUET, "wb") as f:
            f.write(parquet_bytes)

        # 2. Se a nuvem estiver configurada, enviar para o Supabase Storage
        cfg = get_supabase_config()
        if cfg["is_configured"]:
            upload_url = f"{cfg['url']}/storage/v1/object/{cfg['bucket']}/dataset_consolidado.parquet"
            headers = _get_headers(cfg["key"], "application/octet-stream")
            
            resp = requests.post(upload_url, headers=headers, data=parquet_bytes, timeout=15)
            if resp.status_code in (200, 201):
                return True, "Base consolidada persistida com sucesso na Nuvem (Supabase) e localmente."
            else:
                return True, f"Base salva localmente. Nuvem retornou código {resp.status_code}."

        return True, "Base consolidada persistida localmente (modo offline/desenvolvimento)."
    except Exception as e:
        return False, f"Erro ao persistir base consolidada: {str(e)}"


def carregar_base_consolidada() -> Tuple[Optional[pd.DataFrame], str]:
    """
    Carrega o dataset consolidado .parquet mais recente.
    Tenta download do Supabase Storage; se não houver ou falhar, lê o arquivo local.
    """
    cfg = get_supabase_config()

    # 1. Tentar baixar da Nuvem se configurado
    if cfg["is_configured"]:
        try:
            download_url = f"{cfg['url']}/storage/v1/object/authenticated/{cfg['bucket']}/dataset_consolidado.parquet"
            headers = {"Authorization": f"Bearer {cfg['key']}", "apikey": cfg["key"]}
            
            resp = requests.get(download_url, headers=headers, timeout=12)
            if resp.status_code == 200 and len(resp.content) > 500:
                df = pd.read_parquet(io.BytesIO(resp.content), engine="pyarrow")
                # Atualizar cache local com a versão remota mais recente
                with open(_LOCAL_PARQUET, "wb") as f:
                    f.write(resp.content)
                return df, "Carregado com sucesso do Supabase Storage (Nuvem Oficial)."
        except Exception as e:
            print(f"[CloudStorage] Erro ao carregar da nuvem, acionando fallback: {e}")

    # 2. Fallback: Ler cópia local do Parquet se existir
    if os.path.exists(_LOCAL_PARQUET):
        try:
            df = pd.read_parquet(_LOCAL_PARQUET, engine="pyarrow")
            return df, "Carregado do cache local consolidado (dataset_consolidado.parquet)."
        except Exception as e:
            print(f"[CloudStorage] Erro ao ler parquet local: {e}")

    return None, "Nenhuma base consolidada encontrada em nuvem ou em disco local."


# ==============================================================================
# 2. SALVAMENTO DE PLANILHAS ORIGINAIS ENVIADAS
# ==============================================================================
def salvar_planilha_nuvem(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """
    Guarda uma cópia da planilha original enviada pelo usuário no bucket na nuvem.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"uploads/{timestamp}_{filename}"

    cfg = get_supabase_config()
    if cfg["is_configured"]:
        try:
            upload_url = f"{cfg['url']}/storage/v1/object/{cfg['bucket']}/{safe_name}"
            headers = _get_headers(cfg["key"], "application/octet-stream")
            resp = requests.post(upload_url, headers=headers, data=file_bytes, timeout=20)
            if resp.status_code in (200, 201):
                return True, f"Planilha original armazenada na nuvem como: {safe_name}"
            else:
                return False, f"Nuvem retornou status {resp.status_code}"
        except Exception as e:
            return False, f"Falha na comunicação com storage: {e}"

    # Salva em pasta uploads local como fallback
    up_dir = os.path.join(_LOCAL_DIR, "uploads")
    os.makedirs(up_dir, exist_ok=True)
    local_path = os.path.join(up_dir, f"{timestamp}_{filename}")
    with open(local_path, "wb") as f:
        f.write(file_bytes)
    return True, f"Planilha original armazenada localmente em: {local_path}"


# ==============================================================================
# 3. SINCRONIZAÇÃO DO GEOCACHE
# ==============================================================================
def carregar_geocache_nuvem() -> Dict[str, Any]:
    """
    Carrega o arquivo geocache.json da nuvem ou fallback local.
    """
    cfg = get_supabase_config()
    if cfg["is_configured"]:
        try:
            url = f"{cfg['url']}/storage/v1/object/authenticated/{cfg['bucket']}/geocache.json"
            headers = {"Authorization": f"Bearer {cfg['key']}", "apikey": cfg["key"]}
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "enderecos" in data:
                    # Atualiza cache local
                    with open(_LOCAL_GEOCACHE, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return data
        except Exception as e:
            print(f"[CloudStorage] Erro ao sincronizar geocache da nuvem: {e}")

    # Fallback local
    if os.path.exists(_LOCAL_GEOCACHE):
        try:
            with open(_LOCAL_GEOCACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {"enderecos": {}, "bairros": {}, "aliases": {}, "_municipio_default": {"lat": -22.0803, "lon": -54.7892}}


def atualizar_geocache_nuvem(novo_geocache: Dict[str, Any]) -> bool:
    """
    Envia a versão atualizada do geocache.json para a nuvem.
    """
    try:
        data_str = json.dumps(novo_geocache, ensure_ascii=False, indent=2)
        with open(_LOCAL_GEOCACHE, "w", encoding="utf-8") as f:
            f.write(data_str)

        cfg = get_supabase_config()
        if cfg["is_configured"]:
            url = f"{cfg['url']}/storage/v1/object/{cfg['bucket']}/geocache.json"
            headers = _get_headers(cfg["key"], "application/json")
            resp = requests.post(url, headers=headers, data=data_str.encode("utf-8"), timeout=10)
            return resp.status_code in (200, 201)
        return True
    except Exception as e:
        print(f"[CloudStorage] Erro ao atualizar geocache: {e}")
        return False
