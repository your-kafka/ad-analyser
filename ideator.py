"""
ideator.py  ·  Step 3 of 3
---------------------------
Analyzes the gap between top and bottom performers, then generates 
concrete creative concepts grounded in evidence.

FIXED: Handled potential string formatting errors for Streamlit Cloud.
"""

import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

# ──────────────────────────────────────────────────────────────
# 1.  PATTERN DETECTIVE  ·  What separates winners from losers?
# ──────────────────────────────────────────────────────────────

def extract_patterns(scored_ads: list) -> dict:
    """
    Looks at the top half vs. bottom half of the leaderboard.
    Returns a dictionary of concrete patterns or an error if data is insufficient.
    """
    if len(scored_ads) < 2:
        return {"error": "Need at least 2 ads to find patterns."}

    # Split into top and bottom halves
    midpoint = max(1, len(scored_ads) // 2)
    winners = scored_ads[:midpoint]
    losers  = scored_ads[midpoint:]

    def avg_score(ads):
        if not ads: return 0.0
        return sum(a["final_score"] for a in ads) / len(ads)

    def most_common_emotion(ads):
        return [a["ad_data"].get("emotional_appeal", "")[:30] for a in ads]

    def common_hooks(ads):
        return [a["ad_data"].get("hook", "") for a in ads]

    def common_ctas(ads):
        return [a["ad_data"].get("call_to_action", "") for a in ads]

    def avg_dimension(ads, dimension):
        scores = [
            a.get("score_breakdown", {}).get(dimension, {}).get("score", 0)
            for a in ads
        ]
        return round(sum(scores) / len(scores), 1) if scores else 0.0

    dimension_names = ["Hook Strength", "CTA Clarity", "Emotional Punch", "Visual-Copy Fit", "Audience Focus"]

    winner_dims = {d: avg_dimension(winners, d) for d in dimension_names}
    loser_dims  = {d: avg_dimension(losers,  d) for d in dimension_names}

    # Find the dimensions where winners most outperform losers
    gaps = {d: winner_dims[d] - loser_dims[d] for d in dimension_names}
    biggest_gap = max(gaps, key=gaps.get)

    return {
        "winner_avg_score": avg_score(winners),
        "loser_avg_score":  avg_score(losers),
        "winner_hooks":     common_hooks(winners),
        "loser_hooks":      common_hooks(losers),
        "winner_ctas":      common_ctas(winners),
        "winner_emotions":  most_common_emotion(winners),
        "dimension_scores": {
            "winners": winner_dims,
            "losers":  loser_dims,
        },
        "biggest_winner_advantage": biggest_gap,
        "gap_amount": gaps[biggest_gap],
    }


# ──────────────────────────────────────────────────────────────
# 2.  THE IDEA GENERATOR  ·  Grounded in patterns
# ──────────────────────────────────────────────────────────────

def generate_new_creative_ideas(brand_name: str = "the brand") -> str:
    """
    Analyzes patterns and generates 4 evidence-based ad concepts.
    """
    scored_ads_path = "data/scored_ads.json"

    if not os.path.exists(scored_ads_path):
        return "❌ No scored_ads.json found. Run scorer.py first."

    with open(scored_ads_path, "r") as f:
        scored_ads = json.load(f)

    # Perform analysis
    patterns = extract_patterns(scored_ads)
    
    # --- CRITICAL FIX: Ensure values are numbers before formatting with :.1f ---
    win_score  = patterns.get('winner_avg_score', 0.0)
    loss_score = patterns.get('loser_avg_score', 0.0)
    gap_adv    = patterns.get('biggest_winner_advantage', 'None')
    gap_val    = patterns.get('gap_amount', 0.0)

    # Build prompt
    prompt = f"""
You are a Creative Strategist preparing a brief for a {brand_name} ad team.

I've analyzed {len(scored_ads)} ads and found these patterns:

WHAT'S WORKING (top performers average {win_score:.1f}/10):
- Their hooks: {json.dumps(patterns.get('winner_hooks', []), indent=2)}
- Their CTAs: {json.dumps(patterns.get('winner_ctas', []), indent=2)}
- Their emotional appeals: {json.dumps(patterns.get('winner_emotions', []), indent=2)}

WHAT'S FAILING (bottom performers average {loss_score:.1f}/10):
- Their weaker hooks: {json.dumps(patterns.get('loser_hooks', []), indent=2)}

BIGGEST GAP FOUND:
Winners outperform losers most on "{gap_adv}" by {gap_val:.1f} points out of 2.

Based on this evidence, generate exactly 4 creative ad concepts to test next.

For EACH concept, provide:
1. HYPOTHESIS: What pattern from the data are you testing?
2. VISUAL CONCEPT: Describe the image in one vivid sentence.
3. HOOK: The opening line (max 8 words).
4. BODY COPY: Supporting text (2-3 sentences max).
5. CTA: The button text.
6. WHY THIS WILL WORK: Connect back to the analysis data.

Think like a scientist designing experiments. Every recommendation must tie back to a specific insight.
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": "You are a direct-response creative strategist. Your ideas are specific, testable, and grounded in data."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.75,
        max_tokens=2000,
    )

    return response.choices[0].message.content


# ──────────────────────────────────────────────────────────────
# PIPELINE RUNNER
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🧠 Detecting patterns and generating new test concepts...\n")

    brand = "the brand"
    if os.path.exists("data/scored_ads.json"):
        with open("data/scored_ads.json") as f:
            data = json.load(f)
        if data:
            brand = data[0].get("ad_data", {}).get("brand_name", brand)

    ideas = generate_new_creative_ideas(brand_name=brand)

    output_path = "data/new_ideas.txt"
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ideas)

    print(ideas)
    print(f"\n💾 Ideas saved to '{output_path}'")