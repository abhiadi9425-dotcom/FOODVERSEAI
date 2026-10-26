# FoodVerse AI — Scientific Truthfulness & AI Limitations

FoodVerse AI adheres to strict principles of scientific transparency, medical ethics, and responsible artificial intelligence. This document formalizes the capabilities, boundaries, and safety disclaimers of the platform.

---

## 1. Food Freshness & Microbiological Safety

### Critical Safety Directive:
> **A photograph cannot establish that food is microbiologically safe to consume.**

- **Pathogen Invisibility:** Dangerous foodborne pathogens (including *Salmonella enterica*, *Escherichia coli*, *Listeria monocytogenes*, and *Clostridium botulinum* neurotoxins) multiply and produce toxins without altering the color, texture, glossiness, or visible surface appearance of food.
- **Internal vs. External:** Surface images cannot inspect the internal flesh of meat, core of fruits, or subsurface anaerobic environments.
- **Temperature & Storage Precedence:** If food has remained at ambient room temperature in the "danger zone" (4°C to 60°C / 40°F to 140°F) beyond recommended public health durations (typically 2 hours), it must be considered hazardous and discarded regardless of clean visual appearance.
- **AI Role:** The Freshness Checker is strictly an auxiliary visual defect tool (detecting surface mold mycelium, bruising, oxidation, and wilting). It never certifies bacterial sterility.

---

## 2. Nutrition Estimation & Single-Photograph Uncertainty

### Calorie & Portion Scaling Boundaries:
> **A single 2D photograph cannot measure internal moisture, fat concentration, or exact gram weight.**

- **Hidden Ingredients:** Two identical-looking bowls of yellow curry can differ by over 400 calories depending on whether heavy cream, ghee, butter, or low-fat milk was used.
- **Porosity & Volume:** A photograph cannot determine density or void volume.
- **Pipeline Methodology:**
  1. Deep vision models identify the dish candidate.
  2. The application retrieves laboratory macronutrients per 100g from verified databases (USDA FoodData Central / ICMR Composition Tables).
  3. The platform allows users to enter exact portion weights in grams or choose standard serving benchmarks.
  4. The calculated nutrients are explicitly flagged as laboratory estimates scaled to the selected weight.

---

## 3. Commercial Kitchen Video Hygiene Audits

### Regulatory Disclaimer:
> **Video frame analysis provides internal quality oversight, not official legal or HACCP certification.**

- **Sampled Frame Gaps:** Automated processing samples keyframes at intervals (e.g. 2.0 seconds). Activities occurring between frames cannot be verified.
- **Visual Limitations:** Computer vision evaluates visible glove usage, hairnets, and station separation. It cannot test sanitizing chemical ppm concentrations, bacterial swab counts, or internal holding temperatures.
- **Non-Regulatory:** The platform is an internal training and operational audit tool, not a substitute for certified municipal health department inspections.

---

## 4. Dietary Restrictions & Allergen Exclusions

### Zero-Tolerance Allergen Protocol:
- If a user specifies an allergy (e.g. peanuts, tree nuts, shellfish, gluten, dairy), the meal planner and recipe assistant filter ingredients strictly.
- When an AI model suggests a dish with potential cross-contamination risk, the system automatically flags the item with substitution guidance.
- Users with severe anaphylactic allergies must always inspect original commercial packaging labels.

---

## 5. Mode Operation Matrix

| Capability | With External AI Keys (Gemini / OpenAI) | Without External AI Keys (Offline / Local) |
| :--- | :--- | :--- |
| **Food Recognition** | Neural multi-food visual bounding & confidence | Manual selection from 20+ verified USDA/ICMR lab benchmark dishes |
| **Portion & Calorie Scaling** | Automatic portion estimation + user gram slider | Exact USDA laboratory gram scaling via interactive portion slider |
| **Freshness Check** | Visual neural defect & discoloration detection | Category-specific food safety inspection checklist & guidance |
| **Hygiene Video Monitoring** | OpenCV frame extraction + vision model analysis | OpenCV keyframe extraction + metadata & protocol validation |
| **Smart Cooking** | Generative conversational LLM recipe assistant | Deterministic recipe generator with USDA nutritional derivation |
| **Meal Planning** | Personalized 7-day adaptive schedules | Deterministic 7-day allergen-filtered meal schedules |
| **Multimodal Assistant** | Conversational voice transcription & reasoning | Rule-based guidance & domain routing across capabilities |
| **User Data Isolation** | Persisted private SQLite/Postgres storage | Persisted private SQLite/Postgres storage |
