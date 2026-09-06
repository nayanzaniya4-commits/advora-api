import asyncio
import uuid

import httpx

from app.config import settings

JOBS = {}


async def _replicate_prediction(prompt: str, image_url: str | None, duration: int):
    if not settings.REPLICATE_API_TOKEN:
        return None

    payload = {"input": {"prompt": prompt, "duration": duration}}
    if image_url:
        payload["input"]["image"] = image_url

    headers = {
        "Authorization": f"Bearer {settings.REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait",
    }
    url = "https://api.replicate.com/v1/models/" + settings.VIDEO_MODEL + "/predictions"
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()


async def generate_video(job_id: str, prompt: str, image_url: str | None = None, duration: int = 15):
    JOBS[job_id] = {"status": "processing", "progress": 10, "video_url": None, "error": None}
    try:
        if not settings.REPLICATE_API_TOKEN:
            # Test mode: no paid provider is called, so no real video is produced.
            await asyncio.sleep(1)
            JOBS[job_id] = {
                "status": "completed",
                "progress": 100,
                "video_url": None,
                "error": None,
                "message": "Test mode: set REPLICATE_API_TOKEN in .env for real video generation.",
            }
            return

        result = await _replicate_prediction(prompt, image_url, duration)
        output = result.get("output") if result else None
        if isinstance(output, list):
            output = output[0] if output else None
        JOBS[job_id] = {"status": "completed", "progress": 100, "video_url": output, "error": None}
    except Exception as e:
        JOBS[job_id] = {"status": "failed", "progress": 100, "video_url": None, "error": str(e)}


def start_video_job(prompt: str, image_url: str | None = None, duration: int = 15):
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"status": "queued", "progress": 0, "video_url": None, "error": None}
    asyncio.create_task(generate_video(job_id, prompt, image_url, duration))
    return job_id


def get_job(job_id: str):
    return JOBS.get(job_id)
