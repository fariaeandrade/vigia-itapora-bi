# Como Publicar na Vercel

Os arquivos para publicar na **Vercel** já estão configurados e prontos nesta pasta!

---

## 📁 Arquivos Criados para a Vercel

1. **[`vercel.json`](vercel.json):** Configura as rotas e o runtime `@vercel/python`.
2. **[`api/index.py`](api/index.py):** Ponto de entrada compatível com a arquitetura Serverless da Vercel.
3. **[`publicar_na_vercel.bat`](publicar_na_vercel.bat):** Arquivo de 2 cliques para publicar direto no seu painel da Vercel.

---

## 🚀 Como Publicar na Vercel

### Opção 1: Com 2 Cliques no Windows
1. Vá até a pasta do projeto e dê **dois cliques** no arquivo [`publicar_na_vercel.bat`](publicar_na_vercel.bat).
2. Ele chamará o comando oficial da Vercel (`npx vercel --prod`), solicitará seu login (se ainda não estiver conectado) e gerará o link online público.

### Opção 2: Pelo Terminal / Prompt de Comando
Abra o terminal na pasta do projeto e digite:
```bash
npx vercel --prod
```

### Opção 3: Conectando pelo Site da Vercel (vercel.com)
1. Suba este projeto para o seu GitHub (pode usar o [`publicar_online.bat`](publicar_online.bat)).
2. Acesse [vercel.com](https://vercel.com) e clique em **"Add New Project"**.
3. Selecione o repositório no GitHub e clique em **Deploy**.

---

## 💡 Observação Importante sobre o Streamlit na Nuvem

- A **Vercel** é uma plataforma feita para sites estáticos e funções *serverless* que duram apenas alguns segundos.
- O **Streamlit** utiliza conexão bidirecional em tempo real (*WebSockets*) para que os filtros, mapas e gráficos funcionem interativamente sem desconectar.
- Portanto, se você quiser a experiência interativa completa do Streamlit rodando com 100% de velocidade e de graça, a forma oficial recomendada pela equipe do Streamlit é:
  - **[Streamlit Community Cloud](https://share.streamlit.io/)**: Gratuito, oficial e conecta direto com seu GitHub em 1 clique apontando para `app.py`.
  - **[Render.com](https://render.com)**: Utilizando o arquivo [`render.yaml`](render.yaml) que já deixamos configurado.
