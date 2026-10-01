# Deployment

Recommended stack for a simple, low-cost public deployment:

- **Frontend** → [Vercel](https://vercel.com) (native Next.js hosting)
- **Backend** → [Render](https://render.com) (Docker-based web service) —
  Railway is an equivalent alternative; the steps below transfer directly
- **Database** → [Neon](https://neon.tech) or [Supabase](https://supabase.com)
  (managed Postgres, both have a free tier)

Before you start, verify each platform's current free-tier limits and
signup requirements — they change over time and aren't reproduced here.

## GitHub Actions deployment

This repo includes a deployment workflow in `.github/workflows/deploy.yml` that can trigger a production deploy from GitHub Actions.

Required GitHub repository secrets:

| Secret | Used by | Value |
|---|---|---|
| `VERCEL_TOKEN` | Frontend | Vercel personal access token |
| `VERCEL_ORG_ID` | Frontend | Vercel team or user org ID |
| `VERCEL_PROJECT_ID` | Frontend | Vercel project ID for the frontend |
| `RENDER_API_KEY` | Backend | Render API key |
| `RENDER_SERVICE_ID` | Backend | Render service ID for the backend |

Once those are set, pushes to `main` or a manual `workflow_dispatch` run will trigger deployment. This is the simplest GitHub-native path for a portfolio project because it keeps the deploy process versioned in the repo and uses the hosted platform's own deployment APIs.

## 1. Provision Postgres

Create a Postgres database on Neon or Supabase. Copy the connection string
— it looks like:

```
postgresql://<user>:<password>@<host>/<database>?sslmode=require
```

SQLAlchemy needs the `+psycopg2` driver marker; rewrite it to:

```
postgresql+psycopg2://<user>:<password>@<host>/<database>?sslmode=require
```

This full string is your backend's `DATABASE_URL`.

## 2. Deploy the backend (Render)

1. Push this repository to GitHub.
2. In Render: **New → Web Service**, connect the repo, set:
   - **Root directory:** `backend`
   - **Runtime:** Docker (Render will use `backend/Dockerfile` automatically)
   - **Health check path:** `/health`
3. Environment variables (Render dashboard → Environment):

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | the `postgresql+psycopg2://...` string from step 1 |
   | `CORS_ORIGINS` | your Vercel frontend URL, e.g. `https://apex-predict.vercel.app` |
   | `DATA_CACHE_DIR` | `/app/data/raw` |
   | `PROCESSED_DATA_DIR` | `/app/data/processed` |
   | `MODEL_ARTIFACT_DIR` | `/app/data/models` |

4. **Persistent disk:** attach a Render Disk mounted at `/app/data`. Without
   this, the container's first-boot data/ML pipeline run (see
   `backend/scripts/docker-entrypoint.sh`) repeats on every deploy/restart,
   which works but wastes ~1 minute and re-hits the Jolpica API each time.
   With a persistent disk, the pipeline runs once and subsequent deploys
   just migrate + reuse the existing data/models.
5. Deploy. First boot will take a minute or two while the container ingests
   data and trains the models (watch the logs — this is expected, not a
   hang). Once healthy, `https://<your-service>.onrender.com/health` should
   return `{"status": "ok"}`.

### Refreshing predictions for a new race weekend

The production model is a snapshot trained at container-build time. To pick
up newly completed races (so its rolling-form features stay current), either:

- Trigger a Render redeploy (re-runs the full pipeline if the persistent
  disk was cleared), or
- Exec into the running container / add a scheduled job that runs
  `./scripts/run_pipeline.sh` periodically (e.g. weekly via Render Cron
  Jobs, or a GitHub Actions workflow that calls a protected admin endpoint —
  not included in this project, since it's an operational concern beyond
  its scope as a portfolio demo).

## 3. Deploy the frontend (Vercel)

1. In Vercel: **New Project**, import the same repo.
2. **Root directory:** `frontend`
3. Environment variable:

   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_BASE_URL` | your Render backend URL, e.g. `https://apex-predict-api.onrender.com` |

4. Deploy. Vercel auto-detects Next.js — no build command override needed.

`NEXT_PUBLIC_*` variables are inlined into the client bundle at build time,
so setting this in Vercel's dashboard and redeploying is required any time
the backend URL changes (unlike server-only env vars, it can't be changed
at runtime without a rebuild).

## 4. Wire CORS

Make sure `CORS_ORIGINS` on the backend includes the exact Vercel URL
(including `https://`, no trailing slash). Multiple origins are comma-
separated. Requests from an unlisted origin will fail silently with a CORS
error in the browser console, not a clear API error — check this first if
the deployed frontend can't reach the API.

## 5. Verify

- `GET https://<backend>/health` → `{"status": "ok"}`
- `GET https://<backend>/api/races/upcoming` → a real race
- Open the frontend URL, confirm the homepage shows a live next race and
  the Model Lab page loads real metrics.

## Database migrations in production

Migrations run automatically as part of `docker-entrypoint.sh`
(`alembic upgrade head`) on every container start, before the API starts
serving. To run a migration manually against the production database from
your machine:

```bash
cd backend
DATABASE_URL="postgresql+psycopg2://..." alembic upgrade head
```

## Local Docker Compose vs. cloud deployment

`docker-compose.yml` at the repo root is for **local** development (spins
up its own Postgres container). It is not used by the Vercel/Render
deployment above — each cloud service builds directly from
`backend/Dockerfile` / `frontend/Dockerfile` against the managed Postgres
instance instead.
