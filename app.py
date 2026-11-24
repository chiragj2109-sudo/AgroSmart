import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AgriSmart AI", page_icon="🌱", layout="wide")

CROPS = {
    "Rice": {"N": (60, 100), "P": (30, 60), "K": (30, 60), "ph": (5.5, 7.0), "temp": (20, 35), "humidity": (70, 90), "rainfall": (1000, 2500), "moisture": (60, 90), "water": "Very high"},
    "Wheat": {"N": (50, 100), "P": (30, 60), "K": (20, 50), "ph": (6.0, 7.5), "temp": (10, 25), "humidity": (40, 70), "rainfall": (300, 900), "moisture": (30, 60), "water": "Medium"},
    "Maize": {"N": (60, 120), "P": (35, 70), "K": (25, 60), "ph": (5.5, 7.5), "temp": (18, 32), "humidity": (50, 80), "rainfall": (500, 1200), "moisture": (35, 65), "water": "Medium"},
    "Cotton": {"N": (50, 100), "P": (20, 50), "K": (30, 70), "ph": (5.8, 8.0), "temp": (21, 35), "humidity": (40, 70), "rainfall": (500, 1000), "moisture": (30, 60), "water": "Medium"},
    "Sugarcane": {"N": (80, 150), "P": (30, 70), "K": (40, 100), "ph": (6.0, 7.5), "temp": (20, 35), "humidity": (60, 85), "rainfall": (1000, 2000), "moisture": (55, 85), "water": "Very high"},
    "Chickpea": {"N": (20, 50), "P": (40, 80), "K": (20, 50), "ph": (6.0, 8.0), "temp": (15, 30), "humidity": (30, 60), "rainfall": (300, 800), "moisture": (25, 55), "water": "Low"},
    "Lentil": {"N": (20, 50), "P": (35, 70), "K": (20, 50), "ph": (6.0, 8.0), "temp": (15, 28), "humidity": (30, 65), "rainfall": (300, 750), "moisture": (25, 55), "water": "Low"},
    "Groundnut": {"N": (20, 50), "P": (30, 60), "K": (30, 70), "ph": (5.5, 7.0), "temp": (22, 32), "humidity": (50, 75), "rainfall": (500, 1200), "moisture": (35, 65), "water": "Medium"},
    "Millet": {"N": (20, 60), "P": (20, 50), "K": (15, 45), "ph": (5.5, 8.0), "temp": (25, 38), "humidity": (20, 60), "rainfall": (200, 700), "moisture": (15, 45), "water": "Low"},
    "Potato": {"N": (60, 120), "P": (40, 90), "K": (50, 100), "ph": (5.0, 6.5), "temp": (15, 25), "humidity": (50, 80), "rainfall": (500, 1000), "moisture": (45, 75), "water": "Medium"},
}

FEATURES = ["N", "P", "K", "ph", "temp", "humidity", "rainfall", "moisture"]
LABELS = {"N":"Nitrogen (kg/ha)","P":"Phosphorus (kg/ha)","K":"Potassium (kg/ha)","ph":"Soil pH","temp":"Temperature (°C)","humidity":"Relative humidity (%)","rainfall":"Expected seasonal rainfall (mm)","moisture":"Soil moisture (%)"}

def range_score(value, bounds):
    lo, hi = bounds
    if lo <= value <= hi:
        return 100.0
    distance = lo - value if value < lo else value - hi
    scale = max((hi - lo) / 2, 1)
    return max(0.0, 100.0 - (distance / scale) * 100.0)

def evaluate(data, water_available):
    results = []
    for crop, profile in CROPS.items():
        scores = {f: range_score(data[f], profile[f]) for f in FEATURES}
        suitability = sum(scores.values()) / len(scores)
        risks = []
        # Water risk is explicit: expected rainfall + measured soil moisture + irrigation access.
        if data["rainfall"] < profile["rainfall"][0] or data["moisture"] < profile["moisture"][0]:
            risks.append(("Water stress", "High" if not water_available else "Medium"))
        if data["rainfall"] > profile["rainfall"][1] * 1.2:
            risks.append(("Excess rainfall / waterlogging", "High"))
        if data["ph"] < profile["ph"][0] or data["ph"] > profile["ph"][1]:
            risks.append(("Soil pH mismatch", "Medium"))
        if data["temp"] < profile["temp"][0] or data["temp"] > profile["temp"][1]:
            risks.append(("Temperature stress", "High"))
        if not water_available and profile["water"] == "Very high":
            risks.append(("High irrigation demand without assured supply", "High"))
        if not risks:
            risks.append(("No major rule-based warning detected", "Low"))
        risk_points = sum({"Low": 10, "Medium": 22, "High": 35}[level] for _, level in risks)
        risk_score = min(100, risk_points)
        decision_score = 0.65 * suitability + 0.35 * (100 - risk_score)
        results.append({"Crop": crop, "Suitability": round(suitability,1), "Risk score": round(risk_score,1),
                        "Decision score": round(decision_score,1), "Risk level": "High" if risk_score >= 55 else "Medium" if risk_score >= 25 else "Low",
                        "Water need": profile["water"], "Reasons": risks})
    return sorted(results, key=lambda x: x["Decision score"], reverse=True)

st.title("🌱 AgriSmart AI")
st.caption("Crop Suitability Classification & Risk-Aware Recommendation Decision System")
st.info("Prototype note: recommendations use transparent crop-profile ranges and a rule-based risk engine. They are decision-support estimates, not a substitute for local agronomist advice or soil-lab testing.")

with st.sidebar:
    st.header("Farm conditions")
    st.caption("Enter current soil and expected seasonal weather values.")
    values = {
        "N": st.slider(LABELS["N"], 0, 200, 80),
        "P": st.slider(LABELS["P"], 0, 150, 45),
        "K": st.slider(LABELS["K"], 0, 200, 40),
        "ph": st.slider(LABELS["ph"], 3.0, 10.0, 6.5, 0.1),
        "temp": st.slider(LABELS["temp"], 0, 45, 25),
        "humidity": st.slider(LABELS["humidity"], 0, 100, 65),
        "rainfall": st.slider(LABELS["rainfall"], 0, 3000, 800, 25),
        "moisture": st.slider(LABELS["moisture"], 0, 100, 50),
    }
    water_available = st.toggle("Reliable irrigation available?", value=True)
    submitted = st.button("Analyse farm & recommend crops", type="primary", use_container_width=True)

data = values
results = evaluate(data, water_available)
top = results[0]

if submitted:
    st.success("Farm conditions analysed. Recommendations updated below.")

c1, c2, c3 = st.columns(3)
c1.metric("Top recommendation", top["Crop"])
c2.metric("Suitability", f'{top["Suitability"]}%')
c3.metric("Risk level", top["Risk level"])

st.subheader("Recommended crops")
st.write("Ranked using a combined score: 65% suitability and 35% risk-adjusted safety.")
df = pd.DataFrame([{k:v for k,v in r.items() if k != "Reasons"} for r in results])
st.dataframe(df, use_container_width=True, hide_index=True)
st.bar_chart(df.set_index("Crop")[["Suitability", "Decision score"]].head(8))

st.subheader(f"Why {top['Crop']} is ranked first")
for reason, level in top["Reasons"]:
    st.write(f"- **{reason}** — {level}")

st.subheader("Crop-by-crop risk explanation")
for r in results[:5]:
    with st.expander(f"{r['Crop']} — {r['Risk level']} risk | decision score {r['Decision score']}"):
        st.write(f"**Water requirement:** {r['Water need']}")
        for reason, level in r["Reasons"]:
            st.write(f"- {reason}: **{level}**")

st.subheader("Entered farm conditions")
st.dataframe(pd.DataFrame([{"Parameter": LABELS[k], "Value": v} for k,v in data.items()]), use_container_width=True, hide_index=True)

st.divider()
st.caption("Important: Crop ranges are illustrative starter profiles and vary by variety, season, soil type, district and agronomic practice. Validate and localise the thresholds before real-world use.")
