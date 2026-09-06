import uuid
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models import ProductAnalysis, AdPlan, ProjectResponse
from app.services.storage import save_upload, public_file_path
from app.services.ai import analyze_product, create_ad_plan
from app.services.design import create_template, create_stickers
from app.services.video import start_video_job, get_job

router = APIRouter()
PROJECTS = {}


@router.post("/analyze", response_model=ProductAnalysis)
async def analyze(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image.")
    path = save_upload(file.filename, await file.read())
    return await analyze_product(path)


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    file: UploadFile = File(...),
    brand_name: Optional[str] = Form(None),
    language: str = Form("English"),
    aspect_ratio: str = Form("9:16"),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image.")
    image_path = save_upload(file.filename, await file.read())
    analysis = await analyze_product(image_path)
    plan = create_ad_plan(analysis, brand_name)
    project_id = uuid.uuid4().hex
    template = create_template(image_path, plan.headline, plan.cta)
    stickers = create_stickers(plan.headline)

    prompt = " ".join(s.visual_prompt for s in plan.scenes)
    job_id = start_video_job(prompt, None, 15)

    PROJECTS[project_id] = {
        "project_id": project_id,
        "status": "processing",
        "analysis": analysis,
        "ad_plan": plan,
        "video_job_id": job_id,
        "template_url": public_file_path(template),
        "stickers": [public_file_path(x) for x in stickers],
        "language": language,
        "aspect_ratio": aspect_ratio,
    }
    return PROJECTS[project_id]


@router.post("/ad/direct", response_model=AdPlan)
async def direct(
    product_name: str = Form("Uploaded Product"),
    category: str = Form("general product"),
    brand_name: Optional[str] = Form(None),
):
    analysis = ProductAnalysis(product_name=product_name, category=category)
    return create_ad_plan(analysis, brand_name)


@router.post("/video/generate")
async def video_generate(
    prompt: str = Form(...),
    image_url: Optional[str] = Form(None),
    duration: int = Form(15),
):
    if not 1 <= duration <= 20:
        raise HTTPException(400, "Duration must be between 1 and 20 seconds.")
    job_id = start_video_job(prompt, image_url, duration)
    return {"job_id": job_id, "status": "queued"}


@router.get("/video/{job_id}")
async def video_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Video job not found.")
    return {"job_id": job_id, **job}


@router.post("/template/generate")
async def template_generate(
    file: UploadFile = File(...),
    headline: str = Form("Experience the difference"),
    cta: str = Form("Shop Now"),
):
    path = save_upload(file.filename, await file.read())
    output = create_template(path, headline, cta)
    return {"template_url": public_file_path(output)}


@router.post("/stickers/generate")
async def stickers_generate(headline: str = Form("Premium Product")):
    stickers = create_stickers(headline)
    return {"stickers": [public_file_path(x) for x in stickers]}


@router.get("/projects")
async def list_projects():
    return list(PROJECTS.values())


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = PROJECTS.get(project_id)
    if not project:
        raise HTTPException(404, "Project not found.")
    job = get_job(project["video_job_id"])
    if job and job.get("status") == "completed":
        project["status"] = "completed"
        project["video_url"] = job.get("video_url")
    elif job and job.get("status") == "failed":
        project["status"] = "failed"
    return project


@router.post("/webhooks/video")
async def video_webhook(payload: dict):
    return {"received": True}
