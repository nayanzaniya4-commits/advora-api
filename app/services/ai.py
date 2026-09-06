import base64
import json
import re
from pathlib import Path

import httpx

from app.config import settings
from app.models import ProductAnalysis, AdPlan, Scene


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def analyze_product(image_path: str) -> ProductAnalysis:
    """
    Runs a real vision call when an OpenAI-compatible provider is configured
    (AI_BASE_URL / AI_API_KEY / AI_MODEL in .env). Without those set, it
    returns a safe generic analysis so the rest of the pipeline can still be
    tested end-to-end locally.
    """
    if not (settings.AI_BASE_URL and settings.AI_API_KEY and settings.AI_MODEL):
        return ProductAnalysis(
            product_name="Uploaded Product",
            category="general product",
            colors=[],
            material=None,
            style="premium",
            target_audience="general consumers",
            key_features=["visual product design", "brand-ready presentation"],
            visual_description="Product image supplied by the user.",
            confidence=0.35,
        )

    data = base64.b64encode(Path(image_path).read_bytes()).decode()
    prompt = """Analyze this product image for an advertising app.
Return ONLY valid JSON with:
product_name, category, colors (array), material, style, target_audience,
key_features (array), visual_description, confidence (0 to 1).
Do not invent exact technical specifications that cannot be seen."""

    payload = {
        "model": settings.AI_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}},
            ],
        }],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {settings.AI_API_KEY}"}
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(settings.AI_BASE_URL, json=payload, headers=headers)
        r.raise_for_status()
        body = r.json()
        content = body["choices"][0]["message"]["content"]
    return ProductAnalysis(**_extract_json(content))


def create_ad_plan(analysis: ProductAnalysis, brand_name: str | None = None) -> AdPlan:
    name = brand_name or "Your Brand"
    product = analysis.product_name
    feature1 = analysis.key_features[0] if analysis.key_features else "premium design"

    scenes = [
        Scene(
            scene_number=1, start_sec=0, end_sec=3,
            visual_prompt=f"Cinematic product reveal of {product}, clean premium background, slow push-in, realistic lighting.",
            on_screen_text="MEET THE NEW STANDARD",
        ),
        Scene(
            scene_number=2, start_sec=3, end_sec=6,
            visual_prompt=f"Macro close-up of {product}, highlight {feature1}, shallow depth of field, smooth camera slide.",
            on_screen_text="DETAILS THAT STAND OUT",
        ),
        Scene(
            scene_number=3, start_sec=6, end_sec=10,
            visual_prompt=f"Dynamic lifestyle shot featuring {product} in a setting suited to {analysis.target_audience}, elegant motion.",
            on_screen_text="MADE FOR YOU",
        ),
        Scene(
            scene_number=4, start_sec=10, end_sec=13,
            visual_prompt=f"Hero lifestyle composition of {product}, premium commercial cinematography, subtle motion and reflections.",
            on_screen_text="FEEL THE DIFFERENCE",
        ),
        Scene(
            scene_number=5, start_sec=13, end_sec=15,
            visual_prompt=f"Final hero shot of {product} with {name} brand feel, centered composition, dramatic light, clean background.",
            on_screen_text="SHOP NOW",
            voiceover=f"Discover {product} today.",
        ),
    ]
    return AdPlan(
        concept=f"Premium cinematic launch campaign for {product}",
        headline=f"Experience {product}",
        cta="Shop Now",
        music_mood="premium cinematic",
        scenes=scenes,
  )
