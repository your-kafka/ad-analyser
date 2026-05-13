"""
app.py  ·  The Streamlit Interface  [UPDATED — Color Psychology Edition]
-------------------------------------------------------------------------
Brings together all three steps (Extract → Score → Ideate) into
a single, usable UI.

UPDATE (Color Psychology):
  - Leaderboard now shows color swatches + psychological meaning labels
  - New tab: 🎨 Color Analysis — deep dive into color choices per ad
  - Both powered by color_analyzer.py (Swarnakar, 2024)

Tabs:
  📤 Upload & Analyze  —  upload images and enter copy, run the pipeline
  🏆 Leaderboard       —  ranked ads with score breakdowns + color swatches
  🎨 Color Analysis    —  per-ad color psychology deep dive (NEW)
  🔬 Raw Data          —  full extraction JSON for each ad
  💡 Creative Ideas    —  AI-generated concepts grounded in patterns
"""

import streamlit as st
import json
import os
import tempfile
from PIL import Image
from dotenv import load_dotenv

from extracter import extract_insights_with_ai
from scorer import evaluate_ad, DIMENSIONS
from ideator import generate_new_creative_ideas
from color_analyzer import get_color_insights, score_color_psychology   # ← NEW

load_dotenv()

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Ad Creative Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .score-bar-bg  { background:#e9ecef; border-radius:6px; height:10px; width:100%; margin:4px 0 10px 0; }
    .score-bar-fill{ height:10px; border-radius:6px; transition:width 0.5s ease; }
    .ad-card       { background:#f8f9fa; border:1px solid #dee2e6; border-radius:10px; padding:20px; margin-bottom:20px; }
    .rank-badge    { font-size:2rem; font-weight:800; color:#adb5bd; }
    .rank-badge.gold   { color:#f4a11d; }
    .rank-badge.silver { color:#868e96; }
    .rank-badge.bronze { color:#c56a2d; }
    /* ── Color swatch pill ── */
    .color-pill    { display:inline-block; border-radius:20px; padding:3px 12px;
                     font-size:0.78rem; font-weight:600; margin:2px 3px;
                     border:1px solid rgba(0,0,0,0.12); }
    /* ── Color insight card ── */
    .color-card    { border-radius:10px; padding:16px; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🎯 Ad Analyzer")
    st.caption("Atomic Vector · Creative Intelligence")
    st.divider()
    st.markdown("""
    **How it works:**
    1. 📤 Upload ad images + paste copy
    2. 🤖 AI extracts hook, CTA, style, emotion, **colors**
    3. 📊 Rubric scores each ad on **6 dimensions** (PACT + Color Psychology)
    4. 🎨 Color analysis tab shows palette psychology
    5. 💡 AI generates next creative concepts
    """)
    st.divider()
    st.caption("Model: Llama 4 Scout · Groq API")
    st.caption("Color research: Swarnakar (2024)")


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def color_for_score(score: int, max_score: int = 10) -> str:
    pct = score / max_score
    if pct >= 0.7:   return "#2f9e44"
    elif pct >= 0.4: return "#f59f00"
    else:            return "#e03131"

def rank_badge_class(rank: int) -> str:
    return {1: "gold", 2: "silver", 3: "bronze"}.get(rank, "")

# Approximate hex for each color name (mirrors color_analyzer.py)
COLOR_HEX = {
    "red":    "#e03131", "blue":   "#1971c2", "yellow": "#f59f00",
    "green":  "#2f9e44", "black":  "#212529", "white":  "#e9ecef",
    "orange": "#e8590c", "purple": "#7048e8", "gold":   "#c9a227",
    "pink":   "#e64980", "brown":  "#8B5E3C", "grey":   "#868e96",
}

def render_color_swatches(dominant_colors: list[str]):
    """Renders inline HTML color pills for the leaderboard."""
    pills = ""
    for c in dominant_colors:
        hex_val   = COLOR_HEX.get(c.lower(), "#adb5bd")
        text_col  = "#fff" if c.lower() in ["black", "blue", "purple", "red", "orange", "green"] else "#212529"
        pills += (
            f'<span class="color-pill" style="background:{hex_val}; color:{text_col};">'
            f'{c.upper()}</span>'
        )
    return pills


# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────

tab_upload, tab_leaderboard, tab_color, tab_raw, tab_ideas = st.tabs([
    "📤 Upload & Analyze",
    "🏆 Leaderboard",
    "🎨 Color Analysis",   # ← NEW TAB
    "🔬 Raw Data",
    "💡 Creative Ideas",
])


# ══════════════════════════════════════════════════════════════
# TAB 1  ·  UPLOAD & ANALYZE
# ══════════════════════════════════════════════════════════════

with tab_upload:
    st.header("Upload Ads & Run Analysis")
    st.markdown(
        "Upload your ad images and paste the accompanying copy. "
        "The AI extracts the marketing anatomy of each ad — including dominant colors — "
        "then ranks them across 6 dimensions."
    )

    st.subheader("Option A — Upload Fresh Ads")

    uploaded_images = st.file_uploader(
        "Drop your ad images here (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )

    copy_inputs = {}

    if uploaded_images:
        st.markdown("**Now paste the ad copy for each image:**")
        for img_file in uploaded_images:
            with st.expander(f"✏️ Copy for: {img_file.name}", expanded=True):
                copy_inputs[img_file.name] = st.text_area(
                    "Ad copy text",
                    key=f"copy_{img_file.name}",
                    height=100,
                )

        if st.button("🚀 Analyze These Ads", type="primary", disabled=not uploaded_images):
            os.makedirs("data", exist_ok=True)
            extracted = {}
            scored    = []
            progress  = st.progress(0, text="Starting analysis...")
            total     = len(uploaded_images)

            for i, img_file in enumerate(uploaded_images):
                progress.progress(i / total, text=f"🔍 Extracting from {img_file.name}...")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(img_file.read())
                    tmp_path = tmp.name
                
                try:
                    copy_text = copy_inputs.get(img_file.name, "")
                    
                    # AI Extraction
                    blueprint = extract_insights_with_ai(tmp_path, copy_text)
                    extracted[img_file.name] = blueprint.dict()
                    
                    # Scoring Logic
                    score_result = evaluate_ad(blueprint.dict())
                    
                    scored.append({
                        "image_name":      img_file.name,
                        "final_score":     score_result["total_score"],
                        "raw_score":       score_result.get("raw_score", 0),
                        "score_breakdown": score_result["score_breakdown"],
                        "ad_data":         blueprint.dict(),
                    })
                except Exception as e:
                    # Graceful failure: Warn the user but don't stop the loop
                    st.warning(f"⚠️ Skipping {img_file.name}: The AI couldn't parse this specific ad. (Error: {e})")
                    continue 
                finally:
                    # Clean up the temp file regardless of success or failure
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            # Ensure data is sorted even if some items were skipped

            scored.sort(key=lambda x: x["final_score"], reverse=True)

            with open("data/extracted_ads.json", "w") as f:
                json.dump(extracted, f, indent=4, ensure_ascii=False)
            with open("data/scored_ads.json", "w") as f:
                json.dump(scored, f, indent=4, ensure_ascii=False)
            for img_file in uploaded_images:
                img_file.seek(0)
                with open(os.path.join("data", img_file.name), "wb") as f:
                    f.write(img_file.read())

            progress.progress(1.0, text="✅ Analysis complete!")
            st.success(f"Done! Analyzed {len(scored)} ads. Switch to the 🏆 Leaderboard tab.")
            st.balloons()

    st.divider()
    st.subheader("Option B — Use Pre-loaded /data Folder")
    if st.button("📂 Load from /data folder"):
        if os.path.exists("data/scored_ads.json") and os.path.exists("data/extracted_ads.json"):
            st.success("Found existing analysis data. Check the 🏆 Leaderboard tab!")
        else:
            st.error("No pre-analyzed data found. Run extracter.py and scorer.py first, or use Option A.")


# ══════════════════════════════════════════════════════════════
# TAB 2  ·  LEADERBOARD  (updated with color swatches)
# ══════════════════════════════════════════════════════════════

with tab_leaderboard:
    st.header("Ad Performance Leaderboard")

    if not os.path.exists("data/scored_ads.json"):
        st.info("No results yet. Go to **📤 Upload & Analyze** to run the pipeline first.")
    else:
        with open("data/scored_ads.json") as f:
            scored_ads = json.load(f)

        if not scored_ads:
            st.warning("The scored_ads.json file is empty.")
        else:
            brand = scored_ads[0].get("ad_data", {}).get("brand_name", "")
            if brand:
                st.caption(f"Brand analyzed: **{brand}**  ·  Scoring: PACT framework + Color Psychology (Swarnakar, 2024)")

            for rank, ad in enumerate(scored_ads, 1):
                badge_class = rank_badge_class(rank)
                score       = ad["final_score"]
                bar_color   = color_for_score(score)
                ad_data     = ad.get("ad_data", {})
                dom_colors  = ad_data.get("dominant_colors", [])

                with st.container():
                    st.markdown('<div class="ad-card">', unsafe_allow_html=True)
                    col_rank, col_img, col_info, col_score = st.columns([0.5, 1.5, 3, 2])

                    with col_rank:
                        st.markdown(f'<div class="rank-badge {badge_class}">#{rank}</div>', unsafe_allow_html=True)

                    with col_img:
                        img_path = os.path.join("data", ad["image_name"])
                        if os.path.exists(img_path):
                            st.image(Image.open(img_path), use_container_width=True)
                        else:
                            st.caption(ad["image_name"])

                    with col_info:
                        st.markdown(f"**Hook:** {ad_data.get('hook', '—')}")
                        st.markdown(f"**CTA:** `{ad_data.get('call_to_action', '—')}`")
                        st.markdown(f"**Emotion:** {ad_data.get('emotional_appeal', '—')[:80]}")
                        st.markdown(f"**Audience:** {ad_data.get('target_audience', '—')[:80]}")

                        # ── COLOR SWATCHES (NEW) ──────────────────────────
                        if dom_colors:
                            st.markdown("**Colors:**", unsafe_allow_html=True)
                            st.markdown(render_color_swatches(dom_colors), unsafe_allow_html=True)

                            # Show one-line psychological meaning for the primary color
                            primary = dom_colors[0].lower()
                            from color_analyzer import COLOR_PSYCHOLOGY
                            if primary in COLOR_PSYCHOLOGY:
                                emotions = COLOR_PSYCHOLOGY[primary]["emotions"][:3]
                                st.caption(f"Primary color signal: {', '.join(emotions)}")

                    with col_score:
                        st.markdown(f"<h2 style='color:{bar_color}; margin:0'>{score}/10</h2>", unsafe_allow_html=True)
                        raw = ad.get("raw_score", "—")
                        st.caption(f"Raw: {raw}/12")
                        fill_pct = int(score * 10)
                        st.markdown(f"""
                        <div class="score-bar-bg">
                          <div class="score-bar-fill" style="width:{fill_pct}%; background:{bar_color};"></div>
                        </div>""", unsafe_allow_html=True)

                        verdict = ad.get("verdict", {})
                        if verdict:
                            v_short = verdict.get("verdict_short", "")
                            verdict_colors = {
                                "run":  ("#d3f9d8", "#2f9e44"),
                                "test": ("#fff3bf", "#e67700"),
                                "stop": ("#ffe3e3", "#e03131"),
                            }
                            bg, fg = verdict_colors.get(v_short, ("#f1f3f5", "#495057"))
                            st.markdown(
                                f"<div style='background:{bg}; color:{fg}; border-radius:6px; "
                                f"padding:6px 10px; font-weight:700; font-size:0.9rem; margin:6px 0'>"
                                f"{verdict.get('verdict', '')}</div>", unsafe_allow_html=True
                            )

                        breakdown = ad.get("score_breakdown", {})
                        for dim_name, dim_data in breakdown.items():
                            dim_score = dim_data["score"]
                            dim_max   = dim_data["max"]
                            dim_pct   = int((dim_score / dim_max) * 100)
                            dim_color = color_for_score(dim_score, dim_max)
                            # Highlight color psychology dimension
                            label = f"🎨 {dim_name}" if dim_name == "Color Psychology" else dim_name
                            st.markdown(f"<small style='color:#868e96'>{label}: {dim_score}/{dim_max}</small>", unsafe_allow_html=True)
                            st.markdown(f"""
                            <div class="score-bar-bg">
                              <div class="score-bar-fill" style="width:{dim_pct}%; background:{dim_color};"></div>
                            </div>""", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                    with st.expander(f"📝 Full feedback + fixes for #{rank}"):
                        verdict = ad.get("verdict", {})
                        if verdict:
                            st.markdown(f"**Decision:** {verdict.get('reasoning', '')}")
                            st.markdown(f"**Next action:** {verdict.get('next_action', '')}")
                            st.divider()
                        breakdown = ad.get("score_breakdown", {})
                        for dim_name, dim_data in breakdown.items():
                            icon = "✅" if dim_data["score"] == dim_data["max"] else ("⚠️" if dim_data["score"] > 0 else "❌")
                            st.markdown(f"{icon} **{dim_name}** ({dim_data['score']}/{dim_data['max']}): {dim_data['reason']}")
                            if dim_data["score"] < dim_data["max"] and dim_data.get("fix"):
                                st.markdown(f"   💡 *Fix: {dim_data['fix']}*")


# ══════════════════════════════════════════════════════════════
# TAB 3  ·  COLOR ANALYSIS  (NEW TAB)
# ══════════════════════════════════════════════════════════════

with tab_color:
    st.header("🎨 Color Psychology Analysis")
    st.markdown(
        "Per-ad deep dive into color choices, grounded in peer-reviewed research: "
        "**Swarnakar (2024) — The Role of Color Psychology in Advertisement**"
    )
    st.caption(
        "Key finding: *\"90% of initial product judgments are based solely on color.\"* "
        "— Kumar (2017), cited in Swarnakar (2024)"
    )
    st.divider()

    if not os.path.exists("data/scored_ads.json"):
        st.info("Run the analysis first in **📤 Upload & Analyze**.")
    else:
        with open("data/scored_ads.json") as f:
            scored_ads = json.load(f)

        for rank, ad in enumerate(scored_ads, 1):
            ad_data       = ad.get("ad_data", {})
            dom_colors    = ad_data.get("dominant_colors", [])
            color_count   = ad_data.get("color_count", len(dom_colors))
            color_score   = ad.get("score_breakdown", {}).get("Color Psychology", {})

            with st.expander(
                f"#{rank} {ad['image_name']}  —  "
                f"Color Score: {color_score.get('score', '?')}/2",
                expanded=(rank == 1)
            ):
                col_img, col_details = st.columns([1, 3])

                with col_img:
                    img_path = os.path.join("data", ad["image_name"])
                    if os.path.exists(img_path):
                        st.image(Image.open(img_path), use_container_width=True)

                with col_details:
                    # Color swatch strip
                    st.markdown("**Dominant Colors Detected:**")
                    if dom_colors:
                        st.markdown(render_color_swatches(dom_colors), unsafe_allow_html=True)
                        st.caption(f"Total color count in palette: {color_count}")
                    else:
                        st.warning("No color data — re-run extraction to populate this.")

                    st.divider()

                    # Color Psychology score breakdown
                    st.markdown(f"**Color Psychology Score:** {color_score.get('score', '?')}/2")
                    reason = color_score.get("reason", "")
                    fix    = color_score.get("fix", "")
                    if reason:
                        st.markdown(f"📊 {reason}")
                    if fix and color_score.get("score", 2) < 2:
                        st.info(f"💡 Fix: {fix}")

                    st.divider()

                    # Per-color insight cards
                    if dom_colors:
                        st.markdown("**What Each Color Communicates:**")
                        insights = get_color_insights(dom_colors)
                        for insight in insights:
                            hex_val  = insight["hex"]
                            text_col = "#fff" if insight["color"] in [
                                "black", "blue", "purple", "red", "orange", "green"
                            ] else "#212529"

                            st.markdown(
                                f"<div class='color-card' style='background:{hex_val}22; "
                                f"border-left: 5px solid {hex_val};'>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<span class='color-pill' style='background:{hex_val}; color:{text_col};'>"
                                f"  {insight['color'].upper()}  </span>",
                                unsafe_allow_html=True
                            )
                            st.markdown(f"**Emotions triggered:** {', '.join(insight['emotions'])}")
                            st.markdown(f"**Best used for:** {', '.join(insight['best_for'][:4])}")
                            if insight["avoid_for"]:
                                st.markdown(f"**Avoid for:** {', '.join(insight['avoid_for'][:3])}")
                            st.caption(f"📚 Research: {insight['paper_insight']}")
                            if insight["brand_examples"]:
                                st.caption(f"🏢 Used by: {', '.join(insight['brand_examples'])}")
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown("")   # spacing


# ══════════════════════════════════════════════════════════════
# TAB 4  ·  RAW EXTRACTION DATA
# ══════════════════════════════════════════════════════════════

with tab_raw:
    st.header("Raw AI Extraction Data")
    st.markdown("Structured output from the vision model — what it observed before scoring.")

    if not os.path.exists("data/extracted_ads.json"):
        st.info("No extraction data yet. Run the pipeline in **📤 Upload & Analyze**.")
    else:
        with open("data/extracted_ads.json") as f:
            raw_data = json.load(f)

        for img_name, data in raw_data.items():
            with st.expander(f"🖼️  {img_name}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Brand:** {data.get('brand_name', '—')}")
                    st.markdown(f"**Hook:** {data.get('hook', '—')}")
                    st.markdown(f"**CTA:** {data.get('call_to_action', '—')}")
                    st.markdown(f"**Emotion:** {data.get('emotional_appeal', '—')}")
                    st.markdown(f"**Audience:** {data.get('target_audience', '—')}")
                    # NEW color fields
                    dom = data.get("dominant_colors", [])
                    cnt = data.get("color_count", "—")
                    st.markdown(f"**Dominant Colors:** {dom}")
                    st.markdown(f"**Color Count:** {cnt}")
                with col2:
                    st.markdown(f"**Visual Style:** {data.get('visual_style', '—')}")
                    st.markdown(f"**Image Description:** {data.get('image_description', '—')}")
                    st.markdown(f"**Ad Copy:** {data.get('ad_copy', '—')}")


# ══════════════════════════════════════════════════════════════
# TAB 5  ·  CREATIVE IDEAS
# ══════════════════════════════════════════════════════════════

with tab_ideas:
    st.header("AI-Generated Creative Concepts")
    st.markdown("Concepts grounded in the patterns detected in winning vs. losing ads.")

    if not os.path.exists("data/scored_ads.json"):
        st.info("Run the analysis first so the ideator has data to work from.")
    else:
        if os.path.exists("data/new_ideas.txt"):
            with open("data/new_ideas.txt", "r") as f:
                cached_ideas = f.read()
            st.markdown(cached_ideas)
            st.divider()
            if st.button("🔄 Regenerate Ideas (uses API credits)"):
                with st.spinner("Analyzing patterns and generating new concepts..."):
                    with open("data/scored_ads.json") as f:
                        data = json.load(f)
                    brand = data[0].get("ad_data", {}).get("brand_name", "the brand") if data else "the brand"
                    ideas = generate_new_creative_ideas(brand_name=brand)
                    with open("data/new_ideas.txt", "w") as f:
                        f.write(ideas)
                    st.markdown(ideas)
        else:
            if st.button("💡 Generate Creative Concepts", type="primary"):
                with st.spinner("Detecting patterns, then generating test concepts..."):
                    try:
                        with open("data/scored_ads.json") as f:
                            data = json.load(f)
                        brand = data[0].get("ad_data", {}).get("brand_name", "the brand") if data else "the brand"
                        ideas = generate_new_creative_ideas(brand_name=brand)
                        with open("data/new_ideas.txt", "w") as f:
                            f.write(ideas)
                        st.markdown(ideas)
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")