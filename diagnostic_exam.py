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
    """
    Ejecuta el examen diagnóstico.
    El estudiante responde libremente.
    El modelo predice el tipo de error según
    su comportamiento (tiempo e intentos).
    """

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

    errores_predichos = []
    tiempos           = []

    for i, pregunta in enumerate(preguntas, start=1):

        intentos       = 0
        tiempo_total   = 0.0

        print(f"Pregunta {i}/{num_preguntas}")
        print(f"  {pregunta['pregunta']}\n")

        while True:

            intentos += 1

            inicio    = time.time()
            respuesta = input(
                f"  Tu respuesta (intento {intentos}): "
            ).strip()
            tiempo_respuesta = round(time.time() - inicio, 2)
            tiempo_total    += tiempo_respuesta

            # Verificar respuesta
            correcta = (
                respuesta.replace(" ", "").lower()
                ==
                pregunta["respuesta_correcta"]
                    .replace(" ", "").lower()
            )

            if correcta:
                print("  ✓ Correcto\n")
                break

            else:
                print("  ✗ Incorrecto, intenta de nuevo.\n")

                if intentos >= 3:
                    print(
                        f"  Respuesta correcta: "
                        f"{pregunta['respuesta_correcta']}\n"
                    )
                    break

        # Predecir tipo de error con el modelo
        tipo_error = predecir_error(
            tipo_factorizacion=pregunta["tipo_factorizacion"],
            dificultad=pregunta["nivel"],
            tiempo_respuesta=tiempo_total,
            intentos=intentos
        )

        errores_predichos.append(tipo_error)
        tiempos.append(tiempo_total)

        # Registrar en perfil
        student.registrar_respuesta(
            ejercicio_id=pregunta["id"],
            correcto=correcta,
            tiempo_respuesta=tiempo_total,
            tipo_error=tipo_error if not correcta else None
        )

        print(
            f"  Error detectado por IA : {tipo_error}\n"
        )

    # =========================
    # CALCULAR RESULTADOS
    # =========================
    tiempo_promedio = sum(tiempos) / len(tiempos)

    resultado = evaluate_student(
        aciertos=student.aciertos,
        errores=student.errores,
        tiempo_promedio=tiempo_promedio,
        nivel_actual=nivel
    )

    student.nivel_actual = resultado["nuevo_nivel"]

    # Error más frecuente predicho
    error_frecuente = (
        max(set(errores_predichos), key=errores_predichos.count)
        if errores_predichos else None
    )

    # =========================
    # RESULTADO FINAL
    # =========================
    print("\n" + "="*40)
    print("     RESULTADO DEL EXAMEN")
    print("="*40)
    print(f"Aciertos          : {student.aciertos}/{num_preguntas}")
    print(f"Precisión         : {resultado['precision']:.0%}")
    print(f"Tiempo promedio   : {tiempo_promedio:.1f}s")
    print(f"Decisión          : {resultado['decision']}")
    print(f"Nivel asignado    : {resultado['nuevo_nivel']}")
    print(f"Error más frecuente: {error_frecuente}")
    print("="*40 + "\n")

    return {
        "aciertos":        student.aciertos,
        "total":           num_preguntas,
        "precision":       resultado["precision"],
        "tiempo_promedio": tiempo_promedio,
        "nivel_asignado":  resultado["nuevo_nivel"],
        "decision":        resultado["decision"],
        "error_frecuente": error_frecuente,
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