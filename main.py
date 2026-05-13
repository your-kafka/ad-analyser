"""
main.py  ·  Terminal Pipeline Runner  [UPDATED — Color Psychology Edition]
---------------------------------------------------------------------------
Run this if you want to execute all 3 steps from the command line
without opening the Streamlit UI.

UPDATE (Color Psychology):
  Step 2 now runs a 6-dimension rubric (PACT × 5 + Color Psychology × 1).
  Raw score is 12 pts, normalized back to 10 for the leaderboard.
  Color Psychology dimension is grounded in:
    Swarnakar (2024) — "The Role of Color Psychology in Advertisement"

Prerequisites:
  - Your ad images are in the /data folder
  - /data/ad_copy.json exists and maps image filenames to copy text
  - GROQ_API_KEY is set in your .env file

Usage:
  python main.py
"""

import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()


def print_header(step: str, description: str):
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"  {description}")
    print(f"{'='*60}\n")


def step_1_extract():
    """
    Reads each image + its copy text and asks the AI to fill out
    a structured blueprint (hook, CTA, visual style, emotion, audience,
    dominant_colors, color_count).
    Output: data/extracted_ads.json
    """
    print_header(
        "STEP 1 / 3  ·  EXTRACTION",
        "AI reads every ad — including dominant colors — like a marketing analyst"
    )

    result = subprocess.run(["python", "extracter.py"], capture_output=False)

    if result.returncode != 0:
        print("❌ Extraction failed. Check the error above.")
        return False

    if not os.path.exists("data/extracted_ads.json"):
        print("❌ extracted_ads.json was not created. Something went wrong.")
        return False

    with open("data/extracted_ads.json") as f:
        data = json.load(f)

    print(f"\n✅ Extracted data for {len(data)} ads.")

    # Quick color preview
    for name, ad in list(data.items())[:3]:
        colors = ad.get("dominant_colors", [])
        print(f"   {name}: colors detected → {colors}")

    return True


def step_2_score():
    """
    Applies the 6-dimension rubric to each extracted ad:
      5 dimensions from the PACT (1982) framework
      1 new dimension: Color Psychology (Swarnakar, 2024)

    Raw total: 12 pts → normalized to 10 for the leaderboard.
    Output: data/scored_ads.json
    """
    print_header(
        "STEP 2 / 3  ·  SCORING",
        "6-dimension rubric: PACT (Hook, CTA, Emotion, Visual Fit, Audience) + Color Psychology"
    )

    result = subprocess.run(["python", "scorer.py"], capture_output=False)

    if result.returncode != 0:
        print("❌ Scoring failed. Check the error above.")
        return False

    if not os.path.exists("data/scored_ads.json"):
        print("❌ scored_ads.json was not created. Something went wrong.")
        return False

    with open("data/scored_ads.json") as f:
        data = json.load(f)

    if data:
        best  = data[0]
        worst = data[-1]
        print(f"\n✅ Scored {len(data)} ads  (raw /12 → normalized /10).")
        print(f"   Best:  {best['image_name']}  "
              f"({best['final_score']}/10  ·  raw {best.get('raw_score', '?')}/12)")
        print(f"   Worst: {worst['image_name']}  "
              f"({worst['final_score']}/10  ·  raw {worst.get('raw_score', '?')}/12)")

        # Surface any color psychology failures
        color_failures = [
            a["image_name"] for a in data
            if a.get("score_breakdown", {}).get("Color Psychology", {}).get("score", 2) == 0
        ]
        if color_failures:
            print(f"\n   ⚠️  Color Psychology score of 0 (fatal flaw) in:")
            for name in color_failures:
                print(f"      • {name}")

    return True


def step_3_ideate():
    """
    Analyzes the gap between top and bottom performers, then generates
    4 concrete creative concepts grounded in those specific patterns.
    Output: data/new_ideas.txt (printed to console too)
    """
    print_header(
        "STEP 3 / 3  ·  IDEATION",
        "Finding patterns (incl. color), then generating next test concepts"
    )

    result = subprocess.run(["python", "ideator.py"], capture_output=False)

    if result.returncode != 0:
        print("❌ Ideation failed. Check the error above.")
        return False

    return True


def main():
    print("\n🚀  ATOMIC AD ANALYZER  —  FULL PIPELINE")
    print("   Extract → Score (6 dimensions) → Ideate\n")
    print("   Scoring framework:")
    print("     • Hook Strength    — PACT ④ (attention model)")
    print("     • CTA Clarity      — PACT ① (relevant to objective)")
    print("     • Emotional Punch  — PACT ④ (ELM peripheral route)")
    print("     • Visual-Copy Fit  — PACT ③ (multiple measurements)")
    print("     • Audience Focus   — PACT ① (right universe)")
    print("     • Color Psychology — Swarnakar (2024) [NEW]")
    print("   Raw: 12 pts → Normalized: 10 pts\n")

    if not os.path.exists("data"):
        print("❌ No 'data' folder found.")
        print("   Create one with your ad images and an ad_copy.json file.")
        print("   Or use  streamlit run app.py  to upload directly in the browser.")
        return

    if not os.path.exists("data/ad_copy.json"):
        print("❌ No 'data/ad_copy.json' found.")
        print("   Create a JSON file mapping image filenames to their copy text:")
        print('   { "ad1.jpg": "10 minutes to your door. Order now.", ... }')
        return

    if not step_1_extract():
        return
    if not step_2_score():
        return
    if not step_3_ideate():
        return

    print("\n" + "="*60)
    print("  ✅  ALL DONE!")
    print("  Check these files for the full output:")
    print("    data/extracted_ads.json  ·  blueprints (incl. colors)")
    print("    data/scored_ads.json     ·  ranked leaderboard (6 dimensions)")
    print("    data/new_ideas.txt       ·  creative concepts")
    print("\n  To explore in the UI:")
    print("    streamlit run app.py")
    print("    → New tab: 🎨 Color Analysis")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()