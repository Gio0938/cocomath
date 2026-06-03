import json
import random

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
# EXAMEN DIAGNÓSTICO
# =========================
def ejecutar_examen_diagnostico(
    student:          StudentProfile,
    num_preguntas:    int = 10,
    nivel:            int = 1,
    modo_interactivo: bool = True
) -> dict:
    """
    Ejecuta el examen diagnóstico inicial para un estudiante.

    Retorna un diccionario con los resultados del examen.
    """

    # Filtrar ejercicios del nivel indicado
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

    aciertos       = 0
    errores_lista  = []
    tiempos        = []

    for i, pregunta in enumerate(preguntas, start=1):

        print(f"Pregunta {i}/{num_preguntas}")
        print(f"  {pregunta['pregunta']}")

        if modo_interactivo:

            import time

            inicio   = time.time()
            respuesta = input("  Tu respuesta: ").strip()
            tiempo   = round(time.time() - inicio, 2)

        else:
            # Modo simulación (para pruebas automáticas)
            respuesta = pregunta["respuesta_correcta"]
            tiempo    = random.uniform(30, 90)

        tiempos.append(tiempo)

        correcto = (
            respuesta.replace(" ", "").lower()
            ==
            pregunta["respuesta_correcta"].replace(" ", "").lower()
        )

        if correcto:
            aciertos += 1
            print("  ✓ Correcto\n")
            student.registrar_respuesta(
                ejercicio_id=pregunta["id"],
                correcto=True,
                tiempo_respuesta=tiempo
            )

        else:
            # Detectar tipo de error probable
            tipo_error = pregunta["errores_asociados"][0]
            errores_lista.append(tipo_error)

            print(f"  ✗ Incorrecto")
            print(
                f"  Respuesta correcta: "
                f"{pregunta['respuesta_correcta']}\n"
            )
            student.registrar_respuesta(
                ejercicio_id=pregunta["id"],
                correcto=False,
                tiempo_respuesta=tiempo,
                tipo_error=tipo_error
            )

    # =========================
    # CALCULAR RESULTADOS
    # =========================
    tiempo_promedio = (
        sum(tiempos) / len(tiempos)
        if tiempos else 0
    )

    resultado = evaluate_student(
        aciertos=aciertos,
        errores=num_preguntas - aciertos,
        tiempo_promedio=tiempo_promedio,
        nivel_actual=nivel
    )

    student.nivel_actual = resultado["nuevo_nivel"]

    # =========================
    # MOSTRAR RESULTADO FINAL
    # =========================
    print("\n" + "="*40)
    print("     RESULTADO DEL EXAMEN")
    print("="*40)
    print(f"Aciertos        : {aciertos}/{num_preguntas}")
    print(f"Precisión       : {resultado['precision']:.0%}")
    print(f"Tiempo promedio : {tiempo_promedio:.1f}s")
    print(f"Decisión        : {resultado['decision']}")
    print(f"Nivel asignado  : {resultado['nuevo_nivel']}")

    if errores_lista:
        error_comun = max(
            set(errores_lista),
            key=errores_lista.count
        )
        print(f"Error frecuente : {error_comun}")

    print("="*40 + "\n")

    return {
        "aciertos":       aciertos,
        "total":          num_preguntas,
        "precision":      resultado["precision"],
        "tiempo_promedio":tiempo_promedio,
        "nivel_asignado": resultado["nuevo_nivel"],
        "decision":       resultado["decision"],
        "errores":        errores_lista
    }


# =========================
# PRUEBA (modo simulación)
# =========================
if __name__ == "__main__":

    estudiante = StudentProfile(student_id=42)

    resultados = ejecutar_examen_diagnostico(
        student=estudiante,
        num_preguntas=10,
        nivel=1,
        modo_interactivo=True # True para modo real en consola
    )