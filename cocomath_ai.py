import json
import pickle
import pandas as pd

from learning_logic import evaluate_student

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
# DATOS DEL ESTUDIANTE
# =========================
student_data = {

    "dificultad": [1],

    "tiempo_respuesta": [45],

    "intentos": [2],

    "tipo_factorizacion_diferencia_cuadrados": [1],

    "tipo_factorizacion_factor_comun": [0],

    "tipo_factorizacion_trinomio": [0],

    "tipo_factorizacion_trinomio_cuadrado_perfecto": [0]
}

X_new = pd.DataFrame(student_data)

# =========================
# PREDICCIÓN ML
# =========================
prediction = model.predict(X_new)

predicted_error = prediction[0]

print("\nERROR PREDICHO:")
print(predicted_error)

# =========================
# EVALUAR ESTUDIANTE
# =========================
nuevo_nivel = evaluate_student(

    aciertos=8,

    errores=2,

    tiempo_promedio=45,

    nivel_actual=1
)

# =========================
# RECOMENDAR EJERCICIOS
# =========================
recommended_exercises = []

for ejercicio in ejercicios:

    if (

        ejercicio["nivel"]
        ==
        nuevo_nivel

        and

        predicted_error
        in
        ejercicio["errores_asociados"]

    ):

        recommended_exercises.append(
            ejercicio
        )

# =========================
# RESULTADOS
# =========================
print("\nEJERCICIOS RECOMENDADOS\n")

for ejercicio in recommended_exercises[:5]:

    print(
        ejercicio["pregunta"]
    )