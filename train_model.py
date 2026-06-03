import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report
)

from preprocessing import (
    X_train,
    X_test,
    y_train,
    y_test,
    encoder,
    feature_columns
)


# =========================
# MODELO
# =========================
model = LogisticRegression(
    solver="lbfgs",
    max_iter=1000
)

# =========================
# ENTRENAMIENTO
# =========================
print("\nEntrenando modelo...\n")

model.fit(X_train, y_train)

# =========================
# PREDICCIONES
# =========================
y_pred = model.predict(X_test)

# =========================
# MÉTRICAS
# =========================
accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.4f}")
print("\nReporte de clasificación:\n")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=encoder.classes_
    )
)

# =========================
# GUARDAR MODELO
# =========================
with open("models/logistic_model.pkl", "wb") as f:
    pickle.dump(model, f)

# =========================
# GUARDAR ENCODER
# =========================
with open("models/encoder.pkl", "wb") as f:
    pickle.dump(encoder, f)

# =========================
# GUARDAR COLUMNAS
# =========================
with open("models/feature_columns.pkl", "wb") as f:
    pickle.dump(feature_columns, f)

print("\nModelo, encoder y columnas guardados correctamente")