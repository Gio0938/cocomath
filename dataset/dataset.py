import random
import numpy as np
import pandas as pd


# =========================
# CONFIGURACIÓN
# =========================
N_REGISTROS = 50000

SEMILLA = 42
random.seed(SEMILLA)
np.random.seed(SEMILLA)

TIPOS_FACTORIZACION = [
    "diferencia_cuadrados",
    "factor_comun",
    "trinomio_cuadrado_perfecto",
    "trinomio_general"
]

TIPOS_ERROR = ["signo", "identificacion", "procedimiento"]


# =========================
# PERFILES DE ESTUDIANTE
# =========================
# Cada estudiante simulado tiene un "nivel de habilidad" oculto
# que afecta su tiempo de respuesta e intentos, pero NO determina
# el error de forma exacta — solo influye en las probabilidades.

PERFILES = ["principiante", "intermedio", "avanzado"]

PERFIL_PROBABILIDADES = {
    "principiante": 0.35,
    "intermedio":   0.45,
    "avanzado":     0.20
}


# =========================
# GENERAR UN REGISTRO
# =========================
def generar_registro():

    # -------------------------
    # VARIABLES BASE
    # -------------------------
    perfil = np.random.choice(
        PERFILES,
        p=[PERFIL_PROBABILIDADES[p] for p in PERFILES]
    )

    tipo_factorizacion = random.choice(TIPOS_FACTORIZACION)

    dificultad = random.randint(1, 5)

    # -------------------------
    # TIEMPO DE RESPUESTA
    # -------------------------
    # Cada perfil tiene una distribución base de tiempo,
    # pero con ruido aleatorio (nadie responde siempre igual)

    if perfil == "principiante":
        tiempo_base = np.random.normal(70, 20)

    elif perfil == "intermedio":
        tiempo_base = np.random.normal(45, 15)

    else:  # avanzado
        tiempo_base = np.random.normal(30, 10)

    # La dificultad y el tipo de ejercicio agregan variabilidad
    factor_dificultad = 1 + (dificultad - 1) * 0.12

    factor_tipo = {
        "diferencia_cuadrados":       1.0,
        "factor_comun":               0.9,
        "trinomio_cuadrado_perfecto": 1.05,
        "trinomio_general":           1.3
    }[tipo_factorizacion]

    tiempo_respuesta = tiempo_base * factor_dificultad * factor_tipo

    # Ruido adicional + límites realistas
    tiempo_respuesta += np.random.normal(0, 5)
    tiempo_respuesta = max(8, round(tiempo_respuesta, 2))

    # -------------------------
    # INTENTOS
    # -------------------------
    # Más probable tener más intentos si el tiempo es alto
    # o si el perfil es principiante, pero sigue siendo aleatorio

    if perfil == "principiante":
        intentos = np.random.choice([1, 2, 3, 4], p=[0.30, 0.35, 0.25, 0.10])

    elif perfil == "intermedio":
        intentos = np.random.choice([1, 2, 3, 4], p=[0.50, 0.30, 0.15, 0.05])

    else:  # avanzado
        intentos = np.random.choice([1, 2, 3, 4], p=[0.70, 0.20, 0.08, 0.02])

    # Trinomio general aumenta ligeramente la probabilidad de más intentos
    if tipo_factorizacion == "trinomio_general" and intentos < 4:
        if random.random() < 0.15:
            intentos += 1

    # -------------------------
    # TIPO DE ERROR (PROBABILÍSTICO)
    # -------------------------
    # Las probabilidades de cada tipo de error dependen de
    # tendencias generales, NO de reglas exactas.
    #
    # Tendencias generales:
    #   - Diferencia de cuadrados      -> tiende a error de SIGNO
    #   - Factor común                 -> tiende a error de PROCEDIMIENTO
    #   - Trinomio cuadrado perfecto   -> tiende a IDENTIFICACIÓN
    #   - Trinomio general              -> mezcla, más PROCEDIMIENTO
    #
    #   - Tiempo alto + muchos intentos -> aumenta PROCEDIMIENTO
    #   - Dificultad alta                -> aumenta IDENTIFICACIÓN
    #   - Perfil avanzado                 -> más probable SIGNO (descuido)
    #                                         que error conceptual

    # Probabilidades base por tipo de factorización
    probs_base = {
        "diferencia_cuadrados":       {"signo": 0.65, "identificacion": 0.18, "procedimiento": 0.17},
        "factor_comun":               {"signo": 0.12, "identificacion": 0.18, "procedimiento": 0.70},
        "trinomio_cuadrado_perfecto": {"signo": 0.15, "identificacion": 0.65, "procedimiento": 0.20},
        "trinomio_general":           {"signo": 0.18, "identificacion": 0.22, "procedimiento": 0.60},
    }[tipo_factorizacion]

    probs = dict(probs_base)

    # Ajuste por tiempo de respuesta (más tiempo -> más procedimiento)
    if tiempo_respuesta > 60:
        probs["procedimiento"] += 0.20
        probs["signo"]         -= 0.10
        probs["identificacion"] -= 0.10

    # Ajuste por intentos (más intentos -> más procedimiento/identificación)
    if intentos >= 3:
        probs["procedimiento"]  += 0.15
        probs["identificacion"] += 0.08
        probs["signo"]          -= 0.20

    # Ajuste por dificultad (más difícil -> más identificación)
    if dificultad >= 4:
        probs["identificacion"] += 0.15
        probs["signo"]          -= 0.07
        probs["procedimiento"]  -= 0.08

    # Ajuste por perfil (avanzados cometen más errores "tontos" de signo
    # cuando sí fallan, no conceptuales)
    if perfil == "avanzado":
        probs["signo"]          += 0.15
        probs["identificacion"] -= 0.08
        probs["procedimiento"]  -= 0.07

    elif perfil == "principiante":
        probs["identificacion"] += 0.12
        probs["procedimiento"]  += 0.06
        probs["signo"]          -= 0.18

    # -------------------------
    # NORMALIZAR PROBABILIDADES
    # -------------------------
    # Evitar valores negativos
    for k in probs:
        probs[k] = max(0.01, probs[k])

    total = sum(probs.values())
    for k in probs:
        probs[k] = probs[k] / total

    # -------------------------
    # AGREGAR RUIDO ALEATORIO GLOBAL
    # -------------------------
    # 12% de las veces, ignorar todas las tendencias
    # y asignar el error completamente al azar.
    # Esto simula el comportamiento humano impredecible.

    if random.random() < 0.05:
        tipo_error = random.choice(TIPOS_ERROR)
    else:
        tipo_error = np.random.choice(
            TIPOS_ERROR,
            p=[probs["signo"], probs["identificacion"], probs["procedimiento"]]
        )

    return {
        "tipo_factorizacion": tipo_factorizacion,
        "dificultad":         dificultad,
        "tiempo_respuesta":   tiempo_respuesta,
        "intentos":           int(intentos),
        "tipo_error":         tipo_error
    }


# =========================
# GENERAR DATASET COMPLETO
# =========================
def generar_dataset(n_registros: int) -> pd.DataFrame:

    registros = []

    for i in range(1, n_registros + 1):

        registro = generar_registro()
        registro["student_id"] = i

        registros.append(registro)

    df = pd.DataFrame(registros)

    # Reordenar columnas
    df = df[
        [
            "student_id",
            "tipo_factorizacion",
            "dificultad",
            "tiempo_respuesta",
            "intentos",
            "tipo_error"
        ]
    ]

    return df


# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":

    print(f"\nGenerando {N_REGISTROS} registros...\n")

    df = generar_dataset(N_REGISTROS)

    # =========================
    # ESTADÍSTICAS DEL DATASET
    # =========================
    print("Distribución de tipo_error:")
    print(df["tipo_error"].value_counts(normalize=True).round(3))

    print("\nDistribución de tipo_factorizacion:")
    print(df["tipo_factorizacion"].value_counts(normalize=True).round(3))

    print("\nEstadísticas de tiempo_respuesta:")
    print(df["tiempo_respuesta"].describe().round(2))

    print("\nEstadísticas de intentos:")
    print(df["intentos"].describe().round(2))

    # =========================
    # VERIFICAR QUE NO HAYA DETERMINISMO PERFECTO
    # =========================
    print("\nVerificación de determinismo:")
    print("(Cuántos valores únicos de tipo_error hay por combinación")
    print(" de tipo_factorizacion + dificultad + intentos)\n")

    combinaciones = df.groupby(
        ["tipo_factorizacion", "dificultad", "intentos"]
    )["tipo_error"].nunique()

    print(combinaciones.value_counts())

    # =========================
    # GUARDAR CSV
    # =========================
    output_path = "cocomath_dataset_50000.csv"

    df.to_csv(output_path, index=False)

    print(f"\nDataset guardado en: {output_path}")
    print(f"Total de registros : {len(df)}")