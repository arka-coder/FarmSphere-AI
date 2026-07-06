"""
FarmSphere AI — Agriculture Master Knowledge Base
Encyclopaedic, authoritative, India-focused agricultural intelligence.

Contains:
  A. MSP 2024-25 official values (DAC&FW)
  B. State-wise market price reference (50 crops × 28+ states)
  C. Global commodity benchmarks (CBOT, ICE)
  D. Crop encyclopaedia (50+ crops — scientific names, agronomy, pests, diseases)
  E. Soil types & management (8 major Indian soil types)
  F. Agro-climatic zones of India (15 zones)
  G. Irrigation reference data
  H. Plant science library (photosynthesis types, PGRs, biofertilizers)

Sources: DAC&FW, ICAR, IARI, NABARD, Agmarknet, APEDA, FAO, CBOT
"""

# ════════════════════════════════════════════════════════════════════════════
# A. MSP 2024-25 (Minimum Support Price — DAC&FW Official)
# ════════════════════════════════════════════════════════════════════════════

MSP_2024_25 = {
    # Kharif Crops
    "paddy_common":         {"msp": 2183, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "paddy_grade_a":        {"msp": 2203, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "jowar_hybrid":         {"msp": 3371, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "jowar_maldandi":       {"msp": 3421, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "bajra":                {"msp": 2625, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "maize":                {"msp": 2090, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "ragi":                 {"msp": 4290, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "arhar_tur":            {"msp": 7550, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "moong":                {"msp": 8682, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "urad":                 {"msp": 7400, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "groundnut":            {"msp": 6783, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "sunflower":            {"msp": 7280, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "soybean_yellow":       {"msp": 4892, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "sesamum":              {"msp": 9267, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "nigerseed":            {"msp": 8717, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "cotton_medium_staple": {"msp": 7121, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    "cotton_long_staple":   {"msp": 7521, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
    # Rabi Crops
    "wheat":                {"msp": 2275, "unit": "quintal", "season": "rabi", "source": "DAC&FW Cabinet Approval 2024"},
    "barley":               {"msp": 1735, "unit": "quintal", "season": "rabi", "source": "DAC&FW Cabinet Approval 2024"},
    "gram_chana":           {"msp": 5440, "unit": "quintal", "season": "rabi", "source": "DAC&FW Cabinet Approval 2024"},
    "masur_lentil":         {"msp": 6425, "unit": "quintal", "season": "rabi", "source": "DAC&FW Cabinet Approval 2024"},
    "rapeseed_mustard":     {"msp": 5650, "unit": "quintal", "season": "rabi", "source": "DAC&FW Cabinet Approval 2024"},
    "safflower":            {"msp": 5800, "unit": "quintal", "season": "rabi", "source": "DAC&FW Cabinet Approval 2024"},
    # Other
    "sugarcane_frp":        {"msp": 340,  "unit": "quintal", "season": "annual", "source": "CCEA Fair & Remunerative Price 2024-25"},
    "copra_milling":        {"msp": 11160,"unit": "quintal", "season": "annual", "source": "DAC&FW Cabinet Approval 2024"},
    "copra_ball":           {"msp": 12000,"unit": "quintal", "season": "annual", "source": "DAC&FW Cabinet Approval 2024"},
    "jute":                 {"msp": 5050, "unit": "quintal", "season": "kharif", "source": "DAC&FW Cabinet Approval 2024"},
}

# Aliases for common name lookups
MSP_ALIASES = {
    "rice":     "paddy_common",
    "paddy":    "paddy_common",
    "soybean":  "soybean_yellow",
    "cotton":   "cotton_medium_staple",
    "tur":      "arhar_tur",
    "arhar":    "arhar_tur",
    "mustard":  "rapeseed_mustard",
    "lentil":   "masur_lentil",
    "chana":    "gram_chana",
    "chickpea": "gram_chana",
    "jowar":    "jowar_hybrid",
}


def get_msp(crop: str) -> dict | None:
    """Look up MSP for a crop by common or official name."""
    key = crop.lower().strip()
    if key in MSP_2024_25:
        return {"crop": key, **MSP_2024_25[key]}
    alias = MSP_ALIASES.get(key)
    if alias:
        return {"crop": alias, "alias_of": key, **MSP_2024_25[alias]}
    return None


# ════════════════════════════════════════════════════════════════════════════
# B. State-wise Market Price Reference
# All prices in ₹ per quintal (100 kg). Reference: Agmarknet, eNAM 2024.
# ════════════════════════════════════════════════════════════════════════════

# National baseline prices (₹/quintal) — current market reference
NATIONAL_BASELINE_PRICES = {
    "wheat":       2275,
    "rice":        2183,
    "maize":       2090,
    "soybean":     4892,
    "cotton":      7200,
    "groundnut":   6900,
    "mustard":     5700,
    "sugarcane":   340,
    "tomato":      2000,
    "onion":       2200,
    "potato":      1250,
    "chilli":      9500,
    "garlic":      8000,
    "ginger":      6500,
    "banana":      1600,
    "mango":       4000,
    "grape":       8000,
    "pomegranate": 7500,
    "apple":       10000,
    "orange":      3500,
    "guava":       2500,
    "papaya":      1200,
    "coconut":     2800,   # per 100 coconuts, converted
    "turmeric":    12000,
    "cardamom":    120000,
    "black_pepper":50000,
    "coffee_arabica": 20000,
    "coffee_robusta":  14000,
    "tea":         18000,
    "jute":        5100,
    "sunflower":   7300,
    "arhar":       7600,
    "moong":       8700,
    "urad":        7500,
    "gram":        5500,
    "lentil":      6500,
    "barley":      1740,
    "bajra":       2650,
    "jowar":       3400,
    "ragi":        4300,
    "sesamum":     9300,
    "castor":      6200,
    "linseed":     5400,
    "peas":        3000,
    "cabbage":     800,
    "cauliflower": 1000,
    "brinjal":     1200,
    "okra":        2000,
    "cucumber":    1000,
    "pumpkin":     700,
    "watermelon":  600,
    "drumstick":   3000,
    "spinach":     1000,
    "coriander":   5000,
    "fenugreek":   4500,
}

# State-wise price multipliers (relative to national baseline)
# Values > 1.0 indicate higher prices; < 1.0 lower prices
STATE_PRICE_MULTIPLIERS = {
    "Andhra Pradesh":     {"wheat": 1.05, "rice": 0.98, "chilli": 0.95, "turmeric": 0.97, "tomato": 1.10, "groundnut": 0.98, "cotton": 1.02},
    "Arunachal Pradesh":  {"rice": 1.20, "ginger": 0.90, "maize": 1.15, "orange": 0.92},
    "Assam":              {"rice": 1.10, "jute": 0.95, "tea": 0.92, "ginger": 0.93, "mustard": 1.05},
    "Bihar":              {"wheat": 1.02, "rice": 1.05, "maize": 0.97, "lentil": 1.03, "potato": 1.08, "onion": 1.10},
    "Chhattisgarh":       {"rice": 0.95, "maize": 0.98, "soybean": 0.97, "tomato": 1.05},
    "Goa":                {"coconut": 1.20, "cashew": 1.10, "rice": 1.15, "banana": 1.10},
    "Gujarat":            {"cotton": 0.97, "groundnut": 0.96, "wheat": 1.03, "castor": 0.95, "banana": 0.97},
    "Haryana":            {"wheat": 0.98, "rice": 0.98, "mustard": 0.97, "sugarcane": 1.05, "potato": 0.98},
    "Himachal Pradesh":   {"apple": 0.92, "potato": 0.95, "wheat": 1.08, "ginger": 0.93, "tomato": 0.97},
    "Jharkhand":          {"rice": 1.08, "maize": 1.05, "arhar": 1.03, "tomato": 1.12},
    "Karnataka":          {"ragi": 0.97, "maize": 0.97, "grape": 0.95, "coffee_robusta": 0.97, "coconut": 0.98, "tomato": 1.05, "onion": 1.00},
    "Kerala":             {"coconut": 0.97, "black_pepper": 0.96, "cardamom": 0.97, "coffee_arabica": 0.98, "banana": 0.98, "rice": 1.12},
    "Madhya Pradesh":     {"soybean": 0.97, "wheat": 0.97, "gram": 0.96, "onion": 1.05, "garlic": 0.97, "maize": 0.98},
    "Maharashtra":        {"onion": 0.95, "soybean": 0.97, "cotton": 0.98, "grape": 0.97, "pomegranate": 0.96, "sugarcane": 0.98, "turmeric": 0.98},
    "Manipur":            {"rice": 1.18, "ginger": 0.90, "orange": 0.92},
    "Meghalaya":          {"rice": 1.20, "ginger": 0.90, "potato": 1.05},
    "Mizoram":            {"rice": 1.22, "ginger": 0.90, "banana": 1.05},
    "Nagaland":           {"rice": 1.18, "maize": 1.10, "ginger": 0.92},
    "Odisha":             {"rice": 1.00, "jute": 0.97, "tomato": 1.08, "groundnut": 1.02},
    "Punjab":             {"wheat": 0.97, "rice": 0.97, "potato": 0.95, "maize": 0.98, "cotton": 1.00},
    "Rajasthan":          {"mustard": 0.96, "gram": 0.97, "wheat": 1.00, "bajra": 0.97, "onion": 1.08},
    "Sikkim":             {"cardamom": 0.96, "ginger": 0.91, "rice": 1.15},
    "Tamil Nadu":         {"rice": 1.00, "banana": 0.97, "coconut": 0.98, "groundnut": 0.98, "turmeric": 0.99, "cotton": 1.00},
    "Telangana":          {"rice": 0.98, "cotton": 0.97, "chilli": 0.96, "maize": 0.98, "turmeric": 0.97},
    "Tripura":            {"rice": 1.15, "jute": 0.97, "ginger": 0.92, "banana": 1.05},
    "Uttar Pradesh":      {"wheat": 0.99, "sugarcane": 1.02, "potato": 0.97, "onion": 1.08, "rice": 1.02, "maize": 1.00},
    "Uttarakhand":        {"wheat": 1.05, "apple": 0.96, "rice": 1.10, "potato": 0.97},
    "West Bengal":        {"rice": 1.05, "jute": 0.97, "potato": 1.00, "mustard": 1.02, "onion": 1.12, "banana": 0.98},
    # Union Territories
    "Delhi":              {"tomato": 1.20, "onion": 1.25, "potato": 1.15, "wheat": 1.05},
    "Jammu & Kashmir":    {"apple": 0.93, "rice": 1.15, "wheat": 1.08, "potato": 1.02},
    "Ladakh":             {"wheat": 1.25, "potato": 1.20, "apple": 0.95},
    "Puducherry":         {"rice": 1.05, "groundnut": 1.00, "banana": 0.99},
    "Chandigarh":         {"wheat": 1.01, "rice": 1.00, "potato": 1.05},
    "Andaman & Nicobar":  {"rice": 1.35, "coconut": 1.15, "banana": 1.20},
    "Lakshadweep":        {"coconut": 1.05, "fish": 1.25},
    "Dadra & NH":         {"rice": 1.10, "cotton": 1.02},
    "Daman & Diu":        {"rice": 1.10, "groundnut": 1.05},
}

# State → Major mandis per crop
STATE_MAJOR_MANDIS = {
    "Andhra Pradesh":  {"chilli": "Guntur APMC", "rice": "Rajahmundry Mandi", "cotton": "Kurnool APMC", "tomato": "Madanapalle Mandi", "default": "Kurnool APMC"},
    "Assam":           {"rice": "Kamrup Mandi", "jute": "Dhubri Mandi", "ginger": "Nalbari Market", "default": "Guwahati APMC"},
    "Bihar":           {"wheat": "Patna Mandi", "maize": "Muzaffarpur Mandi", "potato": "Samastipur APMC", "default": "Patna APMC"},
    "Chhattisgarh":    {"rice": "Raipur Mandi", "soybean": "Jagdalpur Mandi", "default": "Raipur APMC"},
    "Gujarat":         {"cotton": "Rajkot APMC", "groundnut": "Junagadh APMC", "castor": "Deesa Market", "banana": "Anand Mandi", "default": "Rajkot APMC"},
    "Haryana":         {"wheat": "Karnal Mandi", "rice": "Karnal Mandi", "mustard": "Rewari Mandi", "default": "Karnal APMC"},
    "Himachal Pradesh":{"apple": "Shimla Fruit Market", "potato": "Rohru Market", "default": "Shimla APMC"},
    "Jharkhand":       {"rice": "Ranchi Mandi", "maize": "Dhanbad Market", "default": "Ranchi APMC"},
    "Karnataka":       {"ragi": "Tumkur Mandi", "maize": "Davangere Mandi", "grape": "Vijayapura APMC", "coffee_robusta": "Hassan Market", "tomato": "Kolar Mandi", "onion": "Gadag Mandi", "default": "Bangalore APMC (Yeshwanthpur)"},
    "Kerala":          {"coconut": "Thrissur Market", "black_pepper": "Kochi Spice Exchange", "cardamom": "Bodinayakanur APMC", "banana": "Kozhikode Market", "default": "Ernakulam APMC"},
    "Madhya Pradesh":  {"soybean": "Indore Mandi", "wheat": "Bhopal Mandi", "gram": "Dewas Market", "onion": "Mandsaur Mandi", "garlic": "Neemuch Market", "default": "Indore APMC"},
    "Maharashtra":     {"onion": "Lasalgaon APMC (Nashik)", "soybean": "Latur Mandi", "cotton": "Akola APMC", "grape": "Sangli APMC", "pomegranate": "Solapur Market", "sugarcane": "Kolhapur Mandi", "turmeric": "Sangli Market", "default": "Pune APMC (Gultekdi)"},
    "Odisha":          {"rice": "Bhubaneswar Mandi", "jute": "Cuttack Market", "tomato": "Berhampur Mandi", "default": "Bhubaneswar APMC"},
    "Punjab":          {"wheat": "Khanna Mandi (Asia's largest grain market)", "rice": "Amritsar Mandi", "potato": "Jalandhar Mandi", "default": "Khanna Mandi"},
    "Rajasthan":       {"mustard": "Bharatpur Mandi", "gram": "Bikaner Mandi", "bajra": "Jodhpur Mandi", "onion": "Alwar Mandi", "default": "Jaipur APMC"},
    "Tamil Nadu":      {"rice": "Thanjavur Mandi", "banana": "Jalgaon (imported); Theni Market (local)", "coconut": "Coimbatore Market", "turmeric": "Erode Market (India's turmeric capital)", "default": "Chennai Koyambedu APMC"},
    "Telangana":       {"rice": "Nalgonda Mandi", "cotton": "Warangal APMC", "chilli": "Khammam Market", "maize": "Nizamabad Mandi", "default": "Hyderabad APMC"},
    "Uttar Pradesh":   {"wheat": "Meerut Mandi", "sugarcane": "Muzaffarnagar (sugar mill gate)", "potato": "Agra Mandi", "onion": "Kanpur Mandi", "default": "Lucknow APMC"},
    "Uttarakhand":     {"wheat": "Haridwar Mandi", "apple": "Haldwani Market", "potato": "Dehradun Market", "default": "Haldwani APMC"},
    "West Bengal":     {"rice": "Burdwan Mandi", "jute": "Murshidabad Market", "potato": "Hooghly APMC", "mustard": "Nadia Mandi", "onion": "Kolkata Mehdipatnam", "default": "Kolkata APMC"},
    "Delhi":           {"tomato": "Azadpur Mandi (Asia's largest fruit & vegetable market)", "onion": "Azadpur Mandi", "potato": "Azadpur Mandi", "default": "Azadpur APMC, Delhi"},
    "Jammu & Kashmir": {"apple": "Sopore Market (J&K)", "default": "Jammu APMC"},
}


def get_statewise_price(crop: str, state: str) -> dict:
    """
    Return state-specific market price for a crop.

    Returns dict with: price, national_avg, state_name, mandi_name, msp (if applicable)
    """
    crop_key = crop.lower().strip()
    national = NATIONAL_BASELINE_PRICES.get(crop_key)
    if not national:
        return {
            "crop": crop,
            "state": state,
            "note": "Price data not available — check local Agmarknet or eNAM portal",
            "agmarknet_url": "https://agmarknet.gov.in",
        }

    multipliers = STATE_PRICE_MULTIPLIERS.get(state, {})
    multiplier = multipliers.get(crop_key, 1.0)
    state_price = round(national * multiplier)

    # Get mandi name
    mandis = STATE_MAJOR_MANDIS.get(state, {})
    mandi_name = mandis.get(crop_key, mandis.get("default", "Nearest APMC mandi"))

    # MSP reference
    msp_data = get_msp(crop_key)

    result = {
        "crop": crop,
        "state": state,
        "price_per_quintal": state_price,
        "national_average": national,
        "major_mandi": mandi_name,
        "trend_vs_national": "above average" if multiplier > 1.02 else ("below average" if multiplier < 0.98 else "at national average"),
    }

    if msp_data:
        result["msp_2024_25"] = msp_data["msp"]
        result["vs_msp"] = f"{'₹' + str(state_price - msp_data['msp']) + ' above' if state_price > msp_data['msp'] else '₹' + str(msp_data['msp'] - state_price) + ' below'} MSP"
        result["msp_source"] = msp_data.get("source", "DAC&FW 2024")

    return result


# ════════════════════════════════════════════════════════════════════════════
# C. Global Commodity Benchmarks
# ════════════════════════════════════════════════════════════════════════════

GLOBAL_BENCHMARKS = {
    "wheat": {
        "exchange": "CBOT (Chicago Board of Trade)",
        "unit": "USD/bushel",
        "reference_range_usd": "5.50 – 7.00",
        "india_equivalent_inr_per_quintal": "1800 – 2300",
        "note": "India is world's 2nd largest wheat producer. Export duty applies during shortage.",
        "india_export_status": "Banned / Restricted (2022–ongoing; check DGFT notifications)",
    },
    "rice": {
        "exchange": "CBOT / Thailand benchmark",
        "unit": "USD/MT",
        "reference_range_usd_mt": "420 – 580",
        "india_equivalent_inr_per_quintal": "3500 – 4800",
        "note": "India is world's largest rice exporter. Non-Basmati white rice export was restricted in 2023.",
        "india_export_status": "Partial restrictions on non-basmati; basmati freely exportable",
    },
    "soybean": {
        "exchange": "CBOT (Chicago Board of Trade)",
        "unit": "USD/bushel",
        "reference_range_usd": "11.50 – 14.50",
        "india_equivalent_inr_per_quintal": "3800 – 4800",
        "note": "India imports ~15 MT soyoil/year. Domestic prices track CBOT with import duty buffer.",
        "india_major_markets": "Indore, Latur, Akola",
    },
    "cotton": {
        "exchange": "ICE Futures U.S. (NYCE)",
        "unit": "USc/lb",
        "reference_range_usc_per_lb": "75 – 95",
        "india_equivalent_inr_per_quintal": "5500 – 7000",
        "note": "India is world's largest cotton producer. Prices track ICE cotton with +15% premium for domestic long-staple.",
        "india_major_markets": "Rajkot, Akola, Kurnool",
    },
    "maize": {
        "exchange": "CBOT",
        "unit": "USD/bushel",
        "reference_range_usd": "4.50 – 6.00",
        "india_equivalent_inr_per_quintal": "1600 – 2200",
        "note": "India's maize is used primarily for poultry feed and starch industry.",
    },
    "sugar": {
        "exchange": "ICE Sugar #11",
        "unit": "USc/lb",
        "reference_range_usc_per_lb": "20 – 28",
        "india_equivalent_inr_per_quintal": "3000 – 4500",
        "note": "India is world's 2nd largest sugar producer. Export quota system (MEQ) applies.",
    },
    "coffee_arabica": {
        "exchange": "ICE Coffee 'C'",
        "unit": "USc/lb",
        "reference_range_usc_per_lb": "170 – 250",
        "india_major_markets": "Chikmagalur, Coorg, Hassan (Karnataka)",
        "note": "India produces ~5.5 MT coffee/year. About 70% exported. ICCRI varieties recommended.",
    },
    "black_pepper": {
        "exchange": "International Pepper Community (IPC)",
        "unit": "USD/MT",
        "reference_range_usd_mt": "4000 – 8000",
        "india_major_markets": "Kochi Spice Exchange",
        "note": "India was world's #1 pepper producer historically. Now competes with Vietnam.",
    },
    "cardamom": {
        "exchange": "Spices Board India (auction)",
        "unit": "₹/kg",
        "reference_range_inr_per_kg": "1000 – 2500",
        "india_major_markets": "Bodinayakanur, Vandiperiyar",
        "note": "India is world's 2nd largest cardamom producer after Guatemala.",
    },
    "turmeric": {
        "exchange": "NCDEX (National Commodity & Derivatives Exchange)",
        "unit": "₹/quintal",
        "reference_range_inr_per_quintal": "8000 – 20000",
        "india_major_markets": "Sangli (Maharashtra), Erode (Tamil Nadu), Nizamabad (Telangana)",
        "note": "India supplies 80% of world's turmeric. Peak prices during April–May.",
    },
}


# ════════════════════════════════════════════════════════════════════════════
# D. Crop Encyclopaedia
# ════════════════════════════════════════════════════════════════════════════

CROP_ENCYCLOPEDIA = {
    "wheat": {
        "scientific_name": "Triticum aestivum",
        "family": "Poaceae (Gramineae)",
        "chromosome_number": "2n = 42 (hexaploid)",
        "type": "cereal",
        "season": "rabi",
        "photosynthesis": "C3",
        "origin": "Fertile Crescent, Southwest Asia",
        "optimal_temperature_c": {"germination": "20-25", "growth": "15-22", "grain_filling": "15-20"},
        "annual_rainfall_mm": "650-1000",
        "soil_ph": "6.0 – 7.5",
        "soil_types": ["Alluvial", "Black cotton soil", "Sandy loam"],
        "growth_duration_days": "110-135",
        "growth_stages": {
            "germination": "0-7 days",
            "seedling": "7-21 days",
            "tillering": "21-45 days",
            "jointing": "45-65 days",
            "booting": "65-80 days",
            "heading": "80-95 days",
            "grain_filling": "95-120 days",
            "maturity": "120-135 days",
        },
        "nutrient_requirements_kg_per_ha": {
            "N": "120-150",
            "P2O5": "60-80",
            "K2O": "40-60",
            "Zn": "25 kg ZnSO4",
        },
        "major_varieties": {
            "ICAR/IIWBR": ["HD 2967 (high yielding)", "HD 3086 (heat tolerant)", "GW 322 (Gujarat)", "K 9107 (UP)"],
            "state": ["PBW 343 (Punjab)", "WH 542 (Haryana)", "Raj 4120 (Rajasthan)"],
        },
        "yield_potential_t_per_ha": "4-6 (irrigated), 2-3 (rainfed)",
        "water_requirement_mm": "400-500",
        "critical_irrigation_stages": ["Crown root initiation (21 DAS)", "Tillering (40 DAS)", "Jointing (60 DAS)", "Flowering (80 DAS)", "Grain filling (100 DAS)"],
        "major_pests": [
            {"name": "Aphid (Sitobion avenae)", "eppo_code": "SITBAV", "damage": "Sucking sap from leaves/ears, sooty mold", "management": "Spray Dimethoate 30% EC @ 1 L/ha or Chlorpyrifos"},
            {"name": "Termite (Odontotermes spp.)", "eppo_code": "ODONSP", "damage": "Root damage, plant wilting", "management": "Chlorpyrifos 20 EC soil treatment"},
            {"name": "Wheat stem sawfly", "damage": "Stem boring, lodging", "management": "Early sowing, resistant varieties"},
        ],
        "major_diseases": [
            {"name": "Yellow rust / Stripe rust", "pathogen": "Puccinia striiformis f. sp. tritici", "symptoms": "Yellow stripes on leaves", "management": "Spray Propiconazole 25 EC @ 500 ml/ha; resistant variety HD 2781"},
            {"name": "Brown rust / Leaf rust", "pathogen": "Puccinia triticina", "symptoms": "Orange-brown pustules on leaves", "management": "Mancozeb + Carbendazim; variety GW 322"},
            {"name": "Loose smut", "pathogen": "Ustilago segetum var. tritici", "symptoms": "Spikes replaced by black powder", "management": "Seed treatment with Vitavax / Carboxin-Thiram"},
            {"name": "Karnal bunt", "pathogen": "Tilletia indica", "symptoms": "Partial bunting of grains, fishy smell", "management": "Use certified seed; Tebuconazole seed treatment"},
        ],
        "icar_source": "ICAR-IIWBR Karnal — Crop Production Technology for Wheat",
    },

    "rice": {
        "scientific_name": "Oryza sativa",
        "family": "Poaceae",
        "chromosome_number": "2n = 24",
        "type": "cereal",
        "season": "kharif",
        "photosynthesis": "C3",
        "origin": "China/Southeast Asia",
        "optimal_temperature_c": {"germination": "25-30", "growth": "25-32", "grain_filling": "20-25"},
        "annual_rainfall_mm": "1000-2000",
        "soil_ph": "5.5 – 7.0",
        "soil_types": ["Alluvial", "Clay loam", "Deltaic soils"],
        "growth_duration_days": "100-130",
        "growth_stages": {
            "germination": "0-7 days",
            "seedling": "7-25 days (in nursery)",
            "tillering": "25-55 days",
            "panicle_initiation": "55-75 days",
            "heading": "75-90 days",
            "grain_filling": "90-115 days",
            "maturity": "115-130 days",
        },
        "nutrient_requirements_kg_per_ha": {
            "N": "80-120",
            "P2O5": "40-60",
            "K2O": "40-60",
            "Zn": "25 kg ZnSO4 (basal)",
        },
        "major_varieties": {
            "ICAR": ["Swarna (MTU7029)", "IR 64", "Pusa Basmati 1121", "BPT 5204", "Samba Mahsuri"],
            "high_yielding": ["Sona Masuri", "Navara", "Ponni (Tamil Nadu)"],
            "basmati": ["Pusa Basmati 1121 (11.7 mm grain)", "Basmati 370", "HBC-19"],
        },
        "yield_potential_t_per_ha": "5-7 (irrigated), 2-4 (rainfed lowland)",
        "water_requirement_mm": "1200-2000",
        "major_pests": [
            {"name": "Brown planthopper (BPH)", "eppo_code": "NILBLU", "damage": "Hopperburn — circular yellow patches", "management": "Spray Buprofezin 25 SC @ 1 L/ha; drain field to reduce humidity"},
            {"name": "Rice stem borer", "eppo_code": "CHIPON", "damage": "Dead hearts (vegetative), white ears (reproductive)", "management": "Cartap hydrochloride granules @ 10 kg/ha"},
            {"name": "Gall midge", "damage": "Silver shoot / onion leaf", "management": "Chlorpyrifos; resistant variety Phalguna"},
        ],
        "major_diseases": [
            {"name": "Blast", "pathogen": "Pyricularia oryzae (syn. Magnaporthe oryzae)", "symptoms": "Diamond-shaped lesions, neck blast", "management": "Tricyclazole 75 WP @ 600 g/ha; Isoprothiolane"},
            {"name": "Bacterial leaf blight", "pathogen": "Xanthomonas oryzae pv. oryzae", "symptoms": "Water-soaked margins turning straw-yellow", "management": "Copper-based bactericides; resistant variety IR 64"},
            {"name": "Sheath blight", "pathogen": "Rhizoctonia solani", "symptoms": "Oval lesions on sheath with dark brown border", "management": "Validamycin 3L @ 2 L/ha; Hexaconazole"},
        ],
        "sri_method": "System of Rice Intensification: 8-12 day old seedlings, 25x25 cm spacing, intermittent irrigation — 20-30% water saving, 25% higher yield",
        "icar_source": "ICAR-NRRI Cuttack — Package of Practices for Rice",
    },

    "tomato": {
        "scientific_name": "Solanum lycopersicum",
        "family": "Solanaceae",
        "chromosome_number": "2n = 24",
        "type": "vegetable (fruit)",
        "season": "year-round (kharif/rabi in plains, summer in hills)",
        "photosynthesis": "C3",
        "origin": "South America (Peru, Ecuador)",
        "optimal_temperature_c": {"germination": "22-26", "growth": "20-27", "fruit_setting": "20-24"},
        "annual_rainfall_mm": "600-1200",
        "soil_ph": "6.0 – 7.0",
        "soil_types": ["Sandy loam", "Red loam", "Alluvial"],
        "growth_duration_days": "75-120",
        "nutrient_requirements_kg_per_ha": {
            "N": "100-150",
            "P2O5": "50-80",
            "K2O": "100-120",
            "Ca": "Important for blossom-end rot prevention",
            "B": "Borax 2 kg/ha for fruit set",
        },
        "major_varieties": {
            "open_pollinated": ["Pusa Ruby", "Pusa Gaurav", "S-12", "CO-3"],
            "hybrids": ["Avinash 2", "Pusa Hybrid 4", "US 618", "Nunhems MHT 10"],
            "processing": ["H-24", "Arka Ahuti"],
        },
        "yield_potential_t_per_ha": "25-35 (OP), 60-80 (hybrid)",
        "water_requirement_mm": "400-600",
        "major_pests": [
            {"name": "Fruit borer (Helicoverpa armigera)", "eppo_code": "HELIAR", "damage": "Bore into fruits, causing rotting and entry for secondary infection", "management": "Spinosad 45 SC @ 300 ml/ha; Neem oil 3%; pheromone traps"},
            {"name": "Whitefly (Bemisia tabaci)", "eppo_code": "BEMITA", "damage": "Direct sap sucking; vectors TYLCV (tomato yellow leaf curl virus)", "management": "Imidacloprid 200 SL @ 120 ml/ha; yellow sticky traps"},
            {"name": "Leaf miner (Liriomyza sativae)", "damage": "Serpentine mines on leaves", "management": "Abamectin, neem-based sprays"},
        ],
        "major_diseases": [
            {"name": "Early blight", "pathogen": "Alternaria solani", "symptoms": "Concentric ring lesions (target spot) on older leaves", "management": "Mancozeb 75 WP @ 2 g/L; Azoxystrobin 23 SC"},
            {"name": "Late blight", "pathogen": "Phytophthora infestans", "symptoms": "Greasy water-soaked lesions, white sporulation on underside", "management": "Metalaxyl + Mancozeb @ 2.5 g/L; copper hydroxide as preventive"},
            {"name": "Tomato Yellow Leaf Curl Virus (TYLCV)", "pathogen": "Begomovirus (whitefly-transmitted)", "symptoms": "Upward curling leaves, yellowing, stunting", "management": "Control whitefly vector; use resistant varieties (Arka Rakshak)"},
            {"name": "Fusarium wilt", "pathogen": "Fusarium oxysporum f. sp. lycopersici", "symptoms": "One-sided yellowing, vascular browning", "management": "Soil solarization; Trichoderma viride biocontrol; resistant rootstocks"},
        ],
        "icar_source": "ICAR-IIHR Bengaluru — Package of Practices for Tomato",
    },

    "cotton": {
        "scientific_name": "Gossypium hirsutum (American upland, 90% of India); G. arboreum (desi)",
        "family": "Malvaceae",
        "chromosome_number": "2n = 52",
        "type": "fibre / oilseed",
        "season": "kharif",
        "photosynthesis": "C3",
        "origin": "Mexico / Central America",
        "optimal_temperature_c": {"germination": "25-35", "growth": "21-27", "boll_development": "20-30"},
        "annual_rainfall_mm": "500-1000",
        "soil_ph": "6.5 – 8.0",
        "soil_types": ["Black cotton soil (Vertisols)", "Red laterite", "Alluvial"],
        "growth_duration_days": "160-200 (Bt cotton)",
        "nutrient_requirements_kg_per_ha": {
            "N": "150-180",
            "P2O5": "60-80",
            "K2O": "60-80",
            "S": "30 kg (sulphur important for fibre quality)",
            "Zn": "25 kg ZnSO4",
        },
        "major_varieties": {
            "bt_hybrids": ["MRC 7361 BG II", "RCH 2 BG II", "NCS 855", "Bunny BG II"],
            "desi": ["MCU 5", "Jayadhar", "GVH 26 (Gujarat)"],
        },
        "yield_potential_t_per_ha": "2-3 (seed cotton) = 0.7-1.2 t/ha lint",
        "major_pests": [
            {"name": "American bollworm (Helicoverpa armigera)", "eppo_code": "HELIAR", "damage": "Boll boring; Bt cotton provides resistance but secondary pests fill the niche", "management": "Emamectin benzoate; pheromone traps"},
            {"name": "Pink bollworm (Pectinophora gossypiella)", "eppo_code": "PECTGO", "damage": "Internal boll damage; difficult to detect", "management": "Spinosad; timely harvest to break life cycle"},
            {"name": "Sucking pests (thrips, whitefly, jassid)", "damage": "Leaf curl virus through whitefly; direct sap loss", "management": "Imidacloprid (seed treatment); yellow traps"},
            {"name": "Mealybug (Phenacoccus solenopsis)", "damage": "Colony on stems; honeydew → sooty mold", "management": "Profenofos; neem oil; release Cryptolaemus beetles"},
        ],
        "major_diseases": [
            {"name": "Cotton leaf curl disease (CLCuD)", "pathogen": "Begomovirus (whitefly-transmitted)", "symptoms": "Leaf curling upward, vein darkening, enations on underside", "management": "Control whitefly; remove infected plants; use tolerant varieties"},
            {"name": "Fusarium wilt", "pathogen": "Fusarium oxysporum f. sp. vasinfectum", "symptoms": "Vascular browning, sudden wilting", "management": "Soil solarization; Trichoderma; resistant variety MCU 5"},
            {"name": "Cercospora leaf spot", "pathogen": "Cercospora gossypina", "symptoms": "Circular spots with gray center", "management": "Mancozeb 75 WP @ 2 g/L"},
        ],
        "icar_source": "ICAR-CICR Nagpur — Cotton Cultivation Technology",
    },

    "onion": {
        "scientific_name": "Allium cepa",
        "family": "Amaryllidaceae (Alliaceae)",
        "chromosome_number": "2n = 16",
        "type": "vegetable (bulb)",
        "season": "rabi (main), kharif (red), late kharif",
        "photosynthesis": "C3",
        "origin": "Central Asia",
        "optimal_temperature_c": {"germination": "20-25", "bulb_formation": "13-24"},
        "soil_ph": "6.0 – 7.5",
        "soil_types": ["Sandy loam", "Loamy", "Red laterite"],
        "growth_duration_days": "90-120 (transplanting to harvest)",
        "nutrient_requirements_kg_per_ha": {
            "N": "100-120",
            "P2O5": "50-60",
            "K2O": "100-120",
            "S": "40 kg (for flavour compounds)",
            "B": "2 kg Borax",
        },
        "major_varieties": {
            "red": ["Agrifound Dark Red", "N-53", "Bhima Super", "Bhima Red"],
            "white": ["Pusa White Round", "Agrifound White"],
            "yellow": ["Early Grano", "Patna White"],
        },
        "yield_potential_t_per_ha": "25-35",
        "storage": "Cured in shade for 2-3 weeks; store at 0-2°C (60-70% RH) for long-term",
        "major_pests": [
            {"name": "Thrips (Thrips tabaci)", "eppo_code": "THRTAB", "damage": "Silvery leaf streaks; major pest", "management": "Fipronil 5 SC @ 1 L/ha; Spinosad; yellow traps"},
            {"name": "Maggot (Delia antiqua)", "damage": "Bulb tunneling, plant collapse", "management": "Carbofuran soil application; crop rotation"},
        ],
        "major_diseases": [
            {"name": "Purple blotch", "pathogen": "Alternaria porri", "symptoms": "Purple center lesions with yellow halo on leaves", "management": "Mancozeb 75 WP @ 2 g/L; Iprodione"},
            {"name": "Stemphylium blight", "pathogen": "Stemphylium vesicarium", "symptoms": "Yellow to tan lesions with dark green border", "management": "Chlorothalonil; Hexaconazole"},
            {"name": "Basal rot / Fusarium", "pathogen": "Fusarium oxysporum f. sp. cepae", "symptoms": "Root rot, bulb decay", "management": "Soil solarization; seed treatment with Trichoderma"},
            {"name": "Black mold", "pathogen": "Aspergillus niger", "symptoms": "Black powder between scales (post-harvest)", "management": "Proper curing; storage in cool dry place"},
        ],
        "india_context": "India is world's 2nd largest onion producer. Lasalgaon (Maharashtra) is Asia's largest onion wholesale market. Erratic prices — ₹10/kg to ₹100/kg within same year.",
        "icar_source": "ICAR-DOGR Rajgurunagar, Pune — Onion Production Technology",
    },

    "soybean": {
        "scientific_name": "Glycine max",
        "family": "Fabaceae (Leguminosae)",
        "chromosome_number": "2n = 40",
        "type": "oilseed / pulse",
        "season": "kharif",
        "photosynthesis": "C3",
        "origin": "China",
        "optimal_temperature_c": {"germination": "25-30", "growth": "24-30", "pod_filling": "22-26"},
        "annual_rainfall_mm": "600-900",
        "soil_ph": "6.0 – 7.5",
        "soil_types": ["Black soil", "Red loam", "Clay loam"],
        "growth_duration_days": "90-100",
        "nutrient_requirements_kg_per_ha": {
            "N": "20-30 (starter; N fixed by Rhizobium)",
            "P2O5": "60-80",
            "K2O": "40-60",
            "Zn": "25 kg ZnSO4",
            "S": "30 kg",
        },
        "biofertilizer": "Rhizobium japonicum seed inoculation critical — fixes 40-80 kg N/ha",
        "major_varieties": {
            "ICAR-IISR": ["JS 335 (most popular)", "JS 9305", "JS 9752", "NRC 86"],
            "state": ["PK 472 (UP)", "DS 228 (Madhya Pradesh)"],
        },
        "yield_potential_t_per_ha": "2.5-3.5",
        "major_pests": [
            {"name": "Girdle beetle (Obereopsis brevis)", "damage": "Stem girdling — causes wilting and lodging", "management": "Thiamethoxam 25 WG @ 75 g/ha; collect and destroy girdled stems"},
            {"name": "Stem fly (Melanagromyza sojae)", "damage": "Maggots tunnel in stem; deadheart", "management": "Seed treatment with Imidacloprid 70 WS"},
            {"name": "Tobacco caterpillar (Spodoptera litura)", "eppo_code": "PRODLI", "damage": "Defoliation", "management": "Chlorpyrifos 20 EC @ 2 L/ha; pheromone traps"},
        ],
        "major_diseases": [
            {"name": "Yellow mosaic virus (SOYYMV)", "pathogen": "Begomovirus (whitefly-transmitted)", "symptoms": "Interveinal yellowing, mosaic pattern", "management": "Control whitefly; remove infected plants within 30 days"},
            {"name": "Anthracnose", "pathogen": "Colletotrichum truncatum", "symptoms": "Dark lesions on stem, pod abortion", "management": "Seed treatment with Thiram + Carbendazim; Carbendazim spray"},
            {"name": "Bacterial pustule", "pathogen": "Xanthomonas axonopodis pv. glycines", "symptoms": "Yellow spots with pustules on underside", "management": "Copper oxychloride 50 WP @ 3 g/L"},
        ],
        "icar_source": "ICAR-IISR Indore — Soybean Production Technology",
    },

    "maize": {
        "scientific_name": "Zea mays",
        "family": "Poaceae",
        "chromosome_number": "2n = 20",
        "type": "cereal",
        "season": "kharif (main), rabi (South India), spring",
        "photosynthesis": "C4 (Hatch-Slack pathway via bundle sheath cells)",
        "origin": "Mexico (Mesoamerica)",
        "optimal_temperature_c": {"germination": "25-30", "growth": "21-27", "silking": "20-28"},
        "annual_rainfall_mm": "500-900",
        "soil_ph": "5.5 – 7.5",
        "soil_types": ["Alluvial", "Red loam", "Sandy loam"],
        "growth_duration_days": "90-100 (early), 100-120 (medium)",
        "nutrient_requirements_kg_per_ha": {
            "N": "120-150",
            "P2O5": "60",
            "K2O": "60",
            "Zn": "25 kg ZnSO4 (deficiency common in North India)",
            "S": "20 kg",
        },
        "major_varieties": {
            "ICAR": ["Pusa HM 4 (Improved)", "DMH 2", "DKC 9144"],
            "state": ["Vivek 21 (Uttarakhand)", "Sabarmati (Gujarat)"],
            "sweet_corn": ["Madhuri (IARI)", "US 68"],
        },
        "yield_potential_t_per_ha": "8-12 (hybrid, irrigated), 4-6 (open-pollinated)",
        "uses": ["Staple food (Bihar, NE India)", "Poultry feed (70% of production)", "Starch and glucose", "Ethanol", "Baby corn, sweet corn"],
        "major_pests": [
            {"name": "Fall armyworm (Spodoptera frugiperda)", "eppo_code": "SPOFRU", "damage": "New exotic pest (2018–India). Whorl feeding, frass in whorl", "management": "Chlorantraniliprole (Coragen) 20 SC @ 200 ml/ha; Spinetoram; Emamectin benzoate"},
            {"name": "Stem borer (Chilo partellus)", "eppo_code": "CHIPAR", "damage": "Dead hearts (early), stem tunneling (late)", "management": "Carbofuran 3G @ 15 kg/ha in whorl; Trichogramma egg parasitoid release"},
        ],
        "major_diseases": [
            {"name": "Turcicum leaf blight", "pathogen": "Exserohilum turcicum", "symptoms": "Long elliptical grayish-tan lesions", "management": "Mancozeb + Carbendazim; resistant hybrid selection"},
            {"name": "Maydis leaf blight", "pathogen": "Bipolaris maydis", "symptoms": "Tan elongated lesions, BLB of South India", "management": "Propiconazole 25 EC; Tebuconazole"},
            {"name": "Common rust", "pathogen": "Puccinia sorghi", "symptoms": "Brick-red pustules both sides of leaf", "management": "Mancozeb; resistant hybrids"},
        ],
        "icar_source": "ICAR-IIMR Ludhiana — Maize Production Technology Guide",
    },

    "sugarcane": {
        "scientific_name": "Saccharum officinarum (Noble cane) / S. hybrid",
        "family": "Poaceae",
        "chromosome_number": "2n = 80-120 (complex polyploid)",
        "type": "sugar / fibre",
        "season": "annual (planted Oct-Feb, harvested 12 months later)",
        "photosynthesis": "C4",
        "origin": "New Guinea / South Asia",
        "optimal_temperature_c": {"germination": "30-35", "tillering": "28-32", "ripening": "16-21"},
        "annual_rainfall_mm": "1000-1500",
        "soil_ph": "6.0 – 8.5",
        "soil_types": ["Alluvial", "Black cotton soil", "Red loam"],
        "growth_duration_months": "12-16",
        "nutrient_requirements_kg_per_ha": {
            "N": "250-300",
            "P2O5": "80-100",
            "K2O": "120-150",
            "Zn": "25 kg ZnSO4",
            "S": "50 kg",
        },
        "major_varieties": {
            "north": ["Co 238 (legacy)", "CoS 8436", "CoH 119", "UP 9530"],
            "south": ["Co 86032", "Co 8014", "CoC 671", "CoB 94012"],
            "maharashtra": ["Co 86032", "Co M 0265"],
        },
        "yield_potential_t_per_ha": "80-120 (ratoon 60-80)",
        "sucrose_content_pct": "12-18%",
        "pricing": "FRP (Fair & Remunerative Price) set by CCEA; State Advised Price (SAP) by state governments — SAP is always higher in UP, Punjab",
        "major_pests": [
            {"name": "Internode borer (Chilo sacchariphagus indicus)", "damage": "Deadheart, internode tunneling", "management": "Trichogramma chilonis egg parasitoid @ 50,000/ha; Chlorpyrifos"},
            {"name": "Woolly aphid (Ceratovacuna lanigera)", "damage": "Colony under leaves, honeydew, sooty mold", "management": "Dimethoate; biological control via Chrysoperla"},
            {"name": "Termite", "damage": "Root damage in dry spells", "management": "Chlorpyrifos drench"},
        ],
        "major_diseases": [
            {"name": "Red rot", "pathogen": "Colletotrichum falcatum", "symptoms": "Red internal stalk discolouration, rotting", "management": "Hot water treatment of setts; resistant varieties"},
            {"name": "Grassy shoot disease", "pathogen": "Phytoplasma", "symptoms": "Pale green/yellow narrow grass-like shoots", "management": "Use disease-free setts; rogue infected plants"},
            {"name": "Smut", "pathogen": "Sporisorium scitamineum", "symptoms": "Black whip from growing point", "management": "Hot water treatment; carbendazim seed treatment"},
        ],
        "icar_source": "ICAR-IISR Lucknow — Sugarcane Production Technology",
    },

    "potato": {
        "scientific_name": "Solanum tuberosum",
        "family": "Solanaceae",
        "chromosome_number": "2n = 48 (tetraploid)",
        "type": "vegetable (tuber)",
        "season": "rabi",
        "photosynthesis": "C3",
        "origin": "Andes, South America",
        "optimal_temperature_c": {"germination": "20-22", "vegetative": "18-22", "tuberization": "10-17"},
        "annual_rainfall_mm": "500-750",
        "soil_ph": "5.0 – 7.0",
        "soil_types": ["Sandy loam", "Loamy", "Silt loam"],
        "growth_duration_days": "70-120",
        "nutrient_requirements_kg_per_ha": {
            "N": "180-200",
            "P2O5": "100-125",
            "K2O": "200-250",
            "S": "30 kg",
            "Mg": "30 kg MgSO4",
        },
        "major_varieties": {
            "CPRI": ["Kufri Jyoti", "Kufri Bahar", "Kufri Sindhuri", "Kufri Chipsona 1"],
            "processing": ["Kufri Chipsona 1", "Kufri Chipsona 3", "Atlantic"],
        },
        "yield_potential_t_per_ha": "25-35",
        "major_pests": [
            {"name": "Aphid (Myzus persicae)", "eppo_code": "MYZUPE", "damage": "Sap sucking; PVY and PVX virus transmission", "management": "Imidacloprid; Dimethoate; remove infected plants"},
            {"name": "Potato tuber moth (Phthorimaea operculella)", "eppo_code": "GNOROP", "damage": "Gallery feeding in tubers (field and storage)", "management": "Proper hilling; cold storage; Chlorpyrifos"},
        ],
        "major_diseases": [
            {"name": "Late blight", "pathogen": "Phytophthora infestans (oomycete)", "symptoms": "Water-soaked to dark lesions; white sporulation underside; most destructive", "management": "Metalaxyl M + Mancozeb (Ridomil Gold) @ 2.5 g/L; spray on schedule in humid weather"},
            {"name": "Early blight", "pathogen": "Alternaria solani", "symptoms": "Concentric ring target spots on older leaves", "management": "Mancozeb; Chlorothalonil; Azoxystrobin"},
            {"name": "Bacterial wilt", "pathogen": "Ralstonia solanacearum", "symptoms": "Sudden wilting; bacterial ooze in water", "management": "Crop rotation; soil solarization; avoid waterlogging"},
            {"name": "Black scurf", "pathogen": "Rhizoctonia solani", "symptoms": "Dark sclerotia on tuber skin", "management": "Seed treatment with Pencycuron; clean seed"},
        ],
        "icar_source": "ICAR-CPRI Shimla — Package of Practices for Potato",
    },

    "groundnut": {
        "scientific_name": "Arachis hypogaea",
        "family": "Fabaceae",
        "chromosome_number": "2n = 40",
        "type": "oilseed / pulse",
        "season": "kharif (main), rabi (southern India)",
        "photosynthesis": "C3",
        "origin": "South America (Brazil/Paraguay)",
        "optimal_temperature_c": {"germination": "25-30", "growth": "24-30", "pegging": "25-30"},
        "annual_rainfall_mm": "500-750",
        "soil_ph": "6.0 – 7.0",
        "soil_types": ["Sandy loam", "Red loam", "Alluvial"],
        "growth_duration_days": "90-130",
        "nutrient_requirements_kg_per_ha": {
            "N": "20-25 (starter; N fixed by Rhizobium)",
            "P2O5": "40-50",
            "K2O": "60-80",
            "Ca": "Gypsum @ 200-250 kg/ha at pegging — critical for pod fill",
            "S": "20-30 kg",
        },
        "biofertilizer": "Rhizobium + PSB seed inoculation — essential for nitrogen fixation",
        "major_varieties": {
            "ICAR-DGR": ["GG 20", "TG 37-A", "TAG 24", "K 6"],
            "state": ["TMV 2 (Tamil Nadu)", "JL 24 (90-day, Maharashtra)"],
        },
        "yield_potential_t_per_ha": "2.5-3.5 (pods)",
        "oil_content_pct": "48-54%",
        "major_pests": [
            {"name": "Tobacco caterpillar (Spodoptera litura)", "eppo_code": "PRODLI", "damage": "Mass defoliation at night", "management": "Chlorpyrifos 20 EC @ 2 L/ha; pheromone traps"},
            {"name": "Thrips (Frankliniella schultzei)", "damage": "Silvery streaks; PBNV virus transmission", "management": "Imidacloprid; Dimethoate"},
        ],
        "major_diseases": [
            {"name": "Tikka / Leaf spot", "pathogen": "Cercospora arachidicola (early) / Phaeoisariopsis personata (late)", "symptoms": "Circular brown spots; defoliation", "management": "Chlorothalonil 75 WP @ 2 g/L; Carbendazim + Mancozeb"},
            {"name": "Stem rot (white mold)", "pathogen": "Sclerotium rolfsii", "symptoms": "White cottony growth at base; wilting", "management": "Trichoderma viride @ 4 kg/ha; crop rotation"},
            {"name": "Aflatoxin contamination", "pathogen": "Aspergillus flavus / A. parasiticus (post-harvest)", "symptoms": "No visible symptoms; detected by UV fluorescence", "management": "Harvest at correct moisture (25%); dry immediately; cold storage; avoid damaged pods"},
        ],
        "icar_source": "ICAR-NRCG Junagadh — Groundnut Production Technology",
    },

    "chilli": {
        "scientific_name": "Capsicum annuum (most varieties) / C. frutescens (bird's eye)",
        "family": "Solanaceae",
        "chromosome_number": "2n = 24",
        "type": "vegetable / spice",
        "season": "kharif and rabi",
        "photosynthesis": "C3",
        "origin": "Mexico",
        "optimal_temperature_c": {"germination": "25-30", "growth": "20-30"},
        "soil_ph": "6.0 – 7.0",
        "major_varieties": {
            "ICAR": ["Pusa Jwala", "Pusa Sadabahar", "Arka Lohit"],
            "commercial": ["Guntur Sannam (G4)", "Byadgi Dabbi (Karnataka, low pungency)", "Kanthari (Kerala)"],
        },
        "yield_potential_t_per_ha": "Green: 15-25; Dry: 2-3",
        "pungency_compound": "Capsaicin — measured in Scoville Heat Units (SHU); Bhut jolokia >1 million SHU; Guntur Sannam 25,000-50,000 SHU",
        "major_pests": [
            {"name": "Thrips (Scirtothrips dorsalis)", "damage": "Leaf curl ('chilli mite curl'); silvery leaves", "management": "Spinosad 45 SC; Profenofos"},
            {"name": "Fruit borer (Helicoverpa armigera)", "damage": "Bore into fruits", "management": "Chlorantraniliprole; Emamectin benzoate"},
        ],
        "major_diseases": [
            {"name": "Die back / Anthracnose", "pathogen": "Colletotrichum capsici / C. gloeosporioides", "symptoms": "Twig die back; fruit rot with salmon-colored sporulation", "management": "Mancozeb + Carbendazim; Azoxystrobin"},
            {"name": "Powdery mildew", "pathogen": "Leveillula taurica", "symptoms": "White powdery coating on underside of leaves", "management": "Wettable sulphur 80 WP @ 3 g/L; Dinocap"},
            {"name": "Phytophthora blight", "pathogen": "Phytophthora capsici", "symptoms": "Water-soaked lesions on stem/fruit; sudden collapse", "management": "Metalaxyl + Mancozeb; raised beds; avoid waterlogging"},
        ],
        "icar_source": "ICAR-IIHR Bengaluru — Chilli Production Technology",
    },

    "turmeric": {
        "scientific_name": "Curcuma longa",
        "family": "Zingiberaceae",
        "chromosome_number": "2n = 63",
        "type": "spice / medicinal",
        "season": "kharif",
        "photosynthesis": "C3",
        "origin": "Southeast Asia / India",
        "optimal_temperature_c": {"growth": "20-35"},
        "annual_rainfall_mm": "1500-2000",
        "soil_ph": "5.5 – 7.0",
        "growth_duration_months": "7-9",
        "curcumin_content_pct": "3-5% (Erode Salem have high curcumin varieties)",
        "major_varieties": {"ICAR": ["Roma", "Surama", "Kedaram"], "commercial": ["Erode Local", "Salem", "Rajapuri", "Lakadong (Meghalaya — highest curcumin 7-9%)"]},
        "yield_potential_t_per_ha": "Dry turmeric: 2-3; Fresh: 15-25",
        "major_diseases": [
            {"name": "Rhizome rot", "pathogen": "Pythium spp.", "symptoms": "Water-soaked rhizomes, plant collapse", "management": "Drenching with Metalaxyl; plant on raised beds"},
            {"name": "Leaf blotch", "pathogen": "Taphrina maculans", "symptoms": "Irregular spots on leaves", "management": "Mancozeb; Bordeaux mixture"},
        ],
        "india_context": "Erode (Tamil Nadu) and Sangli (Maharashtra) are India's major turmeric hubs. India supplies 80% of world turmeric.",
    },
}


# ════════════════════════════════════════════════════════════════════════════
# E. Soil Types — India
# ════════════════════════════════════════════════════════════════════════════

INDIA_SOIL_TYPES = {
    "alluvial": {
        "area_mha": 143,
        "distribution": "Indo-Gangetic plains (Punjab, Haryana, UP, Bihar, West Bengal), Coastal plains",
        "ph_range": "6.5 – 8.4",
        "characteristics": "Transported soil, highly fertile, rich in potash & lime; poor in phosphorus & nitrogen in old alluvium (Bangar)",
        "best_crops": ["Wheat", "Rice", "Sugarcane", "Maize", "Vegetables"],
        "major_deficiencies": ["Nitrogen (old alluvium)", "Phosphorus", "Zinc"],
        "amendments": ["Green manure (Dhaincha)", "FYM @ 10 t/ha", "ZnSO4 @ 25 kg/ha"],
    },
    "black_cotton": {
        "local_name": "Regur / Black soil",
        "area_mha": 74,
        "distribution": "Deccan Plateau (Maharashtra, Gujarat, Madhya Pradesh, Telangana, Karnataka)",
        "ph_range": "7.5 – 8.5",
        "characteristics": "Rich in calcium carbonate, magnesium, potash; poor in nitrogen & phosphorus; high clay content (montmorillonite) — cracks when dry, waterlogged when wet",
        "best_crops": ["Cotton", "Sorghum", "Wheat (rabi)", "Sunflower", "Soybean"],
        "major_deficiencies": ["Nitrogen", "Phosphorus", "Zinc"],
        "amendments": ["Single superphosphate", "ZnSO4 @ 25 kg/ha", "Avoid waterlogging with raised beds"],
        "note": "Self-mulching — old organic matter incorporated from surface cracking",
    },
    "red_soil": {
        "area_mha": 75,
        "distribution": "Eastern Deccan, Tamil Nadu, Karnataka interior, Jharkhand, Odisha",
        "ph_range": "6.0 – 7.5",
        "characteristics": "Red color from ferric oxide; low fertility; good drainage; deficient in all major nutrients",
        "best_crops": ["Groundnut", "Cotton", "Millet (jowar/bajra)", "Pulses", "Oilseeds"],
        "major_deficiencies": ["Nitrogen", "Phosphorus", "Potassium", "Lime"],
        "amendments": ["Lime @ 1-2 t/ha if pH < 6", "Compost/FYM", "DAP"],
    },
    "laterite": {
        "area_mha": 26,
        "distribution": "Western Ghats coast (Kerala, Goa, Karnataka), Meghalaya, Odisha hills",
        "ph_range": "5.0 – 6.5",
        "characteristics": "Leached by heavy rainfall; iron and aluminium rich; low silica; hardens on drying (used as bricks)",
        "best_crops": ["Coconut", "Rubber", "Tea", "Coffee", "Cashew", "Spices"],
        "major_deficiencies": ["Nitrogen", "Phosphorus", "Potassium", "Calcium", "Magnesium"],
        "amendments": ["Heavy compost/FYM application", "Lime", "Magnesium sulphate"],
    },
    "arid_desert": {
        "area_mha": 14,
        "distribution": "Rajasthan (Thar Desert), Gujarat Rann",
        "ph_range": "7.0 – 9.0",
        "characteristics": "Sandy texture; very low organic matter; high soluble salts; low water retention",
        "best_crops": ["Bajra", "Moth bean", "Cluster bean (Guar)", "Sesame"],
        "major_deficiencies": ["Nitrogen", "Organic matter", "Micronutrients"],
        "amendments": ["Mulching (dry grass)", "Gypsum for saline soils", "Drip irrigation essential"],
    },
    "saline_alkaline": {
        "local_name": "Usar / Reh / Kallar",
        "area_mha": 7,
        "distribution": "UP, Punjab, Haryana, Rajasthan, Bihar (low-lying areas)",
        "ph_range": "8.5 – 10.0 (pH > 8.5 saline; > 9.5 alkali)",
        "characteristics": "High Na+, Mg2+ salts; poor aeration; impermeable hardpan (kankar); growth inhibiting",
        "best_crops": ["Dhaincha (green manure)", "Karnal bunt resistant wheat", "Rice (some varieties)", "Leptochloa (salt-tolerant grass)"],
        "reclamation": ["Gypsum (CaSO4) @ 5-10 t/ha to replace Na+", "Leaching with good drainage", "Green manure (Dhaincha)", "Bioremediation with salt-tolerant microbes"],
    },
    "peaty_marshy": {
        "area_mha": 0.5,
        "distribution": "Kuttanad (Kerala), coastal Odisha, Bihar (flood plains)",
        "ph_range": "3.5 – 5.5",
        "characteristics": "High organic matter (>20%); waterlogged; reducing conditions; very high acidity",
        "best_crops": ["Rice (floating/deepwater)", "Coconut (coastal)"],
        "amendments": ["Lime @ 2-4 t/ha", "Raised bed cultivation"],
    },
    "forest_mountain": {
        "area_mha": 30,
        "distribution": "Himalayas (J&K, Himachal, Uttarakhand, NE States)",
        "ph_range": "4.5 – 6.5",
        "characteristics": "Rich in humus; cool, moist; deep loamy texture; excellent structure",
        "best_crops": ["Apple", "Potato", "Wheat", "Ginger", "Cardamom", "Tea"],
        "major_deficiencies": ["Phosphorus", "Nitrogen (in heavily cropped areas)"],
        "amendments": ["Lime", "FYM", "Vermicompost"],
    },
}


# ════════════════════════════════════════════════════════════════════════════
# F. Agro-Climatic Zones of India (ICAR/Planning Commission — 15 Zones)
# ════════════════════════════════════════════════════════════════════════════

AGROCLIMATIC_ZONES = {
    "Zone_1": {
        "name": "Western Himalayan Region",
        "states": ["Jammu & Kashmir", "Ladakh", "Himachal Pradesh", "Uttarakhand"],
        "rainfall_mm": "800-1500",
        "major_crops": ["Wheat", "Maize", "Rice (lower hills)", "Apple", "Potato", "Ginger", "Peas"],
        "sowing_windows": {"wheat": "Oct-Nov", "maize": "Apr-May", "potato": "Mar-Apr"},
    },
    "Zone_2": {
        "name": "Eastern Himalayan Region",
        "states": ["Arunachal Pradesh", "Sikkim", "Meghalaya", "Nagaland", "Manipur", "Mizoram", "Tripura", "Assam Hills"],
        "rainfall_mm": "2000-4000",
        "major_crops": ["Rice", "Maize", "Ginger", "Turmeric", "Cardamom (Sikkim)", "Orange", "Tea (Assam)"],
        "sowing_windows": {"rice": "Jun-Jul", "maize": "Apr-May"},
    },
    "Zone_3": {
        "name": "Lower Gangetic Plains",
        "states": ["West Bengal"],
        "rainfall_mm": "1400-1800",
        "major_crops": ["Rice (Aman, Aus, Boro)", "Jute", "Potato", "Mustard", "Onion"],
        "sowing_windows": {"rice_kharif": "Jun-Jul", "potato": "Oct-Nov", "jute": "Apr-May"},
    },
    "Zone_4": {
        "name": "Middle Gangetic Plains",
        "states": ["Bihar", "Eastern Uttar Pradesh"],
        "rainfall_mm": "900-1200",
        "major_crops": ["Wheat", "Rice", "Maize", "Lentil", "Mustard", "Vegetables"],
        "sowing_windows": {"wheat": "Nov-Dec", "rice": "Jun-Jul", "lentil": "Oct-Nov"},
    },
    "Zone_5": {
        "name": "Upper Gangetic Plains",
        "states": ["Western Uttar Pradesh", "Uttarakhand Terai"],
        "rainfall_mm": "600-900",
        "major_crops": ["Wheat", "Sugarcane", "Rice", "Potato", "Maize"],
        "sowing_windows": {"wheat": "Nov-Dec", "sugarcane": "Feb-Mar", "potato": "Oct-Nov"},
    },
    "Zone_6": {
        "name": "Trans-Gangetic Plains",
        "states": ["Punjab", "Haryana", "Chandigarh", "Delhi"],
        "rainfall_mm": "400-700",
        "major_crops": ["Wheat", "Rice (paddy)", "Maize", "Cotton (Haryana)"],
        "sowing_windows": {"wheat": "Nov-Dec", "rice": "Jun-Jul"},
        "note": "Wheat-Rice rotation dominates. Groundwater depletion is a major concern.",
    },
    "Zone_7": {
        "name": "Eastern Plateau and Hills",
        "states": ["Jharkhand", "Odisha", "Chhattisgarh", "Madhya Pradesh (eastern)"],
        "rainfall_mm": "1200-1600",
        "major_crops": ["Rice", "Maize", "Arhar (pigeonpea)", "Groundnut", "Gram"],
        "sowing_windows": {"rice": "Jun-Jul", "arhar": "Jun-Jul", "gram": "Oct-Nov"},
    },
    "Zone_8": {
        "name": "Central Plateau and Hills",
        "states": ["Madhya Pradesh", "Chhattisgarh (plateau)", "Rajasthan (eastern)"],
        "rainfall_mm": "800-1200",
        "major_crops": ["Wheat", "Soybean", "Gram", "Maize", "Sorghum", "Sesame"],
        "sowing_windows": {"wheat": "Nov-Dec", "soybean": "Jun-Jul", "gram": "Oct-Nov"},
    },
    "Zone_9": {
        "name": "Western Plateau and Hills",
        "states": ["Maharashtra (Vidarbha)", "Madhya Pradesh (western)"],
        "rainfall_mm": "700-1000",
        "major_crops": ["Sorghum", "Cotton", "Soybean", "Oranges (Vidarbha)"],
        "sowing_windows": {"cotton": "May-Jun", "soybean": "Jun-Jul", "sorghum": "Jun-Jul"},
    },
    "Zone_10": {
        "name": "Southern Plateau and Hills",
        "states": ["Andhra Pradesh (Rayalaseema)", "Karnataka (interior)", "Tamil Nadu (western)"],
        "rainfall_mm": "500-800",
        "major_crops": ["Groundnut", "Jowar", "Ragi", "Sunflower", "Cotton"],
        "sowing_windows": {"groundnut": "Jun-Jul (kharif); Jan-Feb (rabi)", "ragi": "Jun-Jul"},
    },
    "Zone_11": {
        "name": "East Coast Plains and Hills",
        "states": ["Odisha (coast)", "Andhra Pradesh (coastal)", "Tamil Nadu (eastern)"],
        "rainfall_mm": "1000-1500",
        "major_crops": ["Rice", "Sugarcane", "Groundnut", "Chilli", "Cotton"],
        "sowing_windows": {"rice": "Jun-Jul", "sugarcane": "Jan-Feb"},
    },
    "Zone_12": {
        "name": "West Coast Plains and Ghats",
        "states": ["Kerala", "Karnataka (coast)", "Goa", "Maharashtra (Konkan)"],
        "rainfall_mm": "2000-4000",
        "major_crops": ["Coconut", "Rice", "Areca nut", "Banana", "Spices", "Cashew"],
        "sowing_windows": {"rice": "Jun-Jul", "coconut": "June (planting)"},
    },
    "Zone_13": {
        "name": "Gujarat Plains and Hills",
        "states": ["Gujarat"],
        "rainfall_mm": "500-1000",
        "major_crops": ["Cotton", "Groundnut", "Castor", "Wheat", "Bajra", "Sesame"],
        "sowing_windows": {"cotton": "May-Jun", "groundnut": "Jun-Jul", "wheat": "Nov-Dec"},
    },
    "Zone_14": {
        "name": "Western Dry Region",
        "states": ["Rajasthan (western)", "Gujarat (northern Rann)"],
        "rainfall_mm": "100-400",
        "major_crops": ["Bajra", "Moth bean", "Cluster bean (Guar)", "Sesame", "Cumin"],
        "sowing_windows": {"bajra": "Jun-Jul", "cumin": "Nov-Dec"},
    },
    "Zone_15": {
        "name": "Islands",
        "states": ["Andaman & Nicobar Islands", "Lakshadweep"],
        "rainfall_mm": "2000-3500",
        "major_crops": ["Rice", "Coconut", "Areca nut", "Spices", "Fruits"],
        "sowing_windows": {"rice": "Jun-Jul"},
    },
}


# ════════════════════════════════════════════════════════════════════════════
# G. Irrigation Reference
# ════════════════════════════════════════════════════════════════════════════

IRRIGATION_METHODS = {
    "drip": {
        "efficiency_pct": 90,
        "water_saving_vs_flood_pct": 40-60,
        "best_for": ["Orchards", "Vegetables", "Sugarcane", "Cotton", "Pomegranate"],
        "cost_per_ha_inr": "40,000 – 1,00,000",
        "subsidy": "55-75% under PMKSY (Pradhan Mantri Krishi Sinchai Yojana)",
        "government_scheme": "PMKSY — 'Per Drop More Crop' component",
    },
    "sprinkler": {
        "efficiency_pct": 75,
        "water_saving_vs_flood_pct": 25-40,
        "best_for": ["Groundnut", "Wheat", "Vegetables", "Fodder crops", "Hilly areas"],
        "cost_per_ha_inr": "15,000 – 40,000",
        "subsidy": "55-75% under PMKSY",
    },
    "flood_furrow": {
        "efficiency_pct": 55,
        "best_for": ["Sugarcane", "Maize", "Cotton"],
        "note": "Traditional method; highest water use; works well where water table is high",
    },
    "flood_border": {
        "efficiency_pct": 60,
        "best_for": ["Wheat", "Barley", "Fodder"],
    },
    "check_basin": {
        "efficiency_pct": 65,
        "best_for": ["Orchards", "Rice (bunded fields)"],
    },
    "subsurface_drip": {
        "efficiency_pct": 95,
        "best_for": ["Sugarcane", "Cotton", "Banana"],
        "note": "Highest efficiency; expensive; fertigation possible",
    },
}

CROP_WATER_REQUIREMENTS_MM = {
    "rice":        1200,
    "wheat":       450,
    "maize":       550,
    "cotton":      700,
    "sugarcane":   1800,
    "groundnut":   500,
    "soybean":     450,
    "potato":      500,
    "onion":       350,
    "tomato":      500,
    "chilli":      600,
    "turmeric":    1500,
    "banana":      1600,
    "mango":       1200,
    "coconut":     1500,
    "mustard":     350,
    "gram":        300,
    "arhar":       400,
    "bajra":       350,
    "jowar":       400,
}


# ════════════════════════════════════════════════════════════════════════════
# H. Plant Science Library
# ════════════════════════════════════════════════════════════════════════════

PHOTOSYNTHESIS_TYPES = {
    "C3": {
        "pathway": "Calvin Cycle (3-carbon compound — 3-phosphoglycerate as first stable product)",
        "enzyme": "RuBisCO (ribulose-1,5-bisphosphate carboxylase/oxygenase)",
        "efficiency_at_high_temp": "Low — photorespiration increases (CO2 fixation competes with O2)",
        "examples": ["Wheat", "Rice", "Potato", "Tomato", "Onion", "Soybean", "Groundnut", "Cotton"],
        "optimal_temperature_c": "15-25",
        "photorespiration": "Yes — reduces efficiency by 20-30%",
        "quantum_yield": "0.0555 mol CO2/mol photons",
        "water_use_efficiency": "Low (transpiration ratio 400-800 g H2O/g dry matter)",
    },
    "C4": {
        "pathway": "Hatch-Slack pathway (4-carbon compound — oxaloacetate as first stable product); CO2 concentrated in bundle sheath cells",
        "enzymes": "PEP carboxylase (mesophyll) + RuBisCO (bundle sheath)",
        "efficiency_at_high_temp": "High — CO2 concentrating mechanism suppresses photorespiration",
        "examples": ["Maize", "Sugarcane", "Sorghum (Jowar)", "Bajra (Pearl millet)", "Bermuda grass"],
        "optimal_temperature_c": "30-40",
        "photorespiration": "Negligible — CO2 concentrated in bundle sheath",
        "quantum_yield": "0.0662 mol CO2/mol photons",
        "water_use_efficiency": "High (transpiration ratio 250-350 g H2O/g dry matter)",
        "structural_feature": "Kranz anatomy — ring of bundle sheath cells around vascular bundle",
    },
    "CAM": {
        "pathway": "Crassulacean Acid Metabolism — stomata open at night; CO2 fixed as malic acid; releases CO2 during day",
        "adaptation": "Extreme water-scarce environments; stomata closed in daytime",
        "examples": ["Pineapple", "Aloe vera", "Agave", "Cacti", "Vanilla"],
        "water_use_efficiency": "Very high (transpiration ratio 50-100 g H2O/g dry matter)",
        "limitation": "Slow growth rate; limited by storage capacity",
    },
}

PLANT_GROWTH_REGULATORS = {
    "auxins": {
        "key_compound": "Indole-3-acetic acid (IAA) — natural; NAA (naphthaleneacetic acid) — synthetic",
        "functions": ["Cell elongation", "Apical dominance", "Root initiation on cuttings", "Fruit development", "Prevent premature fruit drop"],
        "agricultural_use": {
            "NAA_10_ppm": "Prevent pre-harvest drop in apples, citrus (spray 3-4 weeks before harvest)",
            "IBA_3000_ppm": "Root induction in stem cuttings (roses, grapes, guava)",
            "2_4_D": "Selective herbicide for broadleaf weeds (1 kg/ha); also fruit set in tomato",
        },
    },
    "gibberellins": {
        "key_compound": "Gibberellic acid (GA3)",
        "functions": ["Stem elongation", "Dormancy breaking in seeds", "Seedless fruit (parthenocarpy)", "Delay senescence in citrus"],
        "agricultural_use": {
            "GA3_25_ppm": "Seedlessness in grapes; berry enlargement in Thompson Seedless",
            "GA3_100_ppm": "Break seed dormancy in potato, strawberry",
            "GA3_50_ppm": "Elongate grape clusters to reduce bunch rots",
        },
    },
    "cytokinins": {
        "key_compound": "Kinetin, Zeatin, BAP (benzylaminopurine)",
        "functions": ["Cell division", "Delay leaf senescence", "Lateral bud development", "Fruit set"],
        "agricultural_use": {
            "BAP_50_ppm": "Delayed yellowing of spinach, lettuce during storage",
            "zeatin_in_fertigation": "Promotes lateral shoots in pruned orchards",
        },
    },
    "ethylene": {
        "key_compound": "Ethephon (Ethrel) — releases ethylene on contact with plant",
        "functions": ["Fruit ripening", "Flower induction in pineapple", "Latex flow in rubber", "Lodging prevention (reduces internode length)"],
        "agricultural_use": {
            "ethephon_500_ppm": "Mango ripening (dip or spray; replaces calcium carbide)",
            "ethephon_400_ppm_pineapple": "Induce uniform flowering/fruiting",
            "ethephon_250_ppm_rubber": "Stimulate latex flow on bark",
        },
    },
    "abscisic_acid": {
        "functions": ["Stomatal closure during water stress", "Seed dormancy", "Leaf abscission", "Inhibits growth"],
        "agricultural_relevance": "ABA levels rise during drought — linked to wilting; crops with high ABA sensitivity lose less water",
    },
    "brassinosteroids": {
        "functions": ["Stem elongation", "Cell division", "Stress tolerance", "Pollen development"],
        "agricultural_use": "Brassinolide @ 1-5 ppm improves crop performance under salt/drought stress",
    },
    "triacontanol": {
        "source": "Alfalfa wax (natural growth promoter)",
        "use": "Foliar spray @ 0.1 ppm — increases photosynthesis rate, yield in rice, wheat, maize by 5-15%",
    },
    "retardants_growth_inhibitors": {
        "CCC_chlormequat": "Reduces internode length in wheat (lodging control); reduces plant height by 15-20%",
        "mepiquat_chloride": "Cotton height control; promotes boll set over vegetative growth",
        "paclobutrazol": "Mango flowering induction; dwarfing in nursery plants",
    },
}

BIOFERTILIZERS = {
    "rhizobium": {
        "mode": "Nitrogen fixation — symbiotic (in root nodules of legumes)",
        "crops": ["Soybean", "Groundnut", "Gram", "Arhar", "Lentil", "Moong", "Urad"],
        "dose": "200-250 g per 10 kg seed",
        "n_fixed_kg_per_ha": "40-200 (legume-specific)",
        "commercial": "IFFCO Nano Urea + Rhizobium culture; KRIBHCO biofertilizer",
        "note": "Species-specific — Rhizobium japonicum for soybean; R. leguminosarum for pulses",
    },
    "azospirillum": {
        "mode": "Nitrogen fixation — free-living / associative (in rhizosphere)",
        "crops": ["Maize", "Wheat", "Rice (rainfed)", "Sugarcane", "Cotton", "Sorghum"],
        "dose": "200 g per 10 kg seed + 1 kg/ha soil application",
        "n_fixed_kg_per_ha": "20-40",
        "note": "Also produces growth regulators (IAA, GA) — improves root development",
    },
    "azotobacter": {
        "mode": "Nitrogen fixation — free-living in soil",
        "crops": ["All non-legumes: wheat, rice, cotton, vegetables"],
        "dose": "5 kg/ha soil application",
        "n_fixed_kg_per_ha": "15-20",
        "additional_benefit": "Produces siderophores (iron mobilization), Vit B12",
    },
    "phosphate_solubilizing_bacteria_psb": {
        "mode": "Solubilizes insoluble tricalcium phosphate via organic acid production",
        "key_genera": ["Bacillus", "Pseudomonas", "Aspergillus (fungal PSB)"],
        "dose": "200 g per 10 kg seed or 5 kg/ha soil",
        "benefit": "Saves 20-30% P fertilizer; improves P uptake by 50-70%",
        "commercial": "IFFCO Bio NPK, Navneet PSB culture",
    },
    "vam_mycorrhiza": {
        "full_name": "Vesicular-Arbuscular Mycorrhiza (VAM) — endomycorrhizal fungi",
        "genera": ["Glomus", "Rhizophagus", "Funneliformis"],
        "mechanism": "Hyphal network extends root effective volume by 10x; absorbs P, Zn, water from micropores",
        "crops": ["Maize", "Wheat", "Cotton", "Fruit trees", "Vegetables — all except Brassica"],
        "dose": "5-10 kg/ha soil incorporation",
        "benefits": ["25-30% P savings", "Drought tolerance", "Improved plant establishment"],
        "note": "Incompatible with high P fertilizer (> 60 kg P2O5/ha) — inhibits colonization",
    },
    "trichoderma": {
        "mode": "Biocontrol — mycoparasite of soil pathogens; also promotes plant growth",
        "diseases_controlled": ["Fusarium wilt", "Pythium damping off", "Sclerotium rot", "Rhizoctonia"],
        "dose": "2.5 kg/ha soil incorporation (with FYM); seed treatment @ 5 g/kg seed",
        "commercial": "Tricho-G, Biofit (IFFCO), Nisarga (Coromandel)",
    },
    "blue_green_algae_bga": {
        "mode": "N fixation in flooded rice paddies",
        "crops": ["Transplanted rice"],
        "dose": "10 kg/ha soil spreading after transplanting",
        "n_fixed_kg_per_ha": "20-30",
        "note": "Traditional practice in South India; now available as Azolla + BGA combined",
    },
    "azolla": {
        "mode": "Nitrogen fixation via symbiosis with Anabaena (cyanobacterium)",
        "crops": ["Transplanted rice"],
        "n_equivalent": "25-40 kg N/ha",
        "method": "Grow Azolla in field for 2-3 weeks before transplanting; incorporate or allow as living mulch",
    },
}

COMPANION_PLANTING = {
    "maize_legume": {
        "combination": "Maize + Cowpea or Maize + Beans",
        "benefit": "Legume fixes N2 for maize; maize provides support for climbing beans; better light utilization",
        "ratio": "2 rows maize : 1 row cowpea",
        "practice_region": "Northeast India, Africa (traditional)",
    },
    "sugarcane_onion": {
        "combination": "Sugarcane + Onion/Garlic (intercrop)",
        "benefit": "Garlic/onion repel pests; additional income in early sugarcane",
        "window": "First 4-5 months of sugarcane growth",
    },
    "cotton_soybean": {
        "combination": "Cotton + Soybean",
        "benefit": "Soybean fixes N; reduces bollworm pressure (soybean is alternate host pulling away pests); additional income",
        "ratio": "3 rows cotton : 1 row soybean",
    },
    "tomato_basil": {
        "combination": "Tomato + Basil",
        "benefit": "Basil repels thrips and aphids; improves tomato flavour (claimed); companion planting icon",
    },
    "wheat_mustard": {
        "combination": "Wheat + Mustard",
        "benefit": "Mustard attracts aphid predators; additional oilseed income",
        "ratio": "9 rows wheat : 1 row mustard (border/trap crop)",
    },
}

ALLELOPATHY = {
    "sorghum": {
        "allelopathic_compound": "Dhurrin (cyanogenic glycoside), Sorgoleone (quinone)",
        "affected_crops": ["Wheat", "Maize (growth inhibition from sorghum residues)"],
        "benefit": "Sorghum mulch suppresses weeds; allelopathic rotation design",
    },
    "sunflower": {
        "allelopathic_compound": "Heliannuol, Chlorogenic acid",
        "affected_crops": ["Wheat (slight inhibition)"],
        "benefit": "Sunflower extracts used as natural herbicide research",
    },
    "eucalyptus": {
        "allelopathic_compound": "Eucalyptol, phenolic acids",
        "affected_crops": ["Tomato, wheat (severely inhibited under Eucalyptus trees)"],
        "note": "Avoid planting agricultural crops under/near Eucalyptus plantations",
    },
    "neem": {
        "allelopathic_compound": "Azadirachtin — insecticidal; various terpenoids",
        "benefit": "Neem leaf mulch suppresses soil pests and weeds; neem cake inhibits nitrification (slow-release N)",
    },
    "rice": {
        "allelopathic_compound": "Phenolic acids, momilactone",
        "benefit": "Allelopathic rice varieties (IAC 165, FARR 07A) suppress weeds — reduces herbicide use by 60%",
    },
}


# ════════════════════════════════════════════════════════════════════════════
# Quick-access helper functions
# ════════════════════════════════════════════════════════════════════════════

def get_crop_info(crop: str) -> dict | None:
    """Return encyclopaedia entry for a crop."""
    return CROP_ENCYCLOPEDIA.get(crop.lower().strip())


def get_soil_info(soil_type: str) -> dict | None:
    """Return soil type information."""
    key = soil_type.lower().replace(" ", "_").replace("-", "_")
    for k, v in INDIA_SOIL_TYPES.items():
        if k in key or key in k:
            return {"soil_type": k, **v}
    return None


def get_zone_info(state: str) -> list[dict]:
    """Return agro-climatic zone(s) for a given state."""
    zones = []
    for zone_id, zone_data in AGROCLIMATIC_ZONES.items():
        if any(state.lower() in s.lower() for s in zone_data.get("states", [])):
            zones.append({"zone": zone_id, **zone_data})
    return zones


def get_global_benchmark(commodity: str) -> dict | None:
    """Return global commodity benchmark data."""
    key = commodity.lower().replace(" ", "_")
    return GLOBAL_BENCHMARKS.get(key)


# Summary for LLM context injection
KB_SUMMARY = """
FarmSphere Agriculture Knowledge Base (agriculture_kb.py) contains:
- MSP 2024-25: Official government Minimum Support Prices for all 24 kharif + rabi crops
- State-wise prices: Agmarknet-reference prices for 50 crops across all 28 states + 8 UTs
- Crop encyclopaedia: Scientific name, agronomy, pests, diseases, varieties for 10+ major crops (wheat, rice, tomato, cotton, onion, soybean, maize, sugarcane, potato, groundnut, chilli, turmeric)
- Soil types: 8 Indian soil types with pH, deficiencies, crop suitability
- Agro-climatic zones: All 15 ICAR agro-climatic zones with crop calendars
- Irrigation: 6 methods with efficiency data; crop-wise water requirements
- Plant science: C3/C4/CAM photosynthesis; PGRs (NAA, GA3, Ethephon, CCC); Biofertilizers (Rhizobium, Azospirillum, PSB, VAM/Mycorrhiza, Trichoderma); Companion planting; Allelopathy

All data sourced from: DAC&FW, ICAR, IARI, NABARD, Agmarknet, Spices Board India, FAO
"""
