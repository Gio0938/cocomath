def evaluate_student(
    aciertos,
    errores,
    tiempo_promedio,
    nivel_actual
):

    # =========================
    # CALCULAR PRECISIÓN
    # =========================
    total = aciertos + errores

    if total == 0:
        precision = 0
    else:
        precision = aciertos / total

    # =========================
    # MOSTRAR DATOS
    # =========================
    print("\nREPORTE DEL ESTUDIANTE\n")

    print(f"Nivel actual: {nivel_actual}")

    print(f"Precisión: {precision:.2f}")

    print(
        f"Tiempo promedio: {tiempo_promedio}"
    )

    # =========================
    # DECISIONES PEDAGÓGICAS
    # =========================

    # SUBIR NIVEL
    if (
        precision >= 0.80
        and
        tiempo_promedio < 60
        ):

        nuevo_nivel = nivel_actual + 1

        decision = "SUBIR NIVEL"

    # MANTENER NIVEL
    elif (
        precision >= 0.50
        ):

        nuevo_nivel = nivel_actual

        decision = "MANTENER NIVEL"

    # BAJAR / REFORZAR
    else:

        nuevo_nivel = max(
            1,
            nivel_actual - 1
        )

        decision = "REFORZAR TEMAS"

    # =========================
    # RESULTADO
    # =========================
    print(f"\nDECISIÓN: {decision}")

    print(
        f"Nuevo nivel: {nuevo_nivel}"
    )

    return nuevo_nivel


# =========================
# PRUEBA
# =========================
evaluate_student(

    aciertos=8,

    errores=2,

    tiempo_promedio=45,

    nivel_actual=1
)