"""
scorer.py  ·  Step 2 of 3  [UPDATED — Color Psychology Edition]
-----------------------------------------------------------------
Takes the structured blueprints from extracter.py and assigns
each ad a score AND a clear verdict a marketing team can act on.

UPDATE (Color Psychology):
  Added a 6th scoring dimension: Color Psychology (2 pts)
  Sourced from color_analyzer.py, which is grounded in:
    Swarnakar (2024) — "The Role of Color Psychology in Advertisement"

  New total: 12 raw points → normalized back to 10 for consistency.
  Normalization formula: final_score = round((raw / 12) * 10)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHERE THIS RUBRIC COMES FROM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The original 5 dimensions are grounded in the PACT (1982) framework.
The 6th dimension (Color Psychology) is grounded in:

  Swarnakar, S. (2024). The Role of Color Psychology in Advertisement.
  Published in: Advertising Methods, Research and Practices.
  Adamas Knowledge City, West Bengal, India.

  Key finding: "90% of initial product judgments are based solely on color"
  (Kumar, 2017, cited in Swarnakar 2024). Color is not decoration —
  it is a primary persuasion signal that the PACT framework does not
  explicitly address. This dimension fills that gap.

Our 6 scoring dimensions:
  Hook Strength      → PACT ④ (attention model)
  CTA Clarity        → PACT ① (relevant to objective)
  Emotional Punch    → PACT ④ (peripheral route persuasion, ELM)
  Visual-Copy Fit    → PACT ③ (multiple measurements)
  Audience Focus     → PACT ① (right universe)
  Color Psychology   → Swarnakar (2024) (color-emotion-brand alignment)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
from color_analyzer import score_color_psychology   # ← NEW IMPORT


# ──────────────────────────────────────────────────────────────
# DIMENSIONS 1–5  (unchanged from original scorer.py)
# ──────────────────────────────────────────────────────────────

def score_hook_strength(ad: dict) -> tuple[int, str, str]:
    """
    PACT PRINCIPLE ④ — Model of human response.
    Information Processing Model (McGuire, 1978):
    Exposure → Attention → Comprehension → Intent.
    """
    hook = ad.get("hook", "").lower()

    strong_signals = [
        "?" in hook,
        any(c.isdigit() for c in hook),
        len(hook.split()) <= 8,
        any(w in hook for w in [
            "never", "only", "just", "finally", "stop",
            "secret", "why", "how", "warning", "free"
        ]),
    ]

    hits = sum(strong_signals)

    if hits >= 3:
        return (2, "Hook is sharp — short, specific, and curiosity-triggering.",
                "Already strong. Consider A/B testing one alternate version.")
    elif hits >= 1:
        return (1, "Hook works but won't stop a fast scroll reliably.",
                "Add a number or turn it into a question. Example: 'Why does X?' or 'Only 3 left'.")
    else:
        return (0, "Hook is too generic — it won't interrupt a scrolling thumb.",
                "Rewrite completely. Lead with the biggest surprise or the sharpest benefit.")


def score_cta_clarity(ad: dict) -> tuple[int, str, str]:
    """PACT PRINCIPLE ① — Relevant to objectives."""
    cta = ad.get("call_to_action", "").lower()

    if not cta or cta in ["none found", "none", "n/a", ""]:
        return (0, "No CTA found — the ad leaves the viewer with nowhere to go.",
                "Add a direct action line: 'Order Now', 'Download Today', 'Get Yours Free'.")

    action_verbs  = ["order", "buy", "get", "download", "grab", "shop",
                     "claim", "book", "try", "start", "join", "save"]
    urgency_words = ["now", "today", "limited", "free", "first", "instant",
                     "hurry", "last", "only", "ends"]

    has_verb    = any(v in cta for v in action_verbs)
    has_urgency = any(u in cta for u in urgency_words)

    if has_verb and has_urgency:
        return (2, f"CTA is strong — '{cta}' combines action and urgency.",
                "Already solid. Test a benefit-driven variant: 'Get 10 min delivery — Order Now'.")
    elif has_verb:
        return (1, f"CTA has a clear action ('{cta}') but lacks urgency.",
                "Add a time or scarcity signal: 'Order Now', 'Get It Today', 'Only 50 left'.")
    else:
        return (1, f"CTA exists but is passive — it doesn't drive action.",
                "Replace with a verb: 'Learn More' → 'Start Free Today'. Passive CTAs leak conversions.")


def score_emotional_clarity(ad: dict) -> tuple[int, str, str]:
    """PACT PRINCIPLE ④ — Elaboration Likelihood Model (Petty & Cacioppo, 1986)."""
    emotional_appeal = ad.get("emotional_appeal", "").lower()
    copy = ad.get("ad_copy", "").lower()

    KNOWN_TRIGGERS = [
        "convenience", "fomo", "aspiration", "humor",
        "trust", "price shock", "social proof", "curiosity", "fear"
    ]

    emotion_identified = any(trigger in emotional_appeal for trigger in KNOWN_TRIGGERS)

    DELIVERY_WORDS = {
        "convenience": ["delivered", "minutes", "doorstep", "instant", "fast", "quick"],
        "fomo":        ["limited", "ends", "only", "last", "hurry", "almost gone"],
        "aspiration":  ["dream", "style", "premium", "best", "deserve", "upgrade"],
        "humor":       ["😂", "lol", "funny", "wait what", "seriously though"],
        "trust":       ["guaranteed", "certified", "safe", "proven", "trusted", "rated"],
        "price shock": ["₹", "$", "free", "off", "%", "deal", "save", "cheap"],
        "social proof":["lakh", "crore", "million", "rated", "customers", "reviews", "people love"],
        "curiosity":   ["secret", "this is why", "you won't believe", "here's what"],
        "fear":        ["don't miss", "before it's gone", "risk", "warning"],
    }

    copy_delivers = False
    for trigger in KNOWN_TRIGGERS:
        if trigger in emotional_appeal:
            words = DELIVERY_WORDS.get(trigger, [])
            if any(w in copy for w in words):
                copy_delivers = True
                break

    if emotion_identified and copy_delivers:
        return (2, f"Emotion is clear and the copy earns it — '{emotional_appeal[:40]}'.",
                "Strong. Consider testing a second emotional angle.")
    elif emotion_identified:
        return (1, "Emotional direction is clear but the copy doesn't land the feeling.",
                "Rewrite the body copy to use words that trigger that specific emotion.")
    else:
        return (0, "No clear emotional direction — the ad is trying to say too many things.",
                "Pick ONE feeling. Every word should serve it.")


def score_visual_copy_fit(ad: dict) -> tuple[int, str, str]:
    """PACT PRINCIPLE ③ — Use multiple measurements (dual-coding theory)."""
    image_desc = ad.get("image_description", "").lower()
    copy       = ad.get("ad_copy", "").lower()

    if "text overlay" in image_desc or "product" in image_desc or "logo" in image_desc:
        return (2, "Image reinforces the message directly — product or brand is front and center.",
                "Good alignment. Make sure the text overlay isn't competing with the body copy.")

    themes = ["price", "speed", "quality", "family", "food",
              "delivery", "offer", "fresh", "home", "savings"]
    shared = sum(1 for t in themes if t in image_desc and t in copy)

    if shared >= 2:
        return (2, f"Image and copy share {shared} themes — they're telling the same story.",
                "Solid. Ensure the visual leads with the emotion, not just the product.")
    elif shared == 1:
        return (1, "Image and copy partially align, but they could reinforce each other more.",
                "Identify the single most important message and make both visual AND headline reflect it.")
    else:
        return (0, "Image and copy seem to be telling different stories.",
                "Major misalignment. Either change the image to match the copy, or rewrite the copy to match the image.")


def score_audience_focus(ad: dict) -> tuple[int, str, str]:
    """PACT PRINCIPLE ① — Test the proper universe (FTC copy testing method)."""
    audience = ad.get("target_audience", "").lower()

    if not audience:
        return (0, "No audience defined — can't evaluate fit.",
                "Define your audience before anything else: age, lifestyle, specific pain point.")

    generic_phrases  = ["everyone", "all ages", "general", "broad", "anyone", "all people"]
    specific_signals = ["professional", "parent", "student", "urban", "budget",
                        "working", "millennial", "young", "family", "age", "who"]

    is_generic  = any(p in audience for p in generic_phrases)
    is_specific = any(s in audience for s in specific_signals)

    if is_specific and not is_generic:
        return (2, "Audience is specific — the ad knows exactly who it's talking to.",
                "Good. Now check: does EVERY line of copy speak to that specific person?")
    elif is_generic:
        return (0, "Audience is too broad — ads for everyone convert no one.",
                "Narrow down. 'Working parents in metros who hate grocery lines' > 'everyone who shops'.")
    else:
        return (1, "Audience is somewhat defined but could be sharper.",
                "Add a specific life situation or pain point: not just 'urban users' but 'urban users who hate waiting'.")


# ──────────────────────────────────────────────────────────────
# DIMENSION 6 — COLOR PSYCHOLOGY (NEW)
# Wraps color_analyzer.score_color_psychology for use in DIMENSIONS list
# Grounded in: Swarnakar (2024), Kumar (2017), Broeder & Snijder (2019)
# ──────────────────────────────────────────────────────────────

def score_color_psychology_dimension(ad: dict) -> tuple[int, str, str]:
    """
    SWARNAKAR (2024) — Color Psychology in Advertising.

    "90% of initial product judgments are based solely on color." (Kumar, 2017)

    This dimension evaluates three axes (each 0-2, normalized to 0-2 total):
      1. Color-Emotion Match   — do the colors evoke the right emotions for this ad?
      2. Brand-Color Fit       — are these colors right for this product category?
      3. Color Consistency     — is the palette focused (≤2 colors) or scattered?

    A red-dominant ad selling trust-based services fails axis 1.
    A blue-dominant food ad fails axis 2 (blue suppresses appetite).
    A 6-color palette fails axis 3 (diluted message, weak recall).
    """
    return score_color_psychology(ad)


# ──────────────────────────────────────────────────────────────
# VERDICT GENERATOR  (updated for 12-pt raw / 10-pt normalized)
# ──────────────────────────────────────────────────────────────

def generate_verdict(total_score: int, breakdown: dict) -> dict:
    """
    Translates a normalized score (0-10) into a clear recommendation.
    Thresholds unchanged: 8-10 = Run, 5-7 = Test Further, 0-4 = Don't Run.

    Fatal flaw check extended to include Color Psychology:
      A score of 0 on Hook, CTA, OR Color Psychology is a dealbreaker.
      (Color: if 90% of first impressions are color-based, a score of 0
      means the palette is actively working against the ad's goals.)
    """
    hook_score  = breakdown.get("Hook Strength",    {}).get("score", 0)
    cta_score   = breakdown.get("CTA Clarity",       {}).get("score", 0)
    color_score = breakdown.get("Color Psychology",  {}).get("score", 0)

    has_fatal_flaw = (hook_score == 0 or cta_score == 0 or color_score == 0)

    if total_score >= 8 and not has_fatal_flaw:
        return {
            "verdict":       "✅ RUN IT",
            "verdict_short": "run",
            "reasoning":     (
                f"Score of {total_score}/10 with no critical failures. "
                "Ad is ready to air — color, copy, and targeting are all aligned."
            ),
            "next_action": "Launch and monitor CTR/conversion for 72 hours. Set as control for A/B tests."
        }
    elif total_score >= 5 and not has_fatal_flaw:
        weakest_dim = min(breakdown, key=lambda d: breakdown[d]["score"])
        weakest_fix = breakdown[weakest_dim].get("fix", "Fix the weakest dimension.")
        return {
            "verdict":       "⚠️ TEST FURTHER",
            "verdict_short": "test",
            "reasoning":     (
                f"Score of {total_score}/10. Has potential but '{weakest_dim}' "
                f"scored {breakdown[weakest_dim]['score']}/2."
            ),
            "next_action": f"Fix this first: {weakest_fix} Then retest before committing budget."
        }
    else:
        broken_dims = [d for d, v in breakdown.items() if v["score"] == 0]
        broken_str  = " and ".join(broken_dims) if broken_dims else "multiple dimensions"
        return {
            "verdict":       "❌ DON'T RUN",
            "verdict_short": "stop",
            "reasoning":     (
                f"Score of {total_score}/10. Fundamental problems in: {broken_str}. "
                "Running this will waste budget without moving metrics."
            ),
            "next_action": "Don't patch — rebuild. Start from audience + color palette and work forward."
        }


# ──────────────────────────────────────────────────────────────
# MASTER EVALUATOR  ·  6 dimensions + normalization + verdict
# ──────────────────────────────────────────────────────────────

DIMENSIONS = [
    ("Hook Strength",    score_hook_strength),
    ("CTA Clarity",      score_cta_clarity),
    ("Emotional Punch",  score_emotional_clarity),
    ("Visual-Copy Fit",  score_visual_copy_fit),
    ("Audience Focus",   score_audience_focus),
    ("Color Psychology", score_color_psychology_dimension),   # ← NEW (Swarnakar, 2024)
]

RAW_MAX = 12   # 6 dimensions × 2 pts each


def evaluate_ad(ad_elements: dict) -> dict:
    """
    Runs all 6 dimensions, normalizes the raw score (0-12) to 0-10,
    generates a verdict, and returns the complete evaluation.

    Normalization: final_score = round((raw_total / RAW_MAX) * 10)
    This keeps the leaderboard on a familiar 0-10 scale even with
    the new Color Psychology dimension added.
    """
    breakdown = {}
    raw_total = 0

    for dimension_name, scoring_fn in DIMENSIONS:
        score, reason, fix = scoring_fn(ad_elements)
        breakdown[dimension_name] = {
            "score":  score,
            "max":    2,
            "reason": reason,
            "fix":    fix,
        }
        raw_total += score

    # Normalize to 0-10
    normalized_total = round((raw_total / RAW_MAX) * 10)

    verdict = generate_verdict(normalized_total, breakdown)

    return {
        "total_score":     normalized_total,
        "raw_score":       raw_total,
        "raw_max":         RAW_MAX,
        "score_breakdown": breakdown,
        "verdict":         verdict,
    }


# ──────────────────────────────────────────────────────────────
# PIPELINE RUNNER
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    input_file  = "data/extracted_ads.json"
    output_file = "data/scored_ads.json"

    print("📊 Scoring ads — PACT (5 dimensions) + Color Psychology (Swarnakar, 2024)...\n")

    if not os.path.exists(input_file):
        print("❌ 'extracted_ads.json' not found. Run extracter.py first!")
        exit()

    with open(input_file, "r") as f:
        extracted_ads = json.load(f)

    final_rankings = []

    for filename, ad_data in extracted_ads.items():
        result = evaluate_ad(ad_data)
        final_rankings.append({
            "image_name":      filename,
            "final_score":     result["total_score"],
            "raw_score":       result["raw_score"],
            "score_breakdown": result["score_breakdown"],
            "verdict":         result["verdict"],
            "ad_data":         ad_data,
        })

    final_rankings.sort(key=lambda x: x["final_score"], reverse=True)

    with open(output_file, "w") as f:
        json.dump(final_rankings, f, indent=4, ensure_ascii=False)

    print("🏆  AD CREATIVE LEADERBOARD")
    print("=" * 60)
    for rank, ad in enumerate(final_rankings, 1):
        v = ad["verdict"]
        colors = ad["ad_data"].get("dominant_colors", [])
        print(f"\n#{rank}  {ad['image_name']}  —  {ad['final_score']}/10  (raw: {ad['raw_score']}/12)")
        print(f"     Colors: {colors}")
        print(f"     {v['verdict']}")
        print(f"     → {v['next_action']}")
        for dim, detail in ad["score_breakdown"].items():
            bar = "●" * detail["score"] + "○" * (detail["max"] - detail["score"])
            print(f"     [{bar}] {dim}: {detail['reason'][:70]}")

    run_count  = sum(1 for a in final_rankings if a["verdict"]["verdict_short"] == "run")
    test_count = sum(1 for a in final_rankings if a["verdict"]["verdict_short"] == "test")
    stop_count = sum(1 for a in final_rankings if a["verdict"]["verdict_short"] == "stop")

    print(f"\n📋 SUMMARY: {run_count} ready to run · {test_count} need fixes · {stop_count} don't run")
    print(f"✅ Saved to '{output_file}'. Run python ideator.py next!")