import json
import random

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
# EXAMEN DIAGNÓSTICO
# =========================
diagnostic_questions = random.sample(
    ejercicios,
    10
)

print("\nEXAMEN DIAGNÓSTICO\n")

for question in diagnostic_questions:

    print(question["pregunta"])