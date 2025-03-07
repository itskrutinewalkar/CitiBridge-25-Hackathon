# -*- coding: utf-8 -*-
"""Loan_fault.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dX-Zw06hoUvQrhfISAn0tlCVYLcTiaHL
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load Dataset
df = pd.read_csv("/Users/krutinewalkar/Desktop/CitiBridge-25-Hackathon/dataset/loan_data.csv")

# Define Features and Target Variable
X = df.drop(columns=["risk_category"])
y = df["risk_category"]

# Identify if the business is a startup
df["is_startup"] = df["business_age"] < 1

# Split Data Based on Business Type
startup_data = df[df["is_startup"] == True]
established_data = df[df["is_startup"] == False]

# Preprocessing for Startups
numerical_features_startup = startup_data.select_dtypes(include=[np.number]).columns.tolist()
preprocessor_startup = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), numerical_features_startup)
])

# Preprocessing for Established Businesses
numerical_features_established = established_data.select_dtypes(include=[np.number]).columns.tolist()
categorical_features_established = ["credit_history"]  # Example categorical feature

preprocessor_established = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), numerical_features_established),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ]), categorical_features_established)
])

# Create Pipelines for Both Models
pipeline_startup = Pipeline([
    ("preprocessor", preprocessor_startup),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

pipeline_established = Pipeline([
    ("preprocessor", preprocessor_established),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

# Split Dataset into Train and Test Sets for Startups
X_train_startup, X_test_startup, y_train_startup, y_test_startup = train_test_split(
    startup_data.drop(columns=["risk_category"]),
    startup_data["risk_category"],
    test_size=0.2,
    random_state=42,
    stratify=startup_data["risk_category"]
)

# Split Dataset into Train and Test Sets for Established Businesses
X_train_established, X_test_established, y_train_established, y_test_established = train_test_split(
    established_data.drop(columns=["risk_category"]),
    established_data["risk_category"],
    test_size=0.2,
    random_state=42,
    stratify=established_data["risk_category"]
)

# Train Models
pipeline_startup.fit(X_train_startup, y_train_startup)
pipeline_established.fit(X_train_established, y_train_established)

# Extract Feature Importances for Startups
feature_importances_startup = pipeline_startup.named_steps["classifier"].feature_importances_
# Get feature names after preprocessing
feature_names_startup = pipeline_startup.named_steps["preprocessor"].get_feature_names_out()
feature_importance_df_startup = pd.DataFrame({
    "feature": feature_names_startup,
    "importance": feature_importances_startup
}).sort_values(by="importance", ascending=False)

# Extract Feature Importances for Established Businesses
feature_importances_established = pipeline_established.named_steps["classifier"].feature_importances_
# Get feature names after preprocessing
feature_names_established = pipeline_established.named_steps["preprocessor"].get_feature_names_out()
feature_importance_df_established = pd.DataFrame({
    "feature": feature_names_established,
    "importance": feature_importances_established
}).sort_values(by="importance", ascending=False)

# Debugging: Print Important Features
print("\nTop Important Features for Startups:")
print(feature_importance_df_startup.head())

print("\nTop Important Features for Established Businesses:")
print(feature_importance_df_established.head())

# Predictions
y_pred_startup = pipeline_startup.predict(X_test_startup)
y_pred_established = pipeline_established.predict(X_test_established)

# Evaluate Models
print("\nClassification Report for Startups:")
print(classification_report(y_test_startup, y_pred_startup))

print("\nClassification Report for Established Businesses:")
print(classification_report(y_test_established, y_pred_established))

