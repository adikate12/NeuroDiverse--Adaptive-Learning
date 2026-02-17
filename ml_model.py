import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

# Path to the CSV file (same folder as this file)
CSV_PATH = Path(__file__).parent / "adhd_training_data.csv"

# Load training data
df = pd.read_csv(CSV_PATH)

FEATURE_COLS = ["attention_score", "impulsivity_score", "organization_score", "working_memory"]

X = df[FEATURE_COLS].values
y = df["label"].values

# Train Random Forest model
rf_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)
rf_model.fit(X, y)

LABEL_TO_FULL = {
    "PI": "Predominantly inattentive",
    "PH": "Predominantly hyperactive–impulsive",
    "C": "Combined presentation"
}

def classify_from_scores(attention, impulsivity, organization, working_memory):
    """
    Takes 4 scores (0–100) and returns:
      short_label: "PI" / "PH" / "C"
      full_label : human-readable description
    """
    features = np.array([[attention, impulsivity, organization, working_memory]])
    short_label = rf_model.predict(features)[0]
    full_label = LABEL_TO_FULL.get(short_label, "Unspecified / mild")
    return short_label, full_label
