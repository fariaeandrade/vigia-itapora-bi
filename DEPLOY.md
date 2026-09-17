# 🚀 GUIA DE DEPLOY EM NUVEM & PERSISTÊNCIA ONLINE
## Plataforma de Inteligência Epidemiológica e Entomológica de Arboviroses
### Município de Itaporã / MS • Código IBGE: 5004301

Este guia fornece o passo a passo completo e didático para publicar a plataforma na nuvem com **URL pública HTTPS**, acessível por qualquer computador, tablet ou smartphone, com **armazenamento persistente em nuvem (Supabase Storage)** e **controle de acesso seguro (RBAC)**.

---

## 🏛️ ARQUITETURA EM NUVEM DA APLICAÇÃO

```
   ┌─────────────────────────────────────────────────────────┐
   │                  DISPOSITIVOS DOS USUÁRIOS              │
   │      📱 Smartphone / Tablet     💻 Computador / Sala de Gestão   │
   └────────────────────────────┬────────────────────────────┘
                                │ HTTPS (SSL / Criptografado)
                                ▼
   ┌─────────────────────────────────────────────────────────┐
   │             STREAMLIT COMMUNITY CLOUD / RENDER          │
   │  • Interface Interativa Streamlit (Tema Escuro High-Tech)│
   │  • Barreira de Autenticação RBAC (Admin vs. Viewer)     │
   │  • 7 Abas Analíticas + Modelos Preditivos (ARIMA/ETS/RF) │
   │  • Georreferenciamento com Folium e Ovitrampas Fiocruz  │
   └───────────────┬─────────────────────────┬───────────────┘
                   │                         │
                   ▼                         ▼
   ┌────────────────────────┐      ┌────────────────────────┐
   │   SUPABASE STORAGE     │      │   APIS METEOROLÓGICAS  │
   │ (Persistência em Nuvem)│      │     E ENTOMOLÓGICAS    │
   │ • dataset_consolidado  │      │ • Open-Meteo Clima     │
   │   .parquet (712 KB)    │      │ • Conta-Ovos Fiocruz   │
   │ • geocache.json        │      │ • InfoDengue / IBGE    │
   │ • Planilhas enviadas   │      └────────────────────────┘
   └────────────────────────┘
```

---

## 🔐 1. CREDENCIAIS E PERFIS DE ACESSO (RBAC)

O sistema possui controle de acesso por papel com hash criptográfico SHA-256:

| Perfil | Usuário Padrão | Senha Padrão | Permissões |
| :--- | :--- | :--- | :--- |
| **Gestor / Vigilância (Admin)** | `gestor_itapora` | `itapora2026` | Acesso total: visualização de todas as abas, upload de novas planilhas do SINAN (`.xlsx`, `.csv`), sincronização e backup na nuvem. |
| **Consulta / Campo (Visualizador)**| `campo_itapora` | `saude2026` | Somente leitura: navegação interativa em mapas, gráficos epidemiológicos, correlação climática e emissão de boletins técnicos. O envio de arquivos é bloqueado. |

> **Dica de Segurança:** Você pode alterar os usuários e senhas a qualquer momento configurando as variáveis no painel de segredos do Streamlit Cloud (veja o Passo 3).

---

## ☁️ 2. CONFIGURAÇÃO DA PERSISTÊNCIA EM NUVEM (SUPABASE STORAGE)

O Supabase oferece **1 GB de armazenamento gratuito**, ideal para armazenar o arquivo compactado `dataset_consolidado.parquet` (712 KB), planilhas originais e o cache de bairros.

### Passo a Passo no Supabase:
1. Acesse [supabase.com](https://supabase.com) e crie uma conta gratuita (ou faça login com o GitHub).
2. Clique em **"New Project"**, informe um nome (ex: `itapora-arboviroses`) e crie uma senha para o banco de dados.
3. No menu lateral esquerdo, clique no ícone de **Storage** (📦 Armazenamento).
4. Clique em **"New Bucket"**:
   - Nome do Bucket: `arboviroses-itapora`
   - Pode marcar como **Public bucket** (ou privado com service key).
   - Clique em **Save**.
5. No menu lateral esquerdo, vá em **Project Settings** (⚙️) ➡️ **API**:
   - Copie a **Project URL** (ex: `https://abcdefghijkl.supabase.co`).
   - Copie a chave **service_role** (secreta) ou a chave **anon** (pública).

> **Observação:** Se você não configurar o Supabase imediatamente, **o sistema não quebra!** Ele automaticamente opera usando a base local `dataset_consolidado.parquet` já embutida no projeto.

---

## 🐙 3. PUBLICAR NO STREAMLIT COMMUNITY CLOUD (RECOMENDADO - 100% GRATUITO)

O Streamlit Community Cloud é a plataforma oficial da Snowflake/Streamlit para colocar aplicações Python online com suporte nativo a WebSockets e recursos completos.

### Etapa 1: Subir o Projeto no GitHub
1. Crie um repositório no seu GitHub (ex: `itapora-arboviroses-bi`).
2. Envie os arquivos desta pasta para o repositório:
   - `streamlit_app.py` e `app.py`
   - `auth.py`, `cloud_storage.py`, `api_services.py`, `etl.py`, `forecasting.py`
   - `requirements.txt`
   - `geocache.json`
   - `dataset_consolidado.parquet` (712 KB)
   - `.streamlit/secrets.toml.example`

*(Obs: O `.gitignore` incluso já impede que arquivos temporários ou segredos locais sejam expostos).*

### Etapa 2: Conectar no Streamlit Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io) e entre com sua conta do GitHub.
2. Clique no botão azul **"Create app"** (ou **"New app"**).
3. Preencha os dados:
   - **Repository:** `seu-usuario/itapora-arboviroses-bi`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Você pode personalizar o subdomínio (ex: `arboviroses-itapora.streamlit.app`).

### Etapa 3: Inserir as Chaves e Segredos
1. Na mesma tela de criação, clique em **"Advanced settings..."**.
2. Na aba **"Secrets"**, cole o seguinte conteúdo configurado com seus dados:

```toml
# ==============================================================================
# SEGREDOS DE PRODUÇÃO - ITAPORÃ / MS
# ==============================================================================

[supabase]
url = "https://SEU_PROJETO.supabase.co"
key = "SUA_CHAVE_SERVICE_ROLE_OU_ANON"
bucket = "arboviroses-itapora"

[auth]
admin_user = "gestor_itapora"
admin_password = "sua_senha_forte_admin_2026"
viewer_user = "campo_itapora"
viewer_password = "sua_senha_campo_2026"

[apis]
contaovos_token = ""
infodengue_token = ""
```

3. Clique em **Save** e em seguida clique no botão **"Deploy!"**.
4. Em cerca de 1 a 2 minutos, o Streamlit instalará os pacotes e exibirá a tela de login segura com tema escuro de alto contraste!

---

## 🐳 4. ALTERNATIVA: DEPLOY NO RENDER OU RAILWAY

Se preferir hospedar em um servidor de containers (Render, Railway ou Fly.io), o projeto já inclui os arquivos prontos:

- [`Dockerfile`](file:///c:/Users/User/.gemini/Sinan/Dockerfile): Container otimizado com Python 3.12 slim, dependências instaladas e porta 8501 exposta.
- [`render.yaml`](file:///c:/Users/User/.gemini/Sinan/render.yaml): Blueprint declarativo para o Render.

### No Render:
1. Acesse [render.com](https://render.com) e conecte seu repositório GitHub.
2. Crie um **New Web Service**.
3. Escolha o ambiente **Docker**.
4. Em **Environment Variables**, adicione:
   - `ADMIN_USER`: `gestor_itapora`
   - `ADMIN_PASSWORD`: `itapora2026`
   - `VIEWER_USER`: `campo_itapora`
   - `VIEWER_PASSWORD`: `saude2026`
   - `SUPABASE_URL`: `https://abcdef.supabase.co`
   - `SUPABASE_KEY`: `sua_chave`
   - `SUPABASE_BUCKET`: `arboviroses-itapora`
5. Clique em **Deploy**.

---

## 📱 5. ACESSO PELO CELULAR (RESPONSIVIDADE)

A interface foi projetada com adaptação fluida para dispositivos móveis:
- **Barra de navegação retrátil:** Menu compacto que recolhe automaticamente em telas estreitas.
- **Visualização em Cards:** Métricas e KPIs reorganizados verticalmente em telas de smartphone.
- **Mapa Touch-Friendly:** Controle por gestos de pinça para zoom nos bairros e pontos de ovitrampas de Itaporã.
- **Gráficos Redimensionáveis:** Painéis Plotly com renderização vetorial nítida em qualquer densidade de pixels.

---

## 🔄 6. FLUXO DE ATUALIZAÇÃO CONTÍNUA DOS DADOS

Quando novas semanas epidemiológicas forem fechadas:
1. O Gestor acessa a plataforma com a credencial de **Admin**.
2. No menu lateral, acesse o painel **"Upload de Novos Dados SINAN"**.
3. Faça o upload da planilha atualizada (`.xlsx` ou `.csv`).
4. O sistema executa automaticamente:
   - Deduplicação e upsert por `NU_NOTIFIC`.
   - Separação de residentes de Itaporã vs. outros municípios.
   - Cálculo das taxas de incidência e classificação de gravidade.
   - Geração e salvamento do novo arquivo `dataset_consolidado.parquet`.
   - Upload automático do backup para o **Supabase Storage**.
5. Todos os usuários (incluindo equipes em campo pelo celular) passam a visualizar instantaneamente os dados atualizados!

---

*Desenvolvido com tecnologia de ponta para a Vigilância em Saúde de Itaporã - MS.*
