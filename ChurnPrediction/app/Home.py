# Home.py: Model Comparison Page (MLP, Logistic, KNN, SVM & XGBoost)
import streamlit as st
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, f1_score
)
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier

 
import tensorflow as tf
import matplotlib.pyplot as plt


# Page config
st.set_page_config(page_title="Churn Prediction", layout="wide")
st.title("Churn Prediction (Model Comparison)")
st.caption("TensorFlow MLP vs Logistic Regression vs KNN vs SVM")

# Sidebar controls
st.sidebar.header("Settings")

DATA_PATH = st.sidebar.text_input("CSV path", "data/customer_churn_business_dataset.csv")
SEED = st.sidebar.number_input("Random seed", min_value=0, value=42, step=1)

test_size = st.sidebar.slider("Test size", 0.10, 0.40, 0.20, 0.05)
val_share_of_temp = st.sidebar.slider(
    "Val share (of temp split)", 0.10, 0.90, 0.50, 0.05
)

k_neighbors = st.sidebar.slider("KNN: k", 1, 50, 15, 1)
svm_c = st.sidebar.number_input("SVM C", min_value=0.01, value=1.0, step=0.1)
svm_kernel = st.sidebar.selectbox("SVM kernel", ["rbf", "linear", "poly", "sigmoid"], index=0)

threshold = st.sidebar.slider("Decision threshold", 0.05, 0.95, 0.50, 0.05)

use_class_weights = st.sidebar.checkbox("Use class weights (recommended)", value=True)

train_mlp = st.sidebar.checkbox("Train TensorFlow MLP (slower)", value=True)
epochs = st.sidebar.slider("MLP max epochs", 10, 300, 200, 10)
batch_size = st.sidebar.selectbox("Batch size", [16, 32, 64, 128], index=2)
patience = st.sidebar.slider("Early stopping patience", 3, 30, 10, 1)

run = st.sidebar.button("Run Training & Evaluation", type="primary")


# Cached preprocessing
@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def preprocess(df: pd.DataFrame):
    if "churn" not in df.columns:
        raise ValueError("Dataset must contain a 'churn' column.")

    categorical_features = [
        "gender", "country", "city", "customer_segment",
        "signup_channel", "contract_type", "payment_method",
        "complaint_type", "survey_response"
    ]

    y = pd.to_numeric(df["churn"], errors="coerce").fillna(0).astype(int).to_numpy()

    drop_cols = [c for c in ["customer_id", "churn"] if c in df.columns]
    X = df.drop(columns=drop_cols).copy()

    binary_map = {"Yes": 1, "No": 0}
    for bcol in ["discount_applied", "price_increase_last_3m"]:
        if bcol in X.columns:
            X[bcol] = X[bcol].map(binary_map)
            X[bcol] = pd.to_numeric(X[bcol], errors="coerce").fillna(0).astype(int)

    categorical_features = [c for c in categorical_features if c in X.columns]
    X = pd.get_dummies(X, columns=categorical_features, drop_first=False, dtype=int)

    X = X.fillna(0)
    return X, y

def compute_weights(y_train: np.ndarray):
    classes = np.unique(y_train)
    w = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    return {int(c): float(wi) for c, wi in zip(classes, w)}

def eval_sklearn_model(name, clf, Xtr, ytr, Xte, yte, thr=0.5):
    clf.fit(Xtr, ytr)

    if hasattr(clf, "predict_proba"):
        probs = clf.predict_proba(Xte)[:, 1]
    elif hasattr(clf, "decision_function"):
        scores = clf.decision_function(Xte)
        probs = 1 / (1 + np.exp(-scores))
    else:
        probs = None

    preds = clf.predict(Xte) if probs is None else (probs >= thr).astype(int)

    out = {
        "model": name,
        "accuracy": float((preds == yte).mean()),
        "f1": float(f1_score(yte, preds, zero_division=0)),
        "auc": float(roc_auc_score(yte, probs)) if probs is not None else np.nan
    }

    details = {
        "confusion": confusion_matrix(yte, preds),
        "report": classification_report(yte, preds, digits=4, zero_division=0),
        "probs": probs,
        "preds": preds
    }
    return out, details

def build_mlp(input_dim: int, lr=1e-3):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_dim,)),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.20),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall")
        ]
    )
    return model

# Preview 
with st.expander("Dataset preview", expanded=False):
    try:
        df_preview = load_data(DATA_PATH)
        st.dataframe(df_preview.head(10), use_container_width=True, hide_index=True)
        if "churn" in df_preview.columns:
            churn_rate_preview = pd.to_numeric(df_preview["churn"], errors="coerce").mean()
            st.write(f"Churn rate (mean of churn): **{churn_rate_preview:.2%}**")
    except Exception as e:
        st.warning(f"Could not load dataset preview: {e}")

# If user clicked RUN, train models and STORE results in session_state
if run:
    np.random.seed(int(SEED))
    tf.random.set_seed(int(SEED))

    with st.spinner("Loading and preprocessing data..."):
        df = load_data(DATA_PATH)
        X, y = preprocess(df)

    churn_rate = float(np.mean(y))
    st.write(f"Churn rate: **{churn_rate:.2%}**")

    with st.spinner("Splitting + scaling..."):
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=float(test_size),
            stratify=y,
            random_state=int(SEED)
        )

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=float(1 - val_share_of_temp),
            stratify=y_temp,
            random_state=int(SEED)
        )

        scaler = MinMaxScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_val_s   = scaler.transform(X_val)
        X_test_s  = scaler.transform(X_test)

    cw = compute_weights(y_train) if use_class_weights else None
    if cw:
        st.sidebar.success(f"Using class weights: {cw}")

    results = []
    details_map = {}
    mlp_history = None

    # Logistic Regression
    with st.spinner("Training Logistic Regression..."):
        lr = LogisticRegression(max_iter=2000, class_weight="balanced" if use_class_weights else None)
        r, d = eval_sklearn_model("Logistic Regression", lr, X_train_s, y_train, X_test_s, y_test, thr=float(threshold))
        results.append(r); details_map[r["model"]] = d

    # KNN
    with st.spinner("Training KNN..."):
        knn = KNeighborsClassifier(n_neighbors=int(k_neighbors))
        r, d = eval_sklearn_model(f"KNN (k={int(k_neighbors)})", knn, X_train_s, y_train, X_test_s, y_test, thr=float(threshold))
        results.append(r); details_map[r["model"]] = d

    # SVM
    with st.spinner("Training SVM... (this can be slower)"):
        svm = SVC(
            kernel=svm_kernel,
            C=float(svm_c),
            gamma="scale",
            probability=True,
            class_weight="balanced" if use_class_weights else None,
            random_state=int(SEED)
        )
        r, d = eval_sklearn_model(f"SVM ({svm_kernel})", svm, X_train_s, y_train, X_test_s, y_test, thr=float(threshold))
        results.append(r); details_map[r["model"]] = d

    # XGBoost
    with st.spinner("Training XGBoost..."):
        xgb = XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            use_label_encoder=False,
            random_state=int(SEED)
        )

        r, d = eval_sklearn_model(
            "XGBoost",
            xgb,
            X_train_s,
            y_train,
            X_test_s,
            y_test,
            thr=float(threshold)
        )

        results.append(r)
        details_map[r["model"]] = d


    # MLP 
    if train_mlp:
        with st.spinner("Training TensorFlow MLP..."):
            mlp = build_mlp(X_train_s.shape[1], lr=1e-3)

            early_stop = tf.keras.callbacks.EarlyStopping(
                monitor="val_auc",
                mode="max",
                patience=int(patience),
                restore_best_weights=True
            )

            mlp_history = mlp.fit(
                X_train_s, y_train,
                validation_data=(X_val_s, y_val),
                epochs=int(epochs),
                batch_size=int(batch_size),
                callbacks=[early_stop],
                class_weight=cw,
                verbose=0
            )

            mlp_probs = mlp.predict(X_test_s, verbose=0).ravel()
            mlp_preds = (mlp_probs >= float(threshold)).astype(int)

            r = {
                "model": "TensorFlow MLP",
                "accuracy": float((mlp_preds == y_test).mean()),
                "f1": float(f1_score(y_test, mlp_preds, zero_division=0)),
                "auc": float(roc_auc_score(y_test, mlp_probs))
            }
            d = {
                "confusion": confusion_matrix(y_test, mlp_preds),
                "report": classification_report(y_test, mlp_preds, digits=4, zero_division=0),
                "probs": mlp_probs,
                "preds": mlp_preds
            }
            results.append(r); details_map[r["model"]] = d

    results_df = pd.DataFrame(results).sort_values("auc", ascending=False)

    # Persist results so widget interactions don't wipe them
    st.session_state["has_run"] = True
    st.session_state["results_df"] = results_df
    st.session_state["details_map"] = details_map
    st.session_state["y_test"] = y_test
    st.session_state["mlp_history"] = mlp_history

# If not run yet, but no cached results, prompt user
if not st.session_state.get("has_run", False):
    st.info("Adjust settings in the sidebar, then click **Run Training & Evaluation**.")
    st.stop()

# Read cached results from session_state 
results_df = st.session_state["results_df"]
details_map = st.session_state["details_map"]
y_test = st.session_state["y_test"]
mlp_history = st.session_state.get("mlp_history", None)

# Show results table & winner KPIs
st.subheader("Model Comparison")
st.dataframe(results_df, use_container_width=True, hide_index=True)

best_row = results_df.iloc[0].to_dict()
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Best model (by AUC)", best_row["model"])
kpi2.metric("Best AUC", f"{best_row['auc']:.3f}")
kpi3.metric("Best F1", f"{best_row['f1']:.3f}")

# Model drill-down 
st.divider()
st.subheader("Model Details")

model_choice = st.selectbox("Select a model to inspect:", results_df["model"].tolist(), key="model_choice")
d = details_map[model_choice]

c1, c2 = st.columns(2)
with c1:
    st.write("Confusion matrix")
    st.code(d["confusion"])
with c2:
    st.write("Classification report")
    st.text(d["report"])


# ROC curve plot (all models w/ probs)
st.divider()
st.subheader("ROC Curves (Test Set)")

fig = plt.figure()
for m in results_df["model"].tolist():
    probs = details_map[m]["probs"]
    if probs is None:
        continue
    fpr, tpr, _ = roc_curve(y_test, probs)
    plt.plot(fpr, tpr, label=m)

plt.plot([0, 1], [0, 1], linestyle="--", label="Random")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves")
plt.legend()
st.pyplot(fig)

# MLP training curves (if trained)
if mlp_history is not None:
    st.divider()
    st.subheader("MLP Training Curves")

    fig1 = plt.figure()
    plt.plot(mlp_history.history.get("loss", []), label="train_loss")
    plt.plot(mlp_history.history.get("val_loss", []), label="val_loss")
    plt.xlabel("Epoch")
    plt.ylabel("Binary Cross-Entropy")
    plt.title("MLP Loss over epochs")
    plt.legend()
    st.pyplot(fig1)

    fig2 = plt.figure()
    plt.plot(mlp_history.history.get("auc", []), label="train_auc")
    plt.plot(mlp_history.history.get("val_auc", []), label="val_auc")
    plt.xlabel("Epoch")
    plt.ylabel("AUC")
    plt.title("MLP AUC over epochs")
    plt.legend()
    st.pyplot(fig2)
