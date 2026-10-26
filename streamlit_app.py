"""
FoodVerse AI — Multimodal Food Intelligence Platform
Streamlit Community Cloud Application
"""

import os
import sys
import io
import time
import asyncio
from typing import Dict, Any, List, Optional
from PIL import Image

# Ensure backend modules can be imported directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Populate environment variables from Streamlit secrets if present
if hasattr(st, "secrets"):
    for key in ["GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "USDA_API_KEY", "LLM_PROVIDER", "SECRET_KEY"]:
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = str(st.secrets[key]).strip()

# Import real backend services
from app.services.ai.provider_factory import get_ai_provider, get_provider_status
from app.services.nutrition.calculator import NutritionCalculator
from app.services.nutrition.usda_data import VERIFIED_FOOD_DATABASE, find_matching_food_data
from app.services.hygiene.video_processor import VideoProcessor

# -------------------------------------------------------------
# Page Configuration & Styling
# -------------------------------------------------------------
st.set_page_config(
    page_title="FoodVerse AI — Multimodal Food Intelligence",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Brand Styling (FoodVerse Emerald Theme)
st.markdown("""
<style>
    /* Global styles */
    .main {
        background-color: #FAFAF9;
    }
    
    /* Header container */
    .brand-header {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 50%, #047857 100%);
        color: white;
        padding: 24px 32px;
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(6, 78, 59, 0.25);
    }
    .brand-header h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .brand-header p {
        color: #A7F3D0 !important;
        font-size: 1rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .metric-card .label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #6B7280;
        letter-spacing: 0.5px;
    }
    .metric-card .val {
        font-size: 1.5rem;
        font-weight: 800;
        color: #111827;
        margin-top: 4px;
    }
    
    /* Food info box */
    .food-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Disclaimer pill */
    .disclaimer-box {
        background-color: #FEF3C7;
        border-left: 4px solid #D97706;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #92400E;
        margin-top: 14px;
    }
    
    /* Provenance pill */
    .provenance-box {
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 0.8rem;
        color: #065F46;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# Helper Utilities
# -------------------------------------------------------------
def run_async(coro):
    """Safely runs an async coroutine inside Streamlit synchronous context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        # Inside existing running loop (e.g. some Streamlit runtimes)
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    return loop.run_until_complete(coro)


def create_macro_donut_chart(protein_g: float, carbs_g: float, fat_g: float, total_calories: float):
    """Generates an interactive Plotly donut chart matching FoodVerse design."""
    protein_cals = protein_g * 4.0
    carbs_cals = carbs_g * 4.0
    fat_cals = fat_g * 9.0

    labels = ["Protein", "Carbohydrates", "Fats"]
    values = [protein_cals, carbs_cals, fat_cals]
    colors = ["#10B981", "#F59E0B", "#EF4444"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.68,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent",
        textfont=dict(size=13, color="#1F2937", family="sans-serif"),
        hoverinfo="label+value+percent",
        direction="clockwise"
    )])

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=10, b=30, l=10, r=10),
        height=260,
        annotations=[dict(
            text=f"<b>{int(total_calories)}</b><br><span style='font-size:11px;color:#6B7280;'>KCAL</span>",
            x=0.5, y=0.5,
            font=dict(size=20, color="#111827", family="sans-serif"),
            showarrow=False
        )]
    )
    return fig


# -------------------------------------------------------------
# Sidebar: Navigation & System Status
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=400&auto=format&fit=crop&q=80", use_container_width=True)
    st.title("🥑 FoodVerse AI")
    st.caption("Multimodal Food Intelligence Agent")

    nav_choice = st.radio(
        "Select Capability:",
        [
            "📸 Food Scanner & Nutrition",
            "🥗 Freshness & Spoilage Check",
            "📹 Kitchen Hygiene Video Audit",
            "🍳 Smart Cooking Assistant",
            "📅 Personalized Meal Planner",
            "💬 Multimodal AI Assistant",
            "🔬 Verified Lab Database"
        ],
        index=0
    )

    st.markdown("---")
    
    # Live Status Indicator
    status = get_provider_status()
    st.markdown("### 🟢 System Status")
    
    if status["groq_configured"]:
        st.success("**AI Engine:** Groq Cloud Active (`qwen/qwen3.8-27b`)")
    elif status["gemini_configured"]:
        st.info("**AI Engine:** Google Gemini Active")
    elif status["openai_configured"]:
        st.info("**AI Engine:** OpenAI Active")
    else:
        st.warning("**AI Engine:** Manual Verification Mode (No Live AI Key)")

    st.caption(f"**Laboratory Reference Data:**\nActive ({len(VERIFIED_FOOD_DATABASE)} Verified USDA & ICMR Items)")
    st.caption("Version 1.0.0 • Streamlit Cloud Edition")


# -------------------------------------------------------------
# Module 1: Food Scanner & Precision Nutrition Analysis
# -------------------------------------------------------------
if nav_choice == "📸 Food Scanner & Nutrition":
    st.markdown("""
    <div class="brand-header">
        <h1>📸 Food Scanner & Precision Nutrition Analysis</h1>
        <p>Scan food dishes with multimodal vision, detect ingredients, and calculate verified USDA laboratory nutrition scaled in grams.</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 6], gap="large")

    with col_left:
        st.subheader("1. Food Photo Ingestion")
        input_method = st.radio("Input method:", ["Upload Image File", "Use Web Camera", "Select from Verified Database"], horizontal=True)
        
        image_bytes = None
        selected_db_dish = None

        if input_method == "Upload Image File":
            uploaded_file = st.file_uploader("Upload meal image (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
            if uploaded_file:
                image_bytes = uploaded_file.getvalue()
                st.image(image_bytes, caption="Uploaded Food Image", use_container_width=True)

        elif input_method == "Use Web Camera":
            camera_file = st.camera_input("Capture food photo directly")
            if camera_file:
                image_bytes = camera_file.getvalue()

        else:
            dish_names = [data["canonical_name"] for data in VERIFIED_FOOD_DATABASE.values()]
            selected_db_dish = st.selectbox("Choose a benchmark dish:", sorted(dish_names))
            st.info(f"Selected benchmark: **{selected_db_dish}**")

        st.markdown("---")
        st.subheader("2. Analyze Food")
        analyze_btn = st.button("🔍 Run Multimodal Food Analysis", type="primary", use_container_width=True)

    with col_right:
        st.subheader("3. Nutrition & Composition Breakdown")
        
        if analyze_btn:
            if not image_bytes and not selected_db_dish:
                st.error("Please upload an image, capture a photo, or select a dish first.")
            else:
                with st.spinner("Analyzing food with multimodal vision and calculating USDA lab nutrition..."):
                    ai_provider = get_ai_provider()
                    
                    if image_bytes:
                        try:
                            vision_res = run_async(ai_provider.analyze_food_image(image_bytes, "image/jpeg"))
                            st.session_state["scanner_result"] = vision_res
                            st.session_state["scanner_dish"] = vision_res.primary_food
                            st.session_state["scanner_portion"] = vision_res.estimated_portion_g
                            st.session_state["scanner_notes"] = vision_res.notes
                            st.session_state["scanner_components"] = [d.name for d in vision_res.detected_foods]
                        except Exception as e:
                            st.error(f"Vision analysis error: {e}")
                    else:
                        st.session_state["scanner_dish"] = selected_db_dish
                        st.session_state["scanner_portion"] = 250.0
                        st.session_state["scanner_notes"] = "Selected from verified laboratory benchmark database."
                        st.session_state["scanner_components"] = []

        # Display analysis results if available
        if "scanner_dish" in st.session_state:
            dish_name = st.session_state["scanner_dish"]
            components = st.session_state.get("scanner_components", [])
            
            # Interactive Portion Slider
            current_portion = st.slider(
                "⚖️ Adjust Portion Weight (Grams):",
                min_value=25,
                max_value=1000,
                value=int(st.session_state.get("scanner_portion", 250)),
                step=25
            )

            # Deterministic USDA laboratory calculation
            nutrition = NutritionCalculator.calculate_scaled_nutrition(
                food_name=dish_name,
                serving_size_g=float(current_portion),
                serving_unit="grams"
            )

            # Dish Header Card
            st.markdown(f"""
            <div class="food-card">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <div>
                        <h2 style="margin: 0; color: #111827; font-size: 1.6rem;">{dish_name}</h2>
                        <p style="margin-top: 4px; color: #6B7280; font-size: 0.85rem;">Reference Item: {nutrition['food_name']} • Category: {nutrition.get('category', 'Prepared Entree')}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.8rem; font-weight: 800; color: #047857;">{int(nutrition['calories'])}</span>
                        <span style="font-size: 0.85rem; color: #6B7280; display: block;">KCAL ({current_portion}g)</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Macro Metrics Row
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.markdown(f"""<div class="metric-card"><div class="label">Calories</div><div class="val">{int(nutrition['calories'])}</div></div>""", unsafe_allow_html=True)
            with m_col2:
                st.markdown(f"""<div class="metric-card"><div class="label" style="color:#059669;">Protein</div><div class="val">{nutrition['protein_g']}g</div></div>""", unsafe_allow_html=True)
            with m_col3:
                st.markdown(f"""<div class="metric-card"><div class="label" style="color:#D97706;">Carbs</div><div class="val">{nutrition['carbs_g']}g</div></div>""", unsafe_allow_html=True)
            with m_col4:
                st.markdown(f"""<div class="metric-card"><div class="label" style="color:#DC2626;">Fats</div><div class="val">{nutrition['fat_g']}g</div></div>""", unsafe_allow_html=True)

            st.write("")
            
            # Interactive Donut Chart
            chart = create_macro_donut_chart(
                nutrition['protein_g'],
                nutrition['carbs_g'],
                nutrition['fat_g'],
                nutrition['calories']
            )
            st.plotly_chart(chart, use_container_width=True)

            # Micronutrients & Additional Nutrients
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                st.write(f"🌾 **Dietary Fiber:** `{nutrition.get('fiber_g', 0)}g`")
            with sub_col2:
                st.write(f"🍯 **Sugars:** `{nutrition.get('sugar_g', 0)}g`")
            with sub_col3:
                st.write(f"🧂 **Sodium:** `{nutrition.get('sodium_mg', 0)}mg`")

            # Micronutrients if present
            micros = nutrition.get("micronutrients", {})
            if micros:
                st.markdown("**✨ Key Micronutrients & Minerals:**")
                micro_text = " • ".join([f"**{k.replace('_', ' ').upper()}:** {v}" for k, v in micros.items()])
                st.caption(micro_text)

            # Detected Ingredients
            if components:
                st.markdown("**🥗 Recognized Food Components:**")
                st.info(" • ".join(components))

            # Provenance Note
            st.markdown(f"""
            <div class="provenance-box">
                <b>Source Provenance:</b> {nutrition['data_source']}<br>
                <b>Observation Note:</b> {st.session_state.get('scanner_notes', 'Visual and nutritional evaluation complete.')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Upload a food photo or select a verified dish on the left, then click 'Run Multimodal Food Analysis' to see nutritional insights.")


# -------------------------------------------------------------
# Module 2: Food Freshness & Spoilage Assessor
# -------------------------------------------------------------
elif nav_choice == "🥗 Freshness & Spoilage Check":
    st.markdown("""
    <div class="brand-header">
        <h1>🥗 Food Freshness & Visible Spoilage Assessor</h1>
        <p>Evidence-based visual inspection of surface defects, fungal mycelium, wilting, and slime across perishables.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5, 6], gap="large")

    with col1:
        st.subheader("1. Perishable Item Details")
        category = st.selectbox(
            "Select Food Category:",
            [
                "Fresh Produce (Fruits & Vegetables)",
                "Meat & Poultry (Raw / Cooked)",
                "Fish & Seafood",
                "Dairy & Cheeses",
                "Bakery & Grains",
                "Prepared Dishes & Leftovers"
            ]
        )

        fresh_file = st.file_uploader("Upload close-up photo of surface / edges", type=["jpg", "jpeg", "png", "webp"], key="freshness_upload")
        freshness_bytes = None
        if fresh_file:
            freshness_bytes = fresh_file.getvalue()
            st.image(freshness_bytes, caption="Uploaded Surface Photo", use_container_width=True)

        check_btn = st.button("🔬 Assess Visual Freshness", type="primary", use_container_width=True)

    with col2:
        st.subheader("2. Quality & Spoilage Observations")
        if check_btn:
            if not freshness_bytes:
                st.error("Please upload a photo of the food item to assess.")
            else:
                with st.spinner("Analyzing visual surface cues with Groq vision..."):
                    ai_provider = get_ai_provider()
                    try:
                        fresh_res = run_async(ai_provider.analyze_freshness(freshness_bytes, "image/jpeg", category))
                        
                        # Category Badge
                        if "No obvious" in fresh_res.assessment_category:
                            st.success(f"### Result: {fresh_res.assessment_category}")
                        elif "Visible quality concerns" in fresh_res.assessment_category:
                            st.warning(f"### Result: {fresh_res.assessment_category}")
                        else:
                            st.error(f"### Result: {fresh_res.assessment_category}")

                        if fresh_res.confidence:
                            st.caption(f"**Confidence:** {int(fresh_res.confidence * 100)}% • **Engine:** {fresh_res.provider_used}")

                        st.markdown("#### 🔍 Visual Observations:")
                        for obs in fresh_res.visual_observations:
                            st.markdown(f"- {obs}")

                        st.markdown("#### 💡 Actionable Storage & Handling Guidance:")
                        for rec in fresh_res.recommendations:
                            st.markdown(f"- {rec}")

                        st.markdown(f"""
                        <div class="disclaimer-box">
                            <b>CRITICAL SCIENTIFIC SAFETY DIRECTIVE:</b><br>
                            {fresh_res.safety_disclaimer}
                        </div>
                        """, unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Freshness check error: {e}")
        else:
            st.info("Upload an image of produce, dairy, or meats to evaluate surface freshness indicators.")


# -------------------------------------------------------------
# Module 3: Restaurant & Kitchen Hygiene Video Audit
# -------------------------------------------------------------
elif nav_choice == "📹 Kitchen Hygiene Video Audit":
    st.markdown("""
    <div class="brand-header">
        <h1>📹 Kitchen Hygiene Video Audit</h1>
        <p>OpenCV keyframe extraction and neural inspection of glove protocols, hair restraints, and food contact sanitation.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5, 6], gap="large")

    with col1:
        st.subheader("1. Video Feed Ingestion")
        video_file = st.file_uploader("Upload commercial kitchen video clip (MP4, MOV, WEBM - Max 50 MB)", type=["mp4", "mov", "webm"])
        sample_interval = st.slider("Keyframe sampling interval (seconds):", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

        if video_file:
            st.video(video_file)

        audit_btn = st.button("🛡️ Audit Keyframes for Hygiene Compliance", type="primary", use_container_width=True)

    with col2:
        st.subheader("2. Compliance Findings & Audit Gallery")
        if audit_btn:
            if not video_file:
                st.error("Please upload a video clip to begin the audit.")
            else:
                with st.spinner("Extracting keyframes via OpenCV and executing hygiene inspection..."):
                    try:
                        # Save temp video file
                        temp_video_path = os.path.join(CURRENT_DIR, "temp_hygiene_video.mp4")
                        with open(temp_video_path, "wb") as f:
                            f.write(video_file.getvalue())

                        # Run OpenCV Keyframe Extractor
                        frames_data = VideoProcessor.extract_keyframes(
                            video_path=temp_video_path,
                            interval_seconds=sample_interval,
                            max_frames=6
                        )

                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)

                        if not frames_data:
                            st.warning("Could not extract frames from video. Please ensure valid MP4/WEBM format.")
                        else:
                            st.success(f"Extracted and audited {len(frames_data)} keyframes.")
                            
                            ai_provider = get_ai_provider()
                            hygiene_res = run_async(ai_provider.analyze_hygiene_frames(frames_data))

                            # Risk Overview
                            st.markdown(f"### Overall Risk Rating: **{hygiene_res.overall_risk_level}**")
                            st.write(hygiene_res.overall_summary)

                            st.markdown("#### 📸 Sampled Frame Gallery & Timestamp Findings:")
                            for finding in hygiene_res.findings:
                                f_col1, f_col2 = st.columns([3, 7])
                                with f_col1:
                                    # Locate matching frame thumbnail
                                    matching = next((f for f in frames_data if abs(f["timestamp_s"] - finding.timestamp_s) < 1.0), frames_data[0])
                                    if "image_bytes" in matching:
                                        st.image(matching["image_bytes"], caption=f"Time: {finding.timestamp_s:.1f}s", use_container_width=True)
                                with f_col2:
                                    severity_color = "red" if finding.severity.lower() == "high" else "orange" if finding.severity.lower() == "medium" else "green"
                                    st.markdown(f"**Category:** `{finding.category}` • **Severity:** :{severity_color}[{finding.severity}]")
                                    st.write(finding.observation)
                                st.markdown("---")

                            st.markdown("#### ✅ Corrective Action Plan:")
                            for plan_step in hygiene_res.practical_recommendations:
                                st.markdown(f"- {plan_step}")

                    except Exception as e:
                        st.error(f"Hygiene audit processing error: {e}")
        else:
            st.info("Upload kitchen footage to extract keyframes and identify food safety compliance hazards.")


# -------------------------------------------------------------
# Module 4: Smart Cooking Assistant & Recipe Builder
# -------------------------------------------------------------
elif nav_choice == "🍳 Smart Cooking Assistant":
    st.markdown("""
    <div class="brand-header">
        <h1>🍳 Smart Cooking Assistant & Recipe Builder</h1>
        <p>AI culinary engine for custom recipes, regional spice blends, dietary constraints, and interactive refinement.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5, 6], gap="large")

    with col1:
        st.subheader("1. Recipe Parameters")
        recipe_prompt = st.text_input("What would you like to cook?", placeholder="e.g. High protein paneer bowl, Healthy chicken stir fry")
        ingredients_input = st.text_area("Ingredients available in your pantry:", placeholder="Paneer, tomatoes, ginger, bell peppers, turmeric, cumin")
        
        row1, row2 = st.columns(2)
        with row1:
            cuisine = st.selectbox("Cuisine Style:", ["Any / Global", "Indian Regional", "Mediterranean", "Italian", "Mexican", "Asian / Thai", "American Comfort"])
            cook_time = st.slider("Target Cooking Time (minutes):", 10, 90, 30, step=5)
        with row2:
            diet = st.multiselect("Dietary Preferences:", ["Vegetarian", "Vegan", "High-Protein", "Gluten-Free", "Dairy-Free", "Keto", "Jain"], default=["Vegetarian"])
            servings = st.number_input("Servings:", min_value=1, max_value=10, value=2)

        gen_recipe_btn = st.button("👨‍🍳 Generate Step-by-Step Recipe", type="primary", use_container_width=True)

    with col2:
        st.subheader("2. Culinary Instructions & Nutrition")
        
        if gen_recipe_btn:
            if not recipe_prompt and not ingredients_input:
                st.error("Please enter either a recipe name or ingredients available.")
            else:
                with st.spinner("Formulating authentic recipe and calculating nutritional estimates..."):
                    ai_provider = get_ai_provider()
                    ingredients_list = [i.strip() for i in ingredients_input.split(",") if i.strip()] if ingredients_input else []
                    
                    try:
                        recipe_data = run_async(ai_provider.generate_recipe(
                            query=recipe_prompt or "Creative Chef Special",
                            ingredients=ingredients_list,
                            dietary_restrictions=diet,
                            cuisine=cuisine,
                            servings=servings,
                            cooking_time_min=cook_time
                        ))
                        st.session_state["current_recipe"] = recipe_data
                    except Exception as e:
                        st.error(f"Recipe generation error: {e}")

        # Render Active Recipe
        if "current_recipe" in st.session_state:
            rec = st.session_state["current_recipe"]
            
            st.markdown(f"""
            <div class="food-card">
                <h2 style="margin: 0; color: #111827;">{rec.get('title', 'Chef Recipe')}</h2>
                <p style="color: #6B7280; font-size: 0.9rem; margin-top: 4px;">{rec.get('description', '')}</p>
                <div style="display: flex; gap: 16px; margin-top: 10px; font-size: 0.85rem; color: #047857;">
                    <span>⏱️ <b>Prep:</b> {rec.get('prep_time_min', 10)} min</span>
                    <span>🍳 <b>Cook:</b> {rec.get('cook_time_min', 20)} min</span>
                    <span>🍽️ <b>Servings:</b> {rec.get('servings', 2)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Ingredients Checklist
            st.markdown("#### 🛒 Ingredients Checklist:")
            for ing in rec.get("ingredients", []):
                st.checkbox(f"**{ing.get('item', '')}**: {ing.get('amount', '')} *(Note: {ing.get('notes', 'fresh')})*", value=False, key=f"rec_ing_{ing.get('item')}")

            # Step-by-Step Instructions
            st.markdown("#### 🔪 Preparation & Cooking Steps:")
            for idx, step in enumerate(rec.get("instructions", []), 1):
                st.markdown(f"**Step {idx}:** {step}")

            # Smart Substitutions
            subs = rec.get("substitutions", [])
            if subs:
                st.markdown("#### 🔄 Smart Culinary Substitutions:")
                for sub in subs:
                    st.markdown(f"- Substitute **{sub.get('original')}** with **{sub.get('substitute')}** ({sub.get('ratio')}) — *{sub.get('notes')}*")

            # Estimated Nutrition
            nut = rec.get("estimated_nutrition", {})
            if nut:
                st.markdown("#### 📊 Estimated Nutrition Facts (Per Serving):")
                st.info(f"**Calories:** {nut.get('calories', 0)} kcal • **Protein:** {nut.get('protein_g', 0)}g • **Carbs:** {nut.get('carbs_g', 0)}g • **Fat:** {nut.get('fat_g', 0)}g")

            # Conversational Recipe Refinement Chat
            st.markdown("---")
            st.markdown("#### 💬 Ask Chef for Recipe Refinement:")
            refine_query = st.text_input("Ask a question about this recipe:", placeholder="e.g. Can I substitute tofu for paneer to make it vegan?")
            if st.button("Ask Chef", key="btn_refine"):
                if refine_query:
                    with st.spinner("Chef is advising..."):
                        ai_provider = get_ai_provider()
                        context = f"Current Recipe:\nTitle: {rec.get('title')}\nIngredients: {rec.get('ingredients')}"
                        reply = run_async(ai_provider.chat([{"role": "user", "content": refine_query}], context=context))
                        st.success(reply)
        else:
            st.info("Set your ingredients and cuisine on the left to generate customized culinary recipes.")


# -------------------------------------------------------------
# Module 5: Personalized Meal Planner (Zero-Allergen Protocol)
# -------------------------------------------------------------
elif nav_choice == "📅 Personalized Meal Planner":
    st.markdown("""
    <div class="brand-header">
        <h1>📅 Personalized Meal Planner</h1>
        <p>Physiological macro targets paired with strict Zero-Tolerance Allergen Protocol and consolidated grocery checklists.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5, 6], gap="large")

    with col1:
        st.subheader("1. Profile & Safety Parameters")
        goal = st.selectbox("Primary Nutritional Goal:", ["Healthy Maintenance", "Muscle Gain & Hypertrophy", "Fat Loss & Calorie Deficit", "Cardiovascular Health", "Glycemic Stability"])
        diet_pattern = st.selectbox("Dietary Pattern:", ["Vegetarian", "Vegan", "Balanced Whole Foods", "High-Protein Omnivore", "Pescatarian", "Keto / Low-Carb"])
        
        allergies = st.multiselect(
            "⚠️ Strict Allergen Exclusions (Zero-Tolerance Protocol):",
            ["Peanuts", "Tree Nuts", "Dairy / Milk", "Gluten / Wheat", "Soy", "Eggs", "Shellfish", "Fish", "Mustard", "Sesame"],
            default=["Peanuts"]
        )

        plan_days = st.slider("Duration (Days):", 1, 7, 3)
        meals_per_day = st.slider("Meals per day:", 3, 5, 3)

        gen_plan_btn = st.button("🥗 Generate Safe Meal Plan", type="primary", use_container_width=True)

    with col2:
        st.subheader("2. Meal Schedule & Grocery Checklist")

        if gen_plan_btn:
            with st.spinner("Formulating personalized meal schedule and filtering allergens..."):
                ai_provider = get_ai_provider()
                try:
                    plan = run_async(ai_provider.generate_meal_plan(
                        dietary_pattern=diet_pattern.lower(),
                        allergies=allergies,
                        restrictions=[],
                        goal=goal.lower(),
                        cuisine_preferences=["Indian", "Mediterranean", "Balanced"],
                        meals_per_day=meals_per_day,
                        days=plan_days
                    ))
                    st.session_state["active_meal_plan"] = plan
                except Exception as e:
                    st.error(f"Meal plan generation error: {e}")

        if "active_meal_plan" in st.session_state:
            plan_data = st.session_state["active_meal_plan"]
            
            st.markdown(f"""
            <div class="food-card">
                <h3 style="margin:0; color:#111827;">{plan_data.get('title', 'Weekly Plan')}</h3>
                <p style="color:#6B7280; font-size:0.85rem; margin-top:4px;">{plan_data.get('notes', 'Allergen-safe plan active.')}</p>
                <div style="display:flex; gap:16px; margin-top:8px; font-weight:700; color:#065F46;">
                    <span>🔥 Daily Target: {plan_data.get('total_calories', 1800)} kcal</span>
                    <span>🛡️ Safe Exclusions: {', '.join(allergies) if allergies else 'None specified'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Day tabs
            meals = plan_data.get("meals", [])
            days_set = sorted(list(set(m.get("day", 1) for m in meals)))
            
            day_tabs = st.tabs([f"Day {d}" for d in days_set])
            for idx, tab in enumerate(day_tabs):
                day_num = days_set[idx]
                with tab:
                    day_meals = [m for m in meals if m.get("day", 1) == day_num]
                    for m in day_meals:
                        st.markdown(f"**{m.get('meal_type')}:** {m.get('recipe_name')}")
                        st.caption(f"Estimated Calories: {m.get('calories', 0)} kcal • Description: {m.get('description', '')}")
                        st.markdown("---")

            # Consolidated Grocery Checklist
            groceries = plan_data.get("grocery_checklist", {})
            if groceries:
                st.markdown("#### 🛒 Consolidated Grocery List:")
                for category_name, items in groceries.items():
                    with st.expander(f"📁 {category_name} ({len(items)} items)", expanded=True):
                        for item in items:
                            st.checkbox(str(item), value=False, key=f"groc_{category_name}_{item}")
        else:
            st.info("Specify your nutritional goals and allergen exclusions on the left to generate your custom plan.")


# -------------------------------------------------------------
# Module 6: Central Multimodal AI Assistant
# -------------------------------------------------------------
elif nav_choice == "💬 Multimodal AI Assistant":
    st.markdown("""
    <div class="brand-header">
        <h1>💬 Central Multimodal AI Assistant</h1>
        <p>Conversational food and nutrition reasoning powered by Groq (`qwen/qwen3.8-27b`) and Whisper Speech-to-Text.</p>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Hello! I am FoodVerse AI, your multimodal nutrition and culinary intelligence assistant. Ask me anything about food scanning, recipe modifications, kitchen hygiene, or meal planning!"}
        ]

    # Voice input expander
    with st.expander("🎙️ Voice & Audio Speech-to-Text Input", expanded=False):
        audio_file = st.file_uploader("Upload voice question (WAV, MP3, M4A, WEBM)", type=["wav", "mp3", "m4a", "webm"])
        if audio_file and st.button("Transcribe Voice Question"):
            with st.spinner("Transcribing via Groq Whisper (`whisper-large-v3-turbo`)..."):
                ai_provider = get_ai_provider()
                try:
                    transcribed_text = run_async(ai_provider.transcribe_audio(audio_file.getvalue(), audio_file.type))
                    st.success(f"**Transcribed Speech:** {transcribed_text}")
                    st.session_state["pending_prompt"] = transcribed_text
                except Exception as e:
                    st.error(f"Voice transcription error: {e}")

    # Display chat history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input box
    prompt = st.chat_input("Ask FoodVerse AI a question...")
    if not prompt and "pending_prompt" in st.session_state:
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("FoodVerse AI is reasoning..."):
                ai_provider = get_ai_provider()
                try:
                    reply = run_async(ai_provider.chat(st.session_state["chat_history"]))
                except Exception as e:
                    reply = f"Error communicating with AI engine: {e}"
                st.write(reply)
                st.session_state["chat_history"].append({"role": "assistant", "content": reply})


# -------------------------------------------------------------
# Module 7: Verified Food Reference Database Explorer
# -------------------------------------------------------------
elif nav_choice == "🔬 Verified Lab Database":
    st.markdown("""
    <div class="brand-header">
        <h1>🔬 Verified USDA & ICMR Laboratory Database</h1>
        <p>Explore verified benchmark nutritional composition tables standardized per 100 grams.</p>
    </div>
    """, unsafe_allow_html=True)

    search_query = st.text_input("🔍 Search verified food database (e.g., Poha, Salmon, Quinoa, Pizza, Dal):", placeholder="Type food name...")

    records = []
    for key, val in VERIFIED_FOOD_DATABASE.items():
        if not search_query or search_query.lower() in key or search_query.lower() in val["canonical_name"].lower():
            records.append({
                "Dish Name": val["canonical_name"],
                "Category": val.get("category", "General"),
                "Serving": val.get("serving_description", "100g"),
                "Calories (kcal/100g)": val["per_100g"]["calories"],
                "Protein (g)": val["per_100g"]["protein_g"],
                "Carbs (g)": val["per_100g"]["carbs_g"],
                "Fats (g)": val["per_100g"]["fat_g"],
                "Fiber (g)": val["per_100g"].get("fiber_g", 0),
                "Allergens": ", ".join(val.get("allergens", [])) if val.get("allergens") else "None",
                "Source Reference": val.get("source", "USDA FoodData Central")
            })

    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(records)} verified laboratory benchmarks from USDA FoodData Central & ICMR.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>© 2026 FoodVerse AI • Built for Precision Nutrition, Scientific Truthfulness, and Culinary Intelligence</p>", unsafe_allow_html=True)
