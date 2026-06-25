# URL Shortener — a CI/CD learning project

A deliberately small FastAPI service whose real purpose is to teach you how a
**CI/CD pipeline** works end to end: lint → test → build → deploy.

## What's in here

```
app/                  The API
  main.py             FastAPI endpoints
  storage.py          In-memory URL store
tests/                Test suite (the CI "gate")
Dockerfile            Builds the production image
pyproject.toml        Ruff (linter) + pytest config
.github/workflows/
  ci.yml              The pipeline ← the part you're learning
```

## Run it locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive API.

Try it:
```bash
curl -X POST http://127.0.0.1:8000/shorten -H "Content-Type: application/json" -d "{\"url\": \"https://example.com\"}"
```

## Run the checks the way CI does

```bash
ruff check .     # lint
pytest -v        # tests
```

If both pass locally, they'll pass in CI.

## Build the Docker image locally

```bash
docker build -t url-shortener .
docker run -p 8000:8000 url-shortener
```

## How the pipeline works

Every push to `main` triggers `.github/workflows/ci.yml`, which runs three jobs:

1. **test** — installs deps, runs `ruff` and `pytest`. If anything fails, the
   pipeline stops here. Nothing broken ever gets built or deployed.
2. **build-and-push** — builds the Docker image and pushes it to GitHub's
   container registry (`ghcr.io`). Only runs after `test` passes, and only on
   `main` (not on pull requests).
3. **deploy** — a placeholder for triggering your host.

## Getting it actually running on GitHub

1. Create a new repo on GitHub.
2. Push this code:
   ```bash
   git init
   git add .
   git commit -m "Initial URL shortener + CI/CD"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```
3. Open the **Actions** tab — you'll see the pipeline run. Watch it lint, test,
   and build.

## Wiring up a real (free) deploy with Render

1. Create a free account at https://render.com and a new **Web Service** from
   your repo (it auto-detects the Dockerfile).
2. In Render → service → **Settings → Deploy Hook**, copy the hook URL.
3. In GitHub → repo → **Settings → Secrets and variables → Actions**, add a
   secret named `RENDER_DEPLOY_HOOK` with that URL.
4. Replace the `deploy` job's echo with:
   ```yaml
   - name: Trigger Render deploy
     run: curl -X POST "$RENDER_DEPLOY_HOOK"
     env:
       RENDER_DEPLOY_HOOK: ${{ secrets.RENDER_DEPLOY_HOOK }}
   ```

Now every push to `main` that passes tests auto-deploys. That's CI/CD. 🎉

## Suggested next steps (to learn more)

- Add a **matrix** to test on Python 3.11, 3.12, and 3.13.
- Add **code coverage** (`pytest --cov`) and fail under a threshold.
- Add a **status badge** to this README.
- Swap the in-memory store for **SQLite** and add a migration step.
- Require the pipeline to pass before merging (branch protection rule).
