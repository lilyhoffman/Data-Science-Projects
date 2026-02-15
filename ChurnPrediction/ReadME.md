# Customer Churn Prediction and Analytics Dashboard
An end-to-end machine learning and analytics project for predicting customer churn and visualizing customer behavior insights using Streamlit.

This project combines interactive data exploration, multiple model comparison, ROC evaluation, threshold tuning, class imbalance handling, and gradient boosting optimization using XGBoost.

# Dataset
https://www.kaggle.com/datasets/miadul/customer-churn-prediction-business-dataset/code

## Project Overview
Customer churn is a critical business problem that directly impacts revenue and customer lifetime value. This project builds a full machine learning pipeline to:

- Analyze churn behavior
- Compare multiple classification models
- Optimize classification thresholds
- Identify the best-performing algorithm
- Deploy results in an interactive dashboard

## Models Compared
The following models were implemented and evaluated:
- Logistic Regression  
- K-Nearest Neighbors (KNN)  
- Support Vector Machine (SVM: RBF kernel)  
- TensorFlow Multi-Layer Perceptron (MLP)  
- XGBoost (Gradient Boosting)

### Best Performing Model
XGBoost achieved the highest performance with:

- ROC-AUC ≈ 0.81
- Strong ranking performance on imbalanced data
- Better discrimination than neural and distance-based models on structured tabular data

## Key Findings
- The dataset is imbalanced (approximately 10 percent churn rate)
- Accuracy alone is not an appropriate evaluation metric
- ROC-AUC provides a better measure of ranking performance
- Threshold tuning significantly improves F1-score
- Gradient boosting performs best for structured tabular business data

## Dashboard Features

### Analytics Dashboard
- KPI metrics (Churn rate, CSAT, Session time, etc.)
- Churn distribution visualization
- Feature-by-churn box plots
- Raw dataset explorer
- Interactive filters

### Model Comparison Page
- Stratified train/validation/test split
- MinMax scaling (fit only on training data to avoid leakage)
- Class weight handling for imbalance
- ROC curve visualization
- Model comparison table
- Confusion matrices
- Classification reports
- Adjustable decision threshold
- Early stopping for neural network training

## Project Structure
├── app/
│ └── Home.py
├── pages/
│ ├── About.py
│ └── Analytics_Dashboard.py
├── data/
│ └── customer_churn_business_dataset.csv
├── requirements.txt
└── README.md

## Installation
- Clone the repository
- Install dependencies 
`pip install -r requirements.txt`

## Run Application
python -m streamlit run home.py

## Requirements
- streamlit  
- pandas  
- numpy  
- scikit-learn  
- matplotlib  
- altair  
- xgboost  
- tensorflow

## Evaluation Metrics Used
- Accuracy  
- Precision  
- Recall  
- F1-score  
- ROC-AUC  
- Confusion Matrix  
- ROC Curves  

## Future Improvements
- SHAP feature explanations  
- Hyperparameter tuning (GridSearch or Bayesian optimization)  
- Precision-Recall curve visualization  
- Model persistence using joblib  
- Cloud deployment (Streamlit Cloud, Render, etc.)


## Author
Lily Hoffman

