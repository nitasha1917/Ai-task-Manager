# Railway Deployment Guide

## Files to add to your repo root:
- `Procfile`
- `railway.json`
- `requirements.txt`  ← replace your existing one
- `runtime.txt`

## Folder to create:
- `.streamlit/config.toml`  ← copy content from `.streamlit_config.toml`

## Your project structure must be:
```
your-repo/
├── .streamlit/
│   └── config.toml         ← paste content from .streamlit_config.toml
├── ui/
│   └── app.py
├── agents/
├── memory/
├── cnn/
│   ├── cnn_model.py
│   ├── cnn_page.py
│   └── model/
│       └── distraction_cnn.keras   ← upload this!
├── utils/
├── Procfile
├── railway.json
├── requirements.txt
└── runtime.txt
```

## Steps:

### 1. Add the model file
Your `distraction_cnn.keras` must be committed to git inside `cnn/model/`:
```bash
mkdir -p cnn/model
cp /path/to/distraction_cnn.keras cnn/model/
git add cnn/model/distraction_cnn.keras
git commit -m "add trained CNN model"
```
> ⚠️ If the .keras file is >100MB, use Git LFS:
> ```bash
> git lfs install
> git lfs track "*.keras"
> git add .gitattributes
> ```

### 2. Push to GitHub
```bash
git add Procfile railway.json requirements.txt runtime.txt .streamlit/config.toml
git commit -m "add Railway deployment config"
git push
```

### 3. Deploy on Railway
1. Go to https://railway.app → New Project → Deploy from GitHub repo
2. Select your repo
3. Go to **Variables** tab and add:
   ```
   GEMINI_API_KEY = your_actual_gemini_api_key
   GEMINI_MODEL   = gemini-2.0-flash-exp
   ```
4. Railway auto-detects `Procfile` and deploys — done!

## Environment Variables to set in Railway:
| Variable | Value |
|---|---|
| `GEMINI_API_KEY` | your Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` |

## Notes:
- **Webcam (Distraction Detector)** won't work in Railway's cloud — it requires a local device camera. The rest of the app works fine.
- The `memory/memory.json` file resets on each deploy (Railway containers are ephemeral). For persistence, upgrade to Railway's persistent volume or swap JSON storage for a database.
- Build takes ~5 min first time due to TensorFlow install.
