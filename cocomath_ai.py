import json
import time
import random
import pickle
import re
import pandas as pd

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from sympy import expand, symbols

from student_profile import StudentProfile
from learning_logic  import evaluate_student

x = symbols('x')
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor
)


# =========================
# CARGAR EJERCICIOS
# =========================
with open(
    "dataset/ejercicios.json",
    "r",
    encoding="utf-8"
) as f:
    ejercicios = json.load(f)

# =========================
# CARGAR ARTEFACTOS ML
# =========================
with open("models/logistic_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("models/encoder.pkl", "rb") as f:
    encoder = pickle.load(f)

with open("models/feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)


# =========================
# COMPARACIÓN ALGEBRAICA
# =========================
def respuesta_es_correcta(respuesta_alumno: str, respuesta_correcta: str) -> bool:
    """
    Compara algebraicamente la respuesta del alumno
    con la respuesta correcta usando sympy.
    Acepta variantes equivalentes como:
      (x+3)(x-3) == (x-3)(x+3)
      (x+9)^2    == (x+9)(x+9)
    """
    # Comparación exacta primero (más rápida)
    if (
        respuesta_alumno.replace(" ", "").lower()
        ==
        respuesta_correcta.replace(" ", "").lower()
    ):
        return True

    # Comparación algebraica con sympy
    try:
        expr_alumno   = parse_expr(respuesta_alumno,   transformations=TRANSFORMATIONS)
        expr_correcta = parse_expr(respuesta_correcta, transformations=TRANSFORMATIONS)
        return expand(expr_alumno) == expand(expr_correcta)
    except Exception:
        return False


# =========================
# PREDECIR TIPO DE ERROR
# =========================
def predecir_error(
    tipo_factorizacion: str,
    dificultad:         int,
    tiempo_respuesta:   float,
    intentos:           int
) -> str:

    data = {
        "dificultad":       [dificultad],
        "tiempo_respuesta": [tiempo_respuesta],
        "intentos":         [intentos]
    }

    X_new = pd.DataFrame(data)

    tipos_posibles = [
        col.replace("tipo_factorizacion_", "")
        for col in feature_columns
        if col.startswith("tipo_factorizacion_")
    ]

    for tipo in tipos_posibles:
        col_name = f"tipo_factorizacion_{tipo}"
        X_new[col_name] = (
            1 if tipo == tipo_factorizacion else 0
        )

    X_new = X_new.reindex(
        columns=feature_columns,
        fill_value=0
    )

    pred       = model.predict(X_new)
    tipo_error = encoder.inverse_transform(pred)[0]

    return tipo_error


# =========================
# DETECTAR NIVEL DEL ESTUDIANTE
# =========================
def detectar_nivel(aciertos_por_nivel: dict) -> int:
    """
    Determina el nivel inicial del estudiante
    basándose en cuántos ejercicios acertó por nivel.

    Lógica:
    - Si acertó >= 1 ejercicio de nivel 5 → nivel 4
    - Si acertó >= 1 ejercicio de nivel 4 → nivel 3
    - Si acertó >= 1 ejercicio de nivel 3 → nivel 2
    - Si acertó >= 1 ejercicio de nivel 2 → nivel 1
    - Si solo acertó nivel 1 o ninguno    → nivel 1
    """
    for nivel in [5, 4, 3, 2]:
        if aciertos_por_nivel.get(nivel, 0) >= 1:
            return nivel - 1 if nivel > 1 else 1

    return 1


# =========================
# EXAMEN DIAGNÓSTICO
# =========================
def ejecutar_examen_diagnostico(
    student:       StudentProfile,
    num_preguntas: int = 10
) -> dict:
    """
    Selecciona 2 ejercicios de cada nivel (1-5)
    de forma aleatoria para ubicar al estudiante
    en el nivel correcto.
    """

    # Seleccionar 2 ejercicios por nivel (10 total)
    preguntas = []

    por_nivel = num_preguntas // 5  # 2 por nivel

    for nivel in range(1, 6):
        pool = [ej for ej in ejercicios if ej["nivel"] == nivel]
        muestra = random.sample(pool, min(por_nivel, len(pool)))
        preguntas.extend(muestra)

    # Mezclar para que no estén ordenados por nivel
    random.shuffle(preguntas)

    print("\n" + "="*40)
    print("     EXAMEN DIAGNÓSTICO COCOMATH")
    print("="*40)
    print(f"Total de preguntas : {len(preguntas)}")
    print("="*40 + "\n")

    respuestas_guardadas = []

    for i, pregunta in enumerate(preguntas, start=1):

        print(f"Pregunta {i}/{len(preguntas)}")
        print(f"  {pregunta['pregunta']}\n")

        inicio    = time.time()
        respuesta = input("  Tu respuesta: ").strip()
        tiempo    = round(time.time() - inicio, 2)

        print()

        respuestas_guardadas.append({
            "pregunta":         pregunta,
            "respuesta_alumno": respuesta,
            "tiempo":           tiempo
        })

    # =========================
    # ANALIZAR RESPUESTAS CON IA
    # =========================
    print("="*40)
    print("  Analizando tu desempeño...\n")

    errores_predichos  = []
    tiempos            = []
    aciertos_por_nivel = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for item in respuestas_guardadas:

        pregunta         = item["pregunta"]
        respuesta_alumno = item["respuesta_alumno"]
        tiempo           = item["tiempo"]

        correcta = respuesta_es_correcta(
            respuesta_alumno,
            pregunta["respuesta_correcta"]
        )

        if correcta:
            aciertos_por_nivel[pregunta["nivel"]] += 1

        tipo_error = predecir_error(
            tipo_factorizacion=pregunta["tipo_factorizacion"],
            dificultad=pregunta["nivel"],
            tiempo_respuesta=tiempo,
            intentos=1
        )

        errores_predichos.append(tipo_error)
        tiempos.append(tiempo)

        student.registrar_respuesta(
            ejercicio_id=pregunta["id"],
            correcto=correcta,
            tiempo_respuesta=tiempo,
            tipo_error=tipo_error
        )

    # =========================
    # DETECTAR NIVEL
    # =========================
    nivel_detectado = detectar_nivel(aciertos_por_nivel)
    student.nivel_actual = nivel_detectado

    tiempo_promedio = sum(tiempos) / len(tiempos)

    error_frecuente = max(
        set(errores_predichos),
        key=errores_predichos.count
    )

    # =========================
    # RESULTADO FINAL
    # =========================
    print("="*40)
    print("     RESULTADO DEL EXAMEN")
    print("="*40)
    print(f"Aciertos           : {student.aciertos}/{len(preguntas)}")
    print(f"Precisión          : {student.precision:.0%}")
    print(f"Tiempo promedio    : {tiempo_promedio:.1f}s")
    print(f"Nivel asignado     : {nivel_detectado}")
    print(f"Error más frecuente: {error_frecuente}")
    print("\nAciertos por nivel:")
    for nivel, aciertos in aciertos_por_nivel.items():
        print(f"  Nivel {nivel}: {aciertos}/{por_nivel}")
    print("="*40 + "\n")

    return {
        "aciertos":          student.aciertos,
        "total":             len(preguntas),
        "precision":         student.precision,
        "tiempo_promedio":   tiempo_promedio,
        "nivel_asignado":    nivel_detectado,
        "error_frecuente":   error_frecuente,
        "errores_predichos": errores_predichos,
        "aciertos_por_nivel": aciertos_por_nivel
    }


# =========================
# PRUEBA
# =========================
if __name__ == "__main__":

    estudiante = StudentProfile(student_id=1)

    ejecutar_examen_diagnostico(
        student=estudiante,
        num_preguntas=10
    )