# 🎯 Atomic Ad Analyzer

An AI-powered ad creative analysis tool built for the Atomic Vector mini assignment.

---

## What it does

Given a set of ad creatives (image + copy), the tool:

1. **Extracts** the anatomy of each ad — hook, CTA, visual style, emotional appeal, target audience — using a vision LLM with a structured schema
2. **Scores** each ad on a 5-dimension rubric (10 points total), producing a ranked leaderboard with per-dimension feedback
3. **Ideates** new creative concepts by first detecting what separates winners from losers, then generating test-ready briefs grounded in those patterns

---

## Scoring Rubric (the defensible heuristic)

Each ad is scored out of 10 across 5 dimensions (2 pts each):

| Dimension | What it measures |
|---|---|
| **Hook Strength** | Is it short, specific, and surprising enough to stop a scroll? |
| **CTA Clarity** | Does it use a strong action verb + urgency? |
| **Emotional Punch** | Does it trigger one clear feeling, backed by the copy? |
| **Visual-Copy Fit** | Do the image and text reinforce the same message? |
| **Audience Focus** | Does it speak to a specific person, not everyone? |

---

## Setup

```bash
# 1. Clone and install
pip install groq streamlit pillow python-dotenv pydantic

# 2. Add your API key
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Add your ads
mkdir data
# Put ad images in /data/
# Create /data/ad_copy.json:
# { "ad1.jpg": "10 minutes to your door. Order now.", ... }
```

---

## Running it

**Option A — Streamlit UI (recommended)**
```bash
streamlit run app.py
```
Upload images directly in the browser, no terminal needed.

**Option B — Terminal pipeline**
```bash
python extracter.py   # Step 1: extract structured data
python scorer.py      # Step 2: score and rank
python ideator.py     # Step 3: generate creative ideas

# Or all at once:
python main.py
```

---

## File structure

```
├── extracter.py      # Vision LLM → structured AdBlueprint per ad
├── scorer.py         # 5-dimension rubric → ranked leaderboard
├── ideator.py        # Pattern detection → creative briefs
├── app.py            # Streamlit UI
├── main.py           # Terminal pipeline runner
├── data/
│   ├── ad_copy.json          # Map of { "image.jpg": "copy text" }
│   ├── extracted_ads.json    # Output of extracter.py
│   ├── scored_ads.json       # Output of scorer.py
│   └── new_ideas.txt         # Output of ideator.py
└── .env              # GROQ_API_KEY=...
```

---

## Tradeoffs made

1. **Scoring is heuristic, not data-driven.** Without real CTR/ROAS data, I built a rubric based on direct-response advertising principles (hook specificity, CTA urgency, emotional clarity). It's defensible but would need real conversion data to validate.

2. **Vision model accuracy depends on image quality.** Low-res screenshots from Meta Ad Library can cause the model to miss text overlays. A pre-processing step (OCR before vision) would improve reliability.

3. **Groq free tier has rate limits.** For 15 ads, the pipeline runs sequentially to avoid hitting limits. Parallelizing with a small delay would cut runtime from ~3 min to ~45 sec.

## What I'd do with another week

- Pull real ads automatically from Meta Ad Library API instead of manual screenshots
- Add A/B test tracking: link each ad to actual performance metrics and retrain the scoring rubric against real outcomes
- Build a feedback loop: let the marketing team mark the AI's assessments as right/wrong, so the rubric improves over time
- Add export to a shareable PDF brief so the creative team can act on it without touching the tool