import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing  import LabelEncoder


# =========================
# CARGA DEL DATASET
# =========================
df = pd.read_csv(
    "dataset/cocomath_dataset_50000.csv"
)

print("\nDATASET")
print(df.head())
print(f"\nRegistros totales: {len(df)}")
print(f"\nDistribución de errores:\n{df['tipo_error'].value_counts()}")

# =========================
# VARIABLES DE ENTRADA
# =========================
X = df[[
    "tipo_factorizacion",
    "dificultad",
    "tiempo_respuesta",
    "intentos"
]]

# =========================
# VARIABLE OBJETIVO
# =========================
y = df["tipo_error"]

# =========================
# CODIFICAR VARIABLES CATEGÓRICAS
# =========================
X = pd.get_dummies(
    X,
    columns=["tipo_factorizacion"]
)

# =========================
# GUARDAR COLUMNAS PARA INFERENCIA
# =========================
feature_columns = X.columns.tolist()

# =========================
# CODIFICAR CLASES OBJETIVO
# =========================
encoder = LabelEncoder()

y_encoded = encoder.fit_transform(y)

# =========================
# TRAIN / TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42
)

# =========================
# INFORMACIÓN FINAL
# =========================
print("\nPreprocesamiento completado")
print(f"\nColumnas del modelo : {feature_columns}")
print(f"Clases de error     : {list(encoder.classes_)}")
print(f"\nTrain shape: {X_train.shape}")
print(f"Test shape : {X_test.shape}")