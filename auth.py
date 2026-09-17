"""
================================================================================
MÓDULO DE AUTENTICAÇÃO E CONTROLE DE ACESSO (RBAC) - ITAPORÃ / MS
Gerenciamento seguro de credenciais, hashing e controle de perfis de usuário
================================================================================
"""

import os
import hashlib
import hmac
from typing import Dict, Any, Optional
import streamlit as st

_SALT = "itapora_arboviroses_2026_secure_salt"


def hash_password(password: str) -> str:
    """Gera hash SHA-256 seguro com salt fixo para credenciais."""
    return hashlib.sha256((password + _SALT).encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """Validação de senha com proteção contra timing attacks."""
    computed_hash = hash_password(password)
    return hmac.compare_digest(computed_hash, stored_hash)


def get_user_database() -> Dict[str, Dict[str, Any]]:
    """
    Recupera a base de usuários configurada no st.secrets ou variáveis de ambiente.
    Fornece fallback para testes locais e desenvolvimento.
    """
    users = {}

    # 1. Tentar ler de st.secrets
    try:
        if hasattr(st, "secrets") and "auth" in st.secrets:
            auth_sec = st.secrets["auth"]
            # Usuário Admin
            admin_u = str(auth_sec.get("admin_user", "gestor_itapora")).strip()
            admin_p = str(auth_sec.get("admin_password", "itapora2026")).strip()
            admin_h = str(auth_sec.get("admin_password_hash", "")).strip() or hash_password(admin_p)
            
            users[admin_u] = {
                "name": "Gestor de Vigilância em Saúde",
                "role": "admin",
                "role_label": "Gestor / Vigilância (Admin)",
                "password_hash": admin_h
            }

            # Usuário Visualizador
            view_u = str(auth_sec.get("viewer_user", "campo_itapora")).strip()
            view_p = str(auth_sec.get("viewer_password", "saude2026")).strip()
            view_h = str(auth_sec.get("viewer_password_hash", "")).strip() or hash_password(view_p)

            users[view_u] = {
                "name": "Equipe de Campo / Consulta",
                "role": "viewer",
                "role_label": "Consulta / Campo (Visualizador)",
                "password_hash": view_h
            }
            return users
    except Exception:
        pass

    # 2. Fallback de Desenvolvimento Padrão
    admin_env_u = os.environ.get("ADMIN_USER", "gestor_itapora")
    admin_env_p = os.environ.get("ADMIN_PASSWORD", "itapora2026")
    viewer_env_u = os.environ.get("VIEWER_USER", "campo_itapora")
    viewer_env_p = os.environ.get("VIEWER_PASSWORD", "saude2026")

    users[admin_env_u] = {
        "name": "Gestor de Vigilância em Saúde",
        "role": "admin",
        "role_label": "Gestor / Vigilância (Admin)",
        "password_hash": hash_password(admin_env_p)
    }
    users[viewer_env_u] = {
        "name": "Equipe de Campo / Consulta",
        "role": "viewer",
        "role_label": "Consulta / Campo (Visualizador)",
        "password_hash": hash_password(viewer_env_p)
    }

    return users


def autenticar_usuario(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autentica um usuário via credenciais em texto simples contra o banco de hashes.
    Retorna o dicionário de informações do usuário se válido, ou None se inválido.
    """
    users_db = get_user_database()
    user_key = username.strip()
    if user_key in users_db:
        user_data = users_db[user_key]
        if verify_password(password, user_data["password_hash"]):
            return {
                "username": user_key,
                "name": user_data["name"],
                "role": user_data["role"],
                "role_label": user_data["role_label"]
            }
    return None


def is_auth_required() -> bool:
    """
    Verifica se o sistema exige login obrigatório antes de permitir visualização.
    Por padrão retorna False, permitindo acesso livre sem senha para consulta pública.
    Para exigir senha estrita de todos os usuários, defina require_auth = true em secrets.toml.
    """
    try:
        if hasattr(st, "secrets") and "auth" in st.secrets:
            val = st.secrets["auth"].get("require_auth", False)
            if isinstance(val, bool):
                return val
            if str(val).lower() in ("true", "1", "yes", "sim"):
                return True
    except Exception:
        pass
    env_val = os.environ.get("REQUIRE_AUTH", "false").lower()
    return env_val in ("true", "1", "yes", "sim")


def login_as_guest():
    """Autentica a sessão como perfil público/visualizador sem exigir senha."""
    st.session_state["authenticated"] = True
    st.session_state["user_info"] = {
        "username": "publico",
        "name": "Consulta Pública / Equipe de Saúde",
        "role": "viewer",
        "role_label": "Acesso Livre (Sem Senha)"
    }


def check_authentication() -> bool:
    """
    Verifica se a sessão atual possui autenticação válida.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_info" not in st.session_state:
        st.session_state["user_info"] = None

    return st.session_state["authenticated"]


def is_admin() -> bool:
    """Verifica se o usuário logado possui privilégios de administrador."""
    if not check_authentication():
        return False
    u = st.session_state.get("user_info", {})
    return u.get("role") == "admin"


def logout():
    """Encerra a sessão do usuário e reinicia para o modo de acesso livre."""
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = None
    st.rerun()


def render_login_screen():
    """
    Renderiza tela de login moderna com tema escuro de alto contraste,
    alinhada à identidade visual da plataforma de saúde pública de Itaporã/MS.
    """
    st.markdown("""
    <div style="max-width: 460px; margin: 40px auto 20px auto; text-align: center;">
        <div style="display: inline-block; background: rgba(56, 189, 248, 0.15); border: 1px solid #38BDF8; color: #38BDF8; font-family: 'Space Grotesk', sans-serif; font-size: 0.78rem; font-weight: 700; padding: 4px 14px; border-radius: 9999px; text-transform: uppercase; margin-bottom: 12px;">
            Acesso Restrito • Saúde Pública
        </div>
        <h1 style="font-family: 'Outfit', sans-serif; font-size: 1.85rem; font-weight: 900; margin-bottom: 6px; background: linear-gradient(90deg, #FFFFFF 0%, #60A5FA 50%, #38BDF8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Plataforma de Arboviroses
        </h1>
        <p style="color: #94A3B8; font-size: 0.88rem; margin-bottom: 24px;">
            Município de Itaporã - MS • Vigilância Epidemiológica & Entomológica
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.8, 1])
    with col_l2:
        with st.container(border=True):
            st.markdown("#### 🔐 Entrar no Sistema")
            user_input = st.text_input("Usuário", placeholder="ex: gestor_itapora ou campo_itapora")
            pass_input = st.text_input("Senha", type="password", placeholder="Digite sua senha")

            col_b1, col_b2 = st.columns([1.1, 1.1])
            with col_b1:
                btn_login = st.button("🚀 Entrar com Senha", use_container_width=True, type="primary")
            with col_b2:
                btn_livre = st.button("🌐 Acessar Sem Senha", use_container_width=True)

            if btn_livre:
                login_as_guest()
                st.toast("Acesso público liberado!", icon="🌐")
                st.rerun()

            if btn_login:
                users_db = get_user_database()
                user_key = user_input.strip()

                if user_key in users_db:
                    user_data = users_db[user_key]
                    if verify_password(pass_input, user_data["password_hash"]):
                        st.session_state["authenticated"] = True
                        st.session_state["user_info"] = {
                            "username": user_key,
                            "name": user_data["name"],
                            "role": user_data["role"],
                            "role_label": user_data["role_label"]
                        }
                        st.toast(f"Bem-vindo(a), {user_data['name']}!", icon="👋")
                        st.rerun()
                    else:
                        st.error("Senha incorreta. Verifique e tente novamente.")
                else:
                    st.error("Usuário não encontrado.")

            st.markdown("---")
            st.markdown("""
            <div style="font-size: 0.76rem; color: #64748B; line-height: 1.5;">
                • <strong>Acesso Sem Senha:</strong> Visualize todas as 7 abas, gráficos, mapas e predições.<br>
                • <strong>Gestor (Admin):</strong> Login necessário apenas para upload e reprocessamento de planilhas.
            </div>
            """, unsafe_allow_html=True)


def render_user_sidebar_status():
    """
    Renderiza o card de perfil do usuário logado na sidebar com botão de Logout
    ou login de Gestor caso esteja em modo de Acesso Livre (Sem Senha).
    """
    if check_authentication():
        u = st.session_state.get("user_info", {})
        is_guest = u.get("username") == "publico"
        is_adm = u.get("role") == "admin"

        if is_guest:
            st.sidebar.markdown("""
            <div style="background: #111827; border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-family: 'Space Grotesk'; font-weight: 700;">Modo Ativo</div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC; margin: 2px 0;">Consulta Pública</div>
                <span style="display: inline-block; font-size: 0.72rem; font-weight: 700; color: #10B981; background: rgba(16, 185, 129, 0.15); padding: 2px 8px; border-radius: 999px; margin-top: 4px;">
                    🔓 Acesso Livre (Sem Senha)
                </span>
            </div>
            """, unsafe_allow_html=True)

            with st.sidebar.expander("🔐 Área do Gestor (Upload)", expanded=False):
                st.caption("Faça login apenas se precisar enviar novas planilhas.")
                u_gest = st.text_input("Usuário", key="side_u_gest", placeholder="gestor_itapora")
                p_gest = st.text_input("Senha", type="password", key="side_p_gest")
                if st.button("Entrar como Gestor", key="side_btn_gest", use_container_width=True, type="primary"):
                    user_auth = autenticar_usuario(u_gest, p_gest)
                    if user_auth and user_auth["role"] == "admin":
                        st.session_state["authenticated"] = True
                        st.session_state["user_info"] = user_auth
                        st.toast("Autenticado com sucesso como Gestor!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Credenciais incorretas.")
        else:
            badge_cor = "#EF4444" if is_adm else "#10B981"
            badge_bg = "rgba(239, 68, 68, 0.15)" if is_adm else "rgba(16, 185, 129, 0.15)"

            st.sidebar.markdown(f"""
            <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 10px 14px; margin-bottom: 14px;">
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-family: 'Space Grotesk'; font-weight: 700;">Conectado como</div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC; margin: 2px 0;">{u.get('name', 'Usuário')}</div>
                <span style="display: inline-block; font-size: 0.72rem; font-weight: 700; color: {badge_cor}; background: {badge_bg}; padding: 2px 8px; border-radius: 999px; margin-top: 4px;">
                    {u.get('role_label', 'Identificado')}
                </span>
            </div>
            """, unsafe_allow_html=True)

            if st.sidebar.button("🚪 Sair (Voltar ao Acesso Livre)", use_container_width=True):
                logout()

