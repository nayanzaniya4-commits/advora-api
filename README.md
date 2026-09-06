# AdVora AI — FastAPI API Starter

This backend implements the AdVora AI zero-prompt advertising flow:

Product Photo → Product Analysis → AI Ad Director → 15-sec Video Job → Template → 5 Stickers

## 1. Run locally

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

Open http://localhost:8000/docs for the interactive Swagger UI.

## 2. What's real vs placeholder

- Photo upload, storage, routing — fully working
- Product analysis — real if AI_BASE_URL/AI_API_KEY/AI_MODEL are set, generic placeholder otherwise
- 15-sec storyboard and ad copy — fully working, no extra API needed
- Template image and 5 stickers — fully working, real files rendered with Pillow
- Video generation — real once REPLICATE_API_TOKEN is set, safe test mode otherwise
- Saving projects to Supabase — schema provided in sql/schema.sql, not yet wired into routes.py

## 3. Deploy

docker build -t advora-api .
docker run -p 8000:8000 --env-file .env advora-api

Or connect this repo directly to Railway or Render — they auto-detect the Dockerfile.

## 4. Endpoints

- POST /api/v1/analyze — photo in, product analysis out
- POST /api/v1/projects — full pipeline: photo in, everything out
- GET /api/v1/projects/{id} — poll project status
- GET /api/v1/projects — list all projects, in-memory only
- POST /api/v1/video/generate — standalone video job
- GET /api/v1/video/{job_id} — poll video job
- POST /api/v1/template/generate — just the template
- POST /api/v1/stickers/generate — just the stickers
