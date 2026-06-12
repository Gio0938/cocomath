
from student_profile  import StudentProfile
from diagnostic_exam  import ejecutar_examen_diagnostico
from adaptive_engine  import AdaptiveEngine


# =========================
# FLUJO PRINCIPAL
# =========================
def iniciar_sesion(student_id: int):

    print("\n" + "="*40)
    print("       BIENVENIDO A COCOMATH")
    print("="*40)
    print(f"Estudiante ID: {student_id}\n")

    # -------------------------
    # 1. PERFIL DEL ESTUDIANTE
    # -------------------------
    estudiante = StudentProfile(student_id=student_id)

    # -------------------------
    # 2. EXAMEN DIAGNÓSTICO
    # El estudiante responde libremente.
    # El modelo predice sus errores.
    # -------------------------
    print("Iniciando examen diagnóstico...\n")

    resultados_examen = ejecutar_examen_diagnostico(
        student=estudiante,
        num_preguntas=10,
        nivel=1
    )

    # -------------------------
    # 3. MOTOR ADAPTATIVO
    # Usa el error frecuente real del estudiante
    # para recomendar ejercicios personalizados.
    # -------------------------
    engine = AdaptiveEngine(student=estudiante)

    recomendados, error_predicho = engine.recomendar_ejercicios(
        tipo_factorizacion="diferencia_cuadrados",
        dificultad=estudiante.nivel_actual,
        tiempo_respuesta=estudiante.tiempo_promedio,
        intentos=2,
        max_ejercicios=5
    )

    # -------------------------
    # 4. MOSTRAR RECOMENDACIONES
    # -------------------------
    print("="*40)
    print("     EJERCICIOS RECOMENDADOS")
    print("="*40)
    print(f"Error frecuente detectado : {resultados_examen['error_frecuente']}")
    print(f"Nivel actual              : {estudiante.nivel_actual}\n")

    for i, ej in enumerate(recomendados, start=1):
        print(f"{i}. {ej['pregunta']}")
        print(f"   Tipo : {ej['tipo_factorizacion']}")
        print(f"   Nivel: {ej['nivel']}\n")

    # -------------------------
    # 5. RESUMEN FINAL
    # -------------------------
    print("="*40)
    print("     RESUMEN DEL ESTUDIANTE")
    print("="*40)

    for clave, valor in estudiante.resumen().items():
        print(f"  {clave}: {valor}")

    print("\n")

    return estudiante, recomendados


# =========================
# PUNTO DE ENTRADA
# =========================
if __name__ == "__main__":

    iniciar_sesion(student_id=1)