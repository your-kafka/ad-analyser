"""
color_analyzer.py  ·  Color Psychology Module
------------------------------------------------
A standalone module grounded in peer-reviewed color psychology research:

  Swarnakar, S. (2024). "The Role of Color Psychology in Advertisement —
  Developing Brand Identity and its Impact on the Buying Habits of Consumers."
  Advertising Methods, Research and Practices. Adamas Knowledge City.

  Supporting references from the paper:
    - Kumar (2017): 90% of initial product judgments are based solely on color
    - Broeder & Snijder (2019): Color in online advertising — trust via blue
    - Gorn et al. (1997): Effects of color as an executional cue in advertising
    - Elliot & Maier (2008): Color associations and consumer psychology
    - Dr. Sajid et al. (2021): Color Psychology in Marketing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT THIS MODULE DOES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The research paper identifies three core ways color works in advertising:

  1. EMOTIONAL TRIGGER     — each color evokes a known psychological response
                             (red → urgency/excitement, blue → trust, etc.)

  2. BRAND-COLOR ALIGNMENT — the color must match the brand's desired perception
                             (a finance brand using red instead of blue = mismatch)

  3. CULTURAL/CONTEXTUAL FIT — the color must suit the product category and
                                audience (luxury = gold/black, eco = green, etc.)

This module scores each of those three axes (2 pts each = 6 pts color sub-score),
then normalizes it to 2 pts for use as a 6th dimension in scorer.py.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ──────────────────────────────────────────────────────────────
# COLOR PSYCHOLOGY LOOKUP TABLE
# Sourced directly from the research paper's findings (Section III, V, VIII)
# ──────────────────────────────────────────────────────────────

COLOR_PSYCHOLOGY = {
    "red": {
        "emotions":      ["urgency", "excitement", "passion", "energy", "hunger"],
        "best_for":      ["food", "sales", "fast food", "promotions", "impulse", "ecommerce"],
        "avoid_for":     ["finance", "healthcare", "luxury", "calm"],
        "paper_insight": "Red evokes urgency and excitement; used by McDonald's to stimulate appetite and speed up decisions. (Swarnakar, 2024 — Section III & VIII)",
        "brand_examples": ["Coca-Cola", "McDonald's", "Zomato", "Amul"],
    },
    "blue": {
        "emotions":      ["trust", "reliability", "calm", "security", "professionalism"],
        "best_for":      ["finance", "technology", "healthcare", "b2b", "banking"],
        "avoid_for":     ["food", "impulse", "fun", "children"],
        "paper_insight": "Blue emanates tranquility, trust, and dependability — favored by financial and tech brands. (Swarnakar, 2024 — Introduction; Broeder & Snijder, 2019)",
        "brand_examples": ["Pepsi", "Facebook", "PayPal", "HDFC"],
    },
    "yellow": {
        "emotions":      ["optimism", "warmth", "attention", "happiness", "cheerfulness"],
        "best_for":      ["children", "food", "retail", "attention-grabbing", "deals"],
        "avoid_for":     ["luxury", "premium", "serious brands"],
        "paper_insight": "Yellow conveys happiness and draws attention; Fevicol uses it for reliability and positivity. Excessive use causes anxiety. (Swarnakar, 2024 — Section III)",
        "brand_examples": ["McDonald's", "Fevicol", "Snapchat", "IKEA"],
    },
    "green": {
        "emotions":      ["nature", "health", "calm", "sustainability", "harmony", "balance"],
        "best_for":      ["health", "wellness", "organic", "eco", "environment", "pharma"],
        "avoid_for":     ["luxury", "tech", "urgency"],
        "paper_insight": "Green is strongly linked with nature, eco-friendliness, and wellness. Used by brands in health and sustainability sectors. (Swarnakar, 2024 — Section III)",
        "brand_examples": ["Whole Foods", "Starbucks", "Patanjali", "John Deere"],
    },
    "black": {
        "emotions":      ["elegance", "power", "sophistication", "authority", "premium"],
        "best_for":      ["luxury", "fashion", "high-end", "premium", "technology"],
        "avoid_for":     ["children", "food", "eco", "healthcare"],
        "paper_insight": "Black signals elegance, power, and exclusivity — dominant in fashion and luxury sectors. Overuse risks heaviness/negativity. (Swarnakar, 2024 — Section III)",
        "brand_examples": ["Apple", "Nike", "Chanel", "Titan"],
    },
    "white": {
        "emotions":      ["simplicity", "cleanliness", "minimalism", "purity", "sophistication"],
        "best_for":      ["tech", "healthcare", "minimalist brands", "premium"],
        "avoid_for":     ["bold", "excitement", "impulse"],
        "paper_insight": "White evokes simplicity and elegance — Apple's white-dominant campaigns position it as the benchmark for tech sophistication. (Swarnakar, 2024 — Section VIII)",
        "brand_examples": ["Apple", "Tesla", "Dove"],
    },
    "orange": {
        "emotions":      ["energy", "vibrancy", "enthusiasm", "warmth", "friendliness"],
        "best_for":      ["sports", "food", "children", "retail", "call-to-action"],
        "avoid_for":     ["luxury", "finance", "serious"],
        "paper_insight": "Orange radiates energy and vibrancy, ideal for action-oriented products. FedEx pairs it with purple for speed and trust. (Swarnakar, 2024 — Section IV & VIII)",
        "brand_examples": ["FedEx", "Amazon", "Swiggy", "Fanta"],
    },
    "purple": {
        "emotions":      ["luxury", "creativity", "mystery", "indulgence", "celebration"],
        "best_for":      ["luxury", "confectionery", "beauty", "premium", "creative"],
        "avoid_for":     ["budget", "food staples", "industrial"],
        "paper_insight": "Purple evokes joy and indulgence — Cadbury's purple packaging is a masterclass in creating visual association with celebration. (Swarnakar, 2024 — Section VIII)",
        "brand_examples": ["Cadbury", "FedEx", "Hallmark"],
    },
    "gold": {
        "emotions":      ["luxury", "prestige", "exclusivity", "success", "elegance"],
        "best_for":      ["luxury", "premium", "fashion", "jewelry", "watches"],
        "avoid_for":     ["budget", "eco", "casual"],
        "paper_insight": "Gold tones represent luxury and exclusivity — Titan leverages gold to establish premium positioning in the Indian watch market. (Swarnakar, 2024 — Section VIII)",
        "brand_examples": ["Titan", "Rolex", "Tanishq"],
    },
    "pink": {
        "emotions":      ["femininity", "warmth", "playfulness", "romance", "care"],
        "best_for":      ["beauty", "fashion", "children", "health", "romance"],
        "avoid_for":     ["industrial", "b2b", "serious"],
        "paper_insight": "Pink carries associations of warmth and playfulness; frequently used in beauty and lifestyle advertising. (Swarnakar, 2024 — Section VII)",
        "brand_examples": ["Barbie", "Victoria's Secret", "T-Mobile"],
    },
}

# ──────────────────────────────────────────────────────────────
# CATEGORY → EXPECTED COLOR MAPPING
# Based on the paper's Section VIII case studies and industry examples
# ──────────────────────────────────────────────────────────────

CATEGORY_COLOR_MAP = {
    "food":       ["red", "yellow", "orange"],
    "finance":    ["blue", "green", "black"],
    "technology": ["blue", "white", "black", "silver"],
    "luxury":     ["black", "gold", "purple", "white"],
    "health":     ["green", "blue", "white"],
    "eco":        ["green", "white"],
    "children":   ["yellow", "orange", "pink", "red"],
    "fashion":    ["black", "white", "gold"],
    "delivery":   ["red", "orange", "blue"],
    "grocery":    ["green", "red", "orange"],
    "sports":     ["red", "orange", "black"],
    "beauty":     ["pink", "purple", "gold"],
    "ecommerce":  ["orange", "blue", "red"],
}


# ──────────────────────────────────────────────────────────────
# AXIS 1: EMOTIONAL TRIGGER SCORE
# Does the dominant color match the ad's intended emotional appeal?
# Paper basis: "90% of initial product judgments based solely on color" (Kumar, 2017)
# ──────────────────────────────────────────────────────────────

def score_color_emotion_match(dominant_colors: list[str], emotional_appeal: str) -> tuple[int, str, str]:
    """
    Checks whether the detected dominant colors trigger emotions that
    align with the ad's intended emotional appeal.

    2 pts → Strong match between color emotions and ad's emotional direction
    1 pt  → Partial match — some alignment but not dominant
    0 pts → Mismatch — the colors contradict the emotional goal
    """
    emotional_appeal_lower = emotional_appeal.lower()

    EMOTION_TO_COLORS = {
        "urgency":      ["red", "orange"],
        "trust":        ["blue", "green", "white"],
        "excitement":   ["red", "orange", "yellow"],
        "convenience":  ["blue", "orange", "green"],
        "fomo":         ["red", "orange"],
        "aspiration":   ["gold", "black", "purple", "white"],
        "humor":        ["yellow", "orange", "pink"],
        "price shock":  ["red", "yellow", "orange"],
        "social proof": ["blue", "green"],
        "curiosity":    ["purple", "orange", "black"],
        "luxury":       ["gold", "black", "purple", "white"],
        "health":       ["green", "blue", "white"],
        "happiness":    ["yellow", "orange", "red"],
        "calm":         ["blue", "green", "white"],
        "eco":          ["green", "white"],
        "nature":       ["green", "brown"],
    }

    matched_emotions = []
    for emotion_key, ideal_colors in EMOTION_TO_COLORS.items():
        if emotion_key in emotional_appeal_lower:
            matched_emotions.extend(ideal_colors)

    if not matched_emotions:
        # Can't evaluate without a known emotion — give partial credit
        return (
            1,
            "Emotional direction is unclear, so color-emotion alignment can't be fully evaluated.",
            "Define a clearer emotional goal (trust, urgency, aspiration, etc.) so color choices can serve it."
        )

    hits = sum(1 for c in dominant_colors if c in matched_emotions)

    if hits >= 2:
        return (
            2,
            f"Color palette strongly supports the emotional goal — {', '.join(dominant_colors)} aligns with '{emotional_appeal[:40]}'.",
            "Great alignment. Run A/B test with a complementary color to confirm this palette's edge."
        )
    elif hits == 1:
        return (
            1,
            f"Partial color-emotion alignment — one dominant color supports the emotion, others don't.",
            "Increase the weight of the aligned color. Remove or reduce colors that dilute the emotional signal."
        )
    else:
        return (
            0,
            f"Color-emotion mismatch — the dominant colors contradict the ad's emotional intent.",
            "Either change the color palette to match the emotion, or rethink the emotional angle to fit the colors."
        )


# ──────────────────────────────────────────────────────────────
# AXIS 2: BRAND-COLOR ALIGNMENT SCORE
# Do the colors fit what research says works for this industry/product?
# Paper basis: Sections V and VIII — brand identity through consistent color
# ──────────────────────────────────────────────────────────────

def score_brand_color_fit(dominant_colors: list[str], ad_copy: str, brand_name: str) -> tuple[int, str, str]:
    """
    Checks if the color palette is appropriate for the detected product category.

    Uses the ad copy to infer product category (food, finance, eco, luxury, etc.),
    then cross-references the paper's recommended colors for that category.

    2 pts → Colors are ideal for this category (research-backed match)
    1 pt  → Acceptable but not optimal
    0 pts → Colors actively work against the category's needs
    """
    copy_lower = (ad_copy + " " + brand_name).lower()

    # Detect category from copy keywords
    CATEGORY_KEYWORDS = {
        "food":       ["food", "eat", "taste", "hungry", "meal", "restaurant", "kitchen", "cook", "chef", "dish"],
        "delivery":   ["deliver", "minutes", "doorstep", "order", "shipped", "arrive", "quick commerce"],
        "grocery":    ["grocery", "vegetable", "fruit", "fresh", "organic", "supermarket", "kirana"],
        "finance":    ["bank", "loan", "invest", "finance", "money", "savings", "insurance", "fund"],
        "technology": ["app", "tech", "software", "digital", "device", "phone", "platform", "ai"],
        "health":     ["health", "wellness", "doctor", "medicine", "pharma", "fitness", "gym", "nutrition"],
        "luxury":     ["luxury", "premium", "exclusive", "elite", "finest", "crafted", "bespoke", "premium"],
        "fashion":    ["fashion", "style", "wear", "clothing", "outfit", "brand", "design", "collection"],
        "eco":        ["eco", "sustainable", "green", "organic", "environment", "natural", "planet", "recycle"],
        "children":   ["kids", "children", "child", "baby", "toy", "school", "learn", "play"],
        "beauty":     ["beauty", "skin", "cream", "cosmetic", "makeup", "glow", "hair", "care"],
        "sports":     ["sport", "fitness", "run", "gym", "train", "athlete", "energy", "performance"],
        "ecommerce":  ["shop", "buy", "deal", "sale", "offer", "discount", "order", "cart", "purchase"],
    }

    detected_category = None
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in copy_lower for kw in keywords):
            detected_category = category
            break

    if not detected_category:
        return (
            1,
            "Product category unclear from copy — can't fully evaluate brand-color fit.",
            "Make the product category clearer in the copy so color choices can be evaluated against industry norms."
        )

    ideal_colors = CATEGORY_COLOR_MAP.get(detected_category, [])
    hits = sum(1 for c in dominant_colors if c in ideal_colors)

    # Check for actively wrong colors
    BAD_COMBOS = {
        "food":    ["blue", "purple"],        # Blue suppresses appetite (paper: Section III)
        "finance": ["red", "orange"],         # Red = risk, not trust (paper: Section III)
        "luxury":  ["yellow", "orange"],      # Too casual for luxury (paper: Section V)
        "eco":     ["black", "red"],           # Contradicts nature/sustainability signal
        "health":  ["red", "black"],           # Evokes danger vs. calm/trust
    }
    bad_hits = sum(1 for c in dominant_colors if c in BAD_COMBOS.get(detected_category, []))

    if hits >= 2 and bad_hits == 0:
        return (
            2,
            f"Color palette is well-matched for a {detected_category} ad — {', '.join(dominant_colors)} aligns with industry research.",
            "Good brand-color fit. Keep the palette consistent across all touchpoints for stronger brand recall. (Swarnakar, 2024)"
        )
    elif bad_hits >= 1:
        return (
            0,
            f"Color palette contains colors that research links to poor performance in {detected_category} advertising.",
            f"For {detected_category}, prioritize: {', '.join(ideal_colors)}. The current palette may undermine trust or appetite."
        )
    else:
        return (
            1,
            f"Color palette is acceptable for {detected_category} but not optimized for maximum impact.",
            f"Shift toward: {', '.join(ideal_colors[:3])} — the research-backed palette for {detected_category} ads."
        )


# ──────────────────────────────────────────────────────────────
# AXIS 3: COLOR CONSISTENCY SCORE
# Is the palette focused (1-2 dominant colors) or scattered?
# Paper basis: Section V — "Consistent use of color across touchpoints builds brand recognition"
# ──────────────────────────────────────────────────────────────

def score_color_consistency(dominant_colors: list[str], color_count: int) -> tuple[int, str, str]:
    """
    Research finding (Swarnakar, 2024 — Section V):
    "Consistent and strategic use of color across marketing materials builds
    brand recognition and fosters a powerful emotional connection."

    Too many colors = diluted message = weak memory encoding.
    1-2 strong colors = clear signal = better brand recall.

    2 pts → 1-2 dominant colors (focused, memorable)
    1 pt  → 3 colors (acceptable, slightly busy)
    0 pts → 4+ colors (scattered, cognitively overloading)
    """
    if color_count <= 2:
        return (
            2,
            f"Focused palette ({color_count} colors: {', '.join(dominant_colors)}) — clean and memorable.",
            "Excellent. Maintain this palette consistently across all ad touchpoints. (Swarnakar, 2024 — Section V)"
        )
    elif color_count == 3:
        return (
            1,
            f"Three-color palette — slightly busy but workable. Risk of diluting the primary color's emotional signal.",
            "Consider reducing to 2 colors. Pick the one that best serves the emotional goal and let it dominate."
        )
    else:
        return (
            0,
            f"Too many colors ({color_count}) — the palette is scattered and cognitively overwhelming.",
            "Rebuild with a maximum of 2 dominant colors. Every additional color halves the impact of the primary one."
        )


# ──────────────────────────────────────────────────────────────
# MASTER COLOR SCORER  ·  Combines all 3 axes → normalizes to 2 pts
# ──────────────────────────────────────────────────────────────

def score_color_psychology(ad: dict) -> tuple[int, str, str]:
    """
    The main function called by scorer.py as the 6th scoring dimension.

    Runs all 3 color axes (emotion match, brand fit, consistency),
    scores each 0-2, sums to a 0-6 sub-score, then normalizes to 0-2
    (so it slots neatly into the existing 10-point scoring system).

    Returns: (normalized_score: int, reason: str, fix: str)
    """
    # Pull data from the ad blueprint
    dominant_colors = [c.lower().strip() for c in ad.get("dominant_colors", [])]
    color_count     = ad.get("color_count", len(dominant_colors))
    emotional_appeal = ad.get("emotional_appeal", "")
    ad_copy          = ad.get("ad_copy", "")
    brand_name       = ad.get("brand_name", "")

    if not dominant_colors:
        return (
            0,
            "No color data found — can't evaluate color psychology.",
            "Run color extraction first (update extracter.py to identify dominant colors)."
        )

    # Score all 3 axes
    emotion_score,     emotion_reason,     emotion_fix     = score_color_emotion_match(dominant_colors, emotional_appeal)
    brand_fit_score,   brand_fit_reason,   brand_fit_fix   = score_brand_color_fit(dominant_colors, ad_copy, brand_name)
    consistency_score, consistency_reason, consistency_fix = score_color_consistency(dominant_colors, color_count)

    raw_total = emotion_score + brand_fit_score + consistency_score  # 0–6

    # Normalize to 0-2 scale (matching scorer.py's per-dimension scoring)
    # 0-2 raw → 0, 3-4 raw → 1, 5-6 raw → 2
    if raw_total >= 5:
        normalized = 2
    elif raw_total >= 3:
        normalized = 1
    else:
        normalized = 0

    # Build a summary reason and fix from the weakest axis
    all_results = [
        ("Emotion Match",    emotion_score,     emotion_reason,     emotion_fix),
        ("Brand-Color Fit",  brand_fit_score,   brand_fit_reason,   brand_fit_fix),
        ("Color Consistency",consistency_score, consistency_reason, consistency_fix),
    ]

    # Find the weakest axis to surface as the actionable fix
    weakest = min(all_results, key=lambda x: x[1])

    combined_reason = (
        f"Color sub-scores — "
        f"Emotion Match: {emotion_score}/2 | "
        f"Brand Fit: {brand_fit_score}/2 | "
        f"Consistency: {consistency_score}/2. "
        f"Weakest: {weakest[0]}. {weakest[2]}"
    )
    combined_fix = weakest[3]

    return (normalized, combined_reason, combined_fix)


# ──────────────────────────────────────────────────────────────
# COLOR INSIGHTS GENERATOR  ·  For app.py's Color Analysis tab
# ──────────────────────────────────────────────────────────────

def get_color_insights(dominant_colors: list[str]) -> list[dict]:
    """
    Returns a list of rich color insight cards for each detected color.
    Used by app.py to render the 🎨 Color Analysis tab.

    Each card contains:
        color        : the color name
        emotions     : list of emotions it evokes
        best_for     : industries/contexts where it excels
        paper_insight: direct reference to the research paper finding
        hex_preview  : approximate hex for UI color swatch
    """
    HEX_MAP = {
        "red":    "#e03131",
        "blue":   "#1971c2",
        "yellow": "#f59f00",
        "green":  "#2f9e44",
        "black":  "#212529",
        "white":  "#f8f9fa",
        "orange": "#e8590c",
        "purple": "#7048e8",
        "gold":   "#c9a227",
        "pink":   "#e64980",
    }

    insights = []
    for color in dominant_colors:
        color_lower = color.lower().strip()
        data = COLOR_PSYCHOLOGY.get(color_lower)
        if data:
            insights.append({
                "color":         color_lower,
                "hex":           HEX_MAP.get(color_lower, "#adb5bd"),
                "emotions":      data["emotions"],
                "best_for":      data["best_for"],
                "avoid_for":     data["avoid_for"],
                "paper_insight": data["paper_insight"],
                "brand_examples": data["brand_examples"],
            })
        else:
            insights.append({
                "color":         color_lower,
                "hex":           "#adb5bd",
                "emotions":      ["Unknown — not in color psychology database"],
                "best_for":      ["Various"],
                "avoid_for":     [],
                "paper_insight": "Not covered in current research database.",
                "brand_examples": [],
            })
    return insights


# ──────────────────────────────────────────────────────────────
# STANDALONE TEST RUNNER
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick smoke test
    test_ad = {
        "brand_name":      "Instamart",
        "dominant_colors": ["red", "orange"],
        "color_count":     2,
        "emotional_appeal": "Convenience and urgency — get groceries in 10 minutes",
        "ad_copy":         "10 minutes to your door. Order groceries now.",
    }

    print("🎨 COLOR PSYCHOLOGY ANALYZER — Test Run")
    print("=" * 55)

    score, reason, fix = score_color_psychology(test_ad)
    print(f"Overall Color Score (normalized): {score}/2")
    print(f"Reason: {reason}")
    print(f"Fix:    {fix}")

    print("\n📚 Color Insights:")
    insights = get_color_insights(test_ad["dominant_colors"])
    for insight in insights:
        print(f"\n  [{insight['color'].upper()}] {insight['hex']}")
        print(f"  Emotions  : {', '.join(insight['emotions'])}")
        print(f"  Best for  : {', '.join(insight['best_for'])}")
        print(f"  Research  : {insight['paper_insight']}")