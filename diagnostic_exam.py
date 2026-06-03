import json
import time
import random
import pickle
import pandas as pd

from student_profile import StudentProfile
from learning_logic  import evaluate_student


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
# EXAMEN DIAGNÓSTICO
# =========================
def ejecutar_examen_diagnostico(
    student:       StudentProfile,
    num_preguntas: int = 10,
    nivel:         int = 1
) -> dict:

    pool = [
        ej for ej in ejercicios
        if ej["nivel"] == nivel
    ]

    if len(pool) < num_preguntas:
        num_preguntas = len(pool)

    preguntas = random.sample(pool, num_preguntas)

    print("\n" + "="*40)
    print("     EXAMEN DIAGNÓSTICO COCOMATH")
    print("="*40)
    print(f"Total de preguntas : {num_preguntas}")
    print(f"Nivel              : {nivel}")
    print("="*40 + "\n")

    respuestas_guardadas = []

    for i, pregunta in enumerate(preguntas, start=1):

        print(f"Pregunta {i}/{num_preguntas}")
        print(f"  {pregunta['pregunta']}\n")

        inicio    = time.time()
        respuesta = input("  Tu respuesta: ").strip()
        tiempo    = round(time.time() - inicio, 2)

        print()

        # Guardar respuesta para analizar al final
        respuestas_guardadas.append({
            "pregunta":          pregunta,
            "respuesta_alumno":  respuesta,
            "tiempo":            tiempo
        })

    # =========================
    # ANALIZAR RESPUESTAS CON IA
    # =========================
    print("="*40)
    print("  Analizando tu desempeño...\n")

    errores_predichos = []
    tiempos           = []

    for item in respuestas_guardadas:

        pregunta         = item["pregunta"]
        respuesta_alumno = item["respuesta_alumno"]
        tiempo           = item["tiempo"]

        correcta = (
            respuesta_alumno.replace(" ", "").lower()
            ==
            pregunta["respuesta_correcta"]
                .replace(" ", "").lower()
        )

        # El modelo predice el tipo de error
        # basándose en el comportamiento del estudiante
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
            tipo_error=tipo_error if not correcta else None
        )

    # =========================
    # EVALUAR NIVEL
    # =========================
    tiempo_promedio = sum(tiempos) / len(tiempos)

    resultado = evaluate_student(
        aciertos=student.aciertos,
        errores=student.errores,
        tiempo_promedio=tiempo_promedio,
        nivel_actual=nivel
    )

    student.nivel_actual = resultado["nuevo_nivel"]

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
    print(f"Aciertos           : {student.aciertos}/{num_preguntas}")
    print(f"Precisión          : {resultado['precision']:.0%}")
    print(f"Tiempo promedio    : {tiempo_promedio:.1f}s")
    print(f"Decisión           : {resultado['decision']}")
    print(f"Nivel asignado     : {resultado['nuevo_nivel']}")
    print(f"Error más frecuente: {error_frecuente}")
    print("="*40 + "\n")

    return {
        "aciertos":          student.aciertos,
        "total":             num_preguntas,
        "precision":         resultado["precision"],
        "tiempo_promedio":   tiempo_promedio,
        "nivel_asignado":    resultado["nuevo_nivel"],
        "decision":          resultado["decision"],
        "error_frecuente":   error_frecuente,
        "errores_predichos": errores_predichos
    }


# =========================
# PRUEBA
# =========================
if __name__ == "__main__":

    estudiante = StudentProfile(student_id=1)

    ejecutar_examen_diagnostico(
        student=estudiante,
        num_preguntas=10,
        nivel=1
    )