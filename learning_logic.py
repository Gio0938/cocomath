from datetime import datetime


# =========================
# EVALUAR ESTUDIANTE
# =========================
def evaluate_student(
    aciertos:        int,
    errores:         int,
    tiempo_promedio: float,
    nivel_actual:    int
) -> dict:

    # =========================
    # CALCULAR PRECISIÓN
    # =========================
    total = aciertos + errores

    if total == 0:
        precision = 0.0
    else:
        precision = aciertos / total

    # =========================
    # DECISIONES PEDAGÓGICAS
    # =========================

    # SUBIR NIVEL
    if precision >= 0.80 and tiempo_promedio < 120:

        nuevo_nivel = nivel_actual + 1
        decision    = "SUBIR NIVEL"
        mensaje     = (
            "¡Excelente desempeño! "
            "Avanzas al siguiente nivel."
        )

    # MANTENER NIVEL
    elif precision >= 0.50:

        nuevo_nivel = nivel_actual
        decision    = "MANTENER NIVEL"
        mensaje     = (
            "Buen trabajo. "
            "Sigue practicando para dominar este nivel."
        )

    # BAJAR / REFORZAR
    else:

        nuevo_nivel = max(1, nivel_actual - 1)
        decision    = "REFORZAR TEMAS"
        mensaje     = (
            "Necesitas reforzar los temas de este nivel. "
            "¡Tú puedes!"
        )

    # =========================
    # RESULTADO COMPLETO
    # =========================
    resultado = {
        "nivel_anterior":  nivel_actual,
        "nuevo_nivel":     nuevo_nivel,
        "decision":        decision,
        "mensaje":         mensaje,
        "precision":       round(precision, 2),
        "aciertos":        aciertos,
        "errores":         errores,
        "tiempo_promedio": tiempo_promedio,
        "timestamp":       datetime.now().isoformat()
    }

    # =========================
    # MOSTRAR REPORTE
    # =========================
    print("\nREPORTE DEL ESTUDIANTE\n")
    print(f"Nivel actual    : {nivel_actual}")
    print(f"Precisión       : {precision:.2%}")
    print(f"Tiempo promedio : {tiempo_promedio:.1f}s")
    print(f"\nDECISIÓN       : {decision}")
    print(f"Nuevo nivel     : {nuevo_nivel}")
    print(f"Mensaje         : {mensaje}")

    return resultado


# =========================
# PRUEBA
# =========================
if __name__ == "__main__":

    resultado = evaluate_student(
        aciertos=8,
        errores=2,
        tiempo_promedio=45,
        nivel_actual=1
    )