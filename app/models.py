from typing import List, Optional
from pydantic import BaseModel, Field


class ProductAnalysis(BaseModel):
    product_name: str = "Unknown Product"
    category: str = "general"
    colors: List[str] = []
    material: Optional[str] = None
    style: str = "premium"
    target_audience: str = "general consumers"
    key_features: List[str] = []
    visual_description: str = ""
    confidence: float = Field(default=0.5, ge=0, le=1)


class Scene(BaseModel):
    scene_number: int
    start_sec: float
    end_sec: float
    visual_prompt: str
    on_screen_text: Optional[str] = None
    voiceover: Optional[str] = None


class AdPlan(BaseModel):
    concept: str
    headline: str
    cta: str = "Shop Now"
    music_mood: str = "cinematic premium"
    scenes: List[Scene]


class VideoJob(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    video_url: Optional[str] = None
    error: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: str
    status: str
    analysis: Optional[ProductAnalysis] = None
    ad_plan: Optional[AdPlan] = None
    video_job_id: Optional[str] = None
    template_url: Optional[str] = None
    stickers: List[str] = []
