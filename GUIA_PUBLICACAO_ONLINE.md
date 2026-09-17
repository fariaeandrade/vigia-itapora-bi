# Guia Oficial de Publicação Online: Painel de Arboviroses Itaporã/MS

Este guia ensina como colocar a **Plataforma de Inteligência Epidemiológica e Entomológica de Arboviroses de Itaporã - MS** no ar na internet gratuitamente, permitindo que qualquer pessoa acesse pelo **celular**, tablet ou computador.

---

## 📱 Visualização no Celular (Mobile View)

A plataforma conta com **responsividade total automática para smartphones**:
- **Abas Deslizáveis (Touch):** As 7 abas funcionam como um carrossel horizontal que pode ser arrastado com o dedo.
- **Cards de Métricas Adaptativos:** Em telas pequenas, os KPIs se reorganizam em 1 ou 2 por linha com tipografia ajustada.
- **Mapas Touch-Friendly:** Na Aba 2, você pode alternar para o modo **"📱 Celular (460p)"**, garantindo que o mapa não bloqueie a rolagem vertical da página no celular.
- **Gráficos com Redimensionamento Automático:** Todos os gráficos do Plotly redimensionam dinamicamente na vertical e na horizontal ao girar o celular.

---

## 🚀 Como Publicar Online Gratuitamente

Você tem 3 opções fáceis de publicação na nuvem:

### Opção 1: Streamlit Community Cloud (Recomendada - Oficial & Grátis)
*A forma mais estável, rápida e com suporte nativo a WebSockets e cache de dados.*

1. Crie uma conta gratuita em [GitHub](https://github.com) (se ainda não tiver).
2. Dê dois cliques no arquivo [`publicar_online.bat`](publicar_online.bat) na pasta do projeto para preparar o repositório Git.
3. Crie um repositório no seu GitHub chamado `painel-arboviroses-itapora` e envie os arquivos:
   ```bash
   git remote add origin https://github.com/SEU_USUARIO/painel-arboviroses-itapora.git
   git push -u origin main
   ```
4. Acesse **[share.streamlit.io](https://share.streamlit.io)** e faça login com seu GitHub.
5. Clique em **"New app"**:
   - **Repository:** `SEU_USUARIO/painel-arboviroses-itapora`
   - **Branch:** `main`
   - **Main file path:** `app.py`
6. Em *Advanced settings*, adicione a variável de ambiente:
   - `GOOGLE_MAPS_API_KEY = AIzaSyDoqwDBVxGLuy8HU75MPGqLWu9cWw4mjjw`
7. Clique em **"Deploy!"**. Em menos de 2 minutos você terá um link público permanente (ex: `https://itapora-arboviroses.streamlit.app`).

---

### Opção 2: Render.com (Arquivo `render.yaml` Já Configurado)
*Excelente alternativa em nuvem para aplicações Python completas com WebSockets contínuos.*

1. Acesse **[dashboard.render.com](https://dashboard.render.com)** e crie uma conta gratuita.
2. Clique no botão **"New +"** e selecione **"Blueprint"**.
3. Conecte sua conta do GitHub e selecione o repositório deste projeto.
4. O Render lerá automaticamente o arquivo [`render.yaml`](render.yaml) configurado neste projeto e iniciará a publicação.
5. O Render fornecerá uma URL pública segura com SSL (`https://painel-arboviroses-itapora.onrender.com`).

---

### Opção 3: Vercel (Arquivo `vercel.json` Já Configurado)
*Para quem já tem conta na Vercel e deseja usar o ecossistema Vercel.*

1. Instale a Vercel CLI no terminal:
   ```bash
   npm i -g vercel
   ```
2. Na pasta do projeto, execute:
   ```bash
   vercel --prod
   ```
3. O arquivo [`vercel.json`](vercel.json) já está configurado na raiz para orientar a compilação do `app.py`.

---

### Opção 4: Docker / VPS Própria (Arquivo `Dockerfile` Já Configurado)
Caso queira subir em um servidor próprio ou nuvem de containers (Railway, Fly.io, Google Cloud Run):
```bash
docker build -t painel-itapora .
docker run -p 8501:8501 painel-itapora
```
