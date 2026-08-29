# Deployment Guide — FinWise AI

This gets you two links to paste into the **Quick Links** table at the top
of `README.md`: a **live app URL** and a **demo video URL**.

Good news: since each visitor now enters their **own** OpenAI API key
directly in the app, you don't need to configure any secret keys in
Streamlit Cloud, and you don't need to install anything on your own
computer either — everything below happens in your browser, on GitHub's
and Streamlit's websites.

## Part 1 — Push this project to GitHub (browser only, no commands)

1. Go to https://github.com/new and create a new **empty** repository
   (don't check "Add a README" — you already have one). Name it e.g.
   `finwise-ai`.
2. On the new repo's page, click **"uploading an existing file"**.
3. Drag the **entire contents** of this project folder (not the folder
   itself — its contents: `app.py`, `src`, `docs`, `README.md`,
   `requirements.txt`, `.gitignore`, `.env.example`, `DEPLOYMENT.md`)
   into the upload box. Most browsers preserve folder structure when you
   drag a folder in (e.g. `src/` stays a folder).
4. Scroll down, write a short commit message like "Initial upload", and
   click **"Commit changes"**.

## Part 2 — Deploy on Streamlit Community Cloud (free)

1. Go to **https://share.streamlit.io** and sign in with your GitHub account
   (click **"Continue with GitHub"** and authorize it).
2. Click **"Create app"** → **"Deploy a public app from GitHub"**.
3. Pick:
   - Repository: `<your-username>/finwise-ai`
   - Branch: `main`
   - Main file path: `app.py`
4. Click **Deploy**. No secrets/API keys needed here — visitors enter their
   own key in the app itself.
5. After the build finishes (1–3 minutes) you'll get a URL like:
   `https://finwise-ai-<random>.streamlit.app`
6. Back on GitHub, open `README.md` in your repo, click the ✏️ pencil icon
   to edit, replace `PASTE_STREAMLIT_APP_URL_HERE` with that URL, then
   scroll down and click **"Commit changes"**.

## Part 3 — Record the demo video

1. Open your **live Streamlit Cloud URL** (not localhost — the reviewer
   needs to see the actual deployed app).
2. Paste a real OpenAI API key into the sidebar field so the app works
   during recording.
3. Record your screen (Windows: `Win+G`; Mac: `Cmd+Shift+5`; or a free tool
   like Loom) walking through:
   - Filling in income, expenses, savings, and a goal
   - Clicking **Analyze My Budget** and showing the dashboard
   - Opening the **Rule-based vs AI** tab to compare Python vs LLM output
   - Clicking **Generate streaming recommendation** to show live typing
   - Switching the cache option and re-submitting to show it's faster
4. Keep it short — 1.5 to 3 minutes.
5. Upload it to YouTube as **Unlisted** and copy the share link (simplest —
   avoids GitHub's 100MB file-size limit).
6. On GitHub, edit `README.md` again, replace `PASTE_DEMO_VIDEO_URL_HERE`
   with that link, and commit.

Once both placeholders are replaced, anyone opening your GitHub repo will
see the live app link first and the demo video link second, right at the
top of the README.
