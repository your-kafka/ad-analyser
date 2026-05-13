"""
extracter.py  ·  Step 1 of 3  [UPDATED — Color Psychology Edition]
---------------------------------------------------------------------
Takes each ad image + its copy text and asks an AI vision model
to fill out a structured "blueprint" of the ad's anatomy.

UPDATE (Color Psychology):
  The AdBlueprint now includes two new fields:
    dominant_colors — the 1-3 most visually prominent colors in the ad
    color_count     — how many distinct colors dominate the palette

  These fields feed directly into color_analyzer.py's scoring rubric,
  which is grounded in Swarnakar (2024): "The Role of Color Psychology
  in Advertisement."
"""

import os
import json
import base64
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv
import json as _json

load_dotenv()

# Wake up the AI client
ai_client = Groq()


# ──────────────────────────────────────────────────────────────
# 1.  THE BLUEPRINT  ·  Forces the AI to give us consistent data
# ──────────────────────────────────────────────────────────────

from typing import List, Optional
from pydantic import BaseModel, Field

class AdBlueprint(BaseModel):
    brand_name: str = Field(
        default="Unknown Brand",
        description="The brand or company being advertised (e.g. 'Instamart', 'Zomato')."
    )
    image_description: str = Field(
        default="No description provided",
        description=(
            "A factual description of the visual: people, objects, setting, "
            "colors, text overlays, and layout."
        )
    )
    ad_copy: str = Field(
        default="No text found",
        description="The full text copy of the ad, exactly as written."
    )
    hook: str = Field(
        default="No hook identified",
        description=(
            "The single phrase or visual element that is designed to stop a "
            "thumb from scrolling in the first 1-2 seconds."
        )
    )
    # This was the specific field causing the crash:
    call_to_action: str = Field(
        default="None found",
        description=(
            "The exact action the ad tells the viewer to take. "
            "Write 'None found' if there is no explicit CTA."
        )
    )
    visual_style: str = Field(
        default="Standard",
        description="The overall aesthetic: color palette, mood, photography vs illustration."
    )
    emotional_appeal: str = Field(
        default="Convenience",
        description=(
            "The core emotion: Convenience | FOMO | Aspiration | Humor | Trust | "
            "Price Shock | Social Proof | Curiosity."
        )
    )
    target_audience: str = Field(
        default="General Audience",
        description="Who this ad seems to be speaking to."
    )

    # ── NEW FIELDS: Color Psychology (Swarnakar, 2024) ──────────
    dominant_colors: List[str] = Field(
        default_factory=list,
        description=(
            "The 1 to 3 most visually dominant colors in this ad. "
            "Use only: red, blue, yellow, green, black, white, orange, purple, gold, pink, brown, grey."
        )
    )
    color_count: int = Field(
        default=0,
        description="The total number of distinct, visually significant colors. Typically 1–5."
    )

# ──────────────────────────────────────────────────────────────
# 2.  IMAGE TRANSLATOR  ·  Converts a file into AI-readable code
# ──────────────────────────────────────────────────────────────

def image_to_base64(filepath: str) -> str:
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# ──────────────────────────────────────────────────────────────
# 3.  THE BRAIN  ·  Sends the ad to the AI and gets the blueprint
# ──────────────────────────────────────────────────────────────

def extract_insights_with_ai(image_path: str, text_copy: str) -> AdBlueprint:
    """
    Sends one ad (image + copy) to the AI vision model.
    The AI acts as a senior marketing analyst and fills out
    our AdBlueprint form. Returns a clean Python object.
    """
    image_code = image_to_base64(image_path)

    system_prompt = (
        "You are a senior direct-response marketing analyst with 15 years of experience "
        "breaking down what makes consumer ads succeed or fail. "
        "You are precise, observational, and never use vague phrases like 'engaging visuals'. "
        "You always back your observations with specific details from the actual ad. "
        "For color analysis, you are trained in color psychology — you identify dominant colors "
        "accurately and understand their psychological significance in advertising."
    )

    user_prompt = f"""
Analyze the ad image attached and the surrounding copy text below.

Ad copy text: "{text_copy}"

Return ONLY a valid JSON object with exactly these keys filled in. No extra keys, no schema, no explanation — just the filled JSON.

IMPORTANT for the color fields:
- dominant_colors: list of 1-3 most dominant color names (use only: red, blue, yellow, green, black, white, orange, purple, gold, pink, brown, grey)
- color_count: total number of distinct visible colors in the ad

Return exactly this structure with real values filled in:

{{
  "brand_name": "brand name shown in the ad",
  "image_description": "factual description of what is visually shown",
  "ad_copy": "full text copy from the ad",
  "hook": "the single phrase designed to stop scrolling in 1-2 seconds",
  "call_to_action": "exact CTA text, or None found",
  "visual_style": "2-3 sentences on aesthetic, palette, mood",
  "emotional_appeal": "Convenience or FOMO or Aspiration or Humor or Trust or Price Shock or Social Proof or Curiosity — with brief explanation",
  "target_audience": "who this ad is speaking to",
  "dominant_colors": ["color1", "color2"],
  "color_count": 3
}}
"""

    response = ai_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_code}"},
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    raw_output = json.loads(response.choices[0].message.content)
    return AdBlueprint(**raw_output)


# ──────────────────────────────────────────────────────────────
# 4.  PIPELINE RUNNER  ·  Loops over all ads in the data folder
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    folder_path    = "data"
    text_data_file = os.path.join(folder_path, "ad_copy.json")

    print("🔍 Starting AI Extraction — reading every ad like a marketing expert...\n")

    with open(text_data_file, "r", encoding="utf-8") as file:
        all_ads_text = json.load(file)

    structured_results = {}

    for image_name, text_copy in all_ads_text.items():
        image_filepath = os.path.join(folder_path, image_name)

        if not os.path.exists(image_filepath):
            print(f"   ⚠️  Skipping {image_name} — image file not found.\n")
            continue

        try:
            print(f"👀  Analyzing {image_name}...")
            blueprint = extract_insights_with_ai(image_filepath, text_copy)
            structured_results[image_name] = blueprint.dict()
            print(f"   ✅  Done. Hook: '{blueprint.hook}' | Colors: {blueprint.dominant_colors}\n")

        except Exception as e:
            print(f"   ❌  Failed on {image_name}: {e}\n")

    output_file = os.path.join(folder_path, "extracted_ads.json")
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(structured_results, file, indent=4, ensure_ascii=False)

    print(f"\n🎉 Extraction complete! Data saved to '{output_file}'.")
    print("Next step: run  python scorer.py")