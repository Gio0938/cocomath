import json
import pickle
import pandas as pd

# =========================
# CARGAR MODELO
# =========================
with open(
    "models/logistic_model.pkl",
    "rb"
) as file:

    model = pickle.load(file)

# =========================
# CARGAR EJERCICIOS
# =========================
with open(
    "dataset/ejercicios.json",
    "r",
    encoding="utf-8"
) as file:

    ejercicios = json.load(file)

# =========================
# DATOS NUEVO ESTUDIANTE
# =========================
student_data = {

    "dificultad": [1],

    "tiempo_respuesta": [50],

    "intentos": [2],

    "tipo_factorizacion_diferencia_cuadrados": [1],

    "tipo_factorizacion_factor_comun": [0],

    "tipo_factorizacion_trinomio": [0],

    "tipo_factorizacion_trinomio_cuadrado_perfecto": [0]
}

X_new = pd.DataFrame(student_data)

# =========================
# PREDICCIÓN
# =========================
prediction = model.predict(X_new)

predicted_error = prediction[0]

print("\nERROR PREDICHO:")
print(predicted_error)

# =========================
# RECOMENDAR EJERCICIOS
# =========================
recommended_exercises = []

for ejercicio in ejercicios:

    if (
        predicted_error
        in
        ejercicio["errores_asociados"]
    ):

        recommended_exercises.append(
            ejercicio
        )

# =========================
# MOSTRAR RESULTADOS
# =========================
print("\nEJERCICIOS RECOMENDADOS\n")

for ejercicio in recommended_exercises[:5]:

    print(
        ejercicio["pregunta"]
    )