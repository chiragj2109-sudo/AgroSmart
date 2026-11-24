# AgriSmart AI

A runnable prototype for **Crop Suitability Classification and Risk-Aware Recommendation**.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create/activate a virtual environment (recommended).
4. Run:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
5. Open the local URL shown in the terminal (usually http://localhost:8501).

## Current features
- Inputs: N, P, K, soil pH, temperature, humidity, seasonal rainfall, soil moisture and irrigation availability.
- Multi-crop suitability scoring.
- Rule-based risk flags for water stress, excess rainfall, pH mismatch and temperature stress.
- Risk-adjusted ranking and explanations.

## Important scope note
This is an educational prototype. It uses transparent starter crop-profile ranges, not a validated trained model or live weather feed. The thresholds are illustrative and must be calibrated with local agricultural extension guidance, crop variety, season and reliable district-level data before field deployment.

## Suggested next development stage
Replace the starter profiles with locally validated crop-specific datasets; add a train/test evaluated classifier (e.g. Random Forest), seasonal weather forecasts, location-aware soil data and model performance reporting.
