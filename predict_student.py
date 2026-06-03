import pickle
import pandas as pd


# =========================
# CARGAR MODELO Y ARTEFACTOS
# =========================
with open("models/logistic_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("models/encoder.pkl", "rb") as f:
    encoder = pickle.load(f)

with open("models/feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)


# =========================
# FUNCIÓN DE PREDICCIÓN
# =========================
def predecir_error(
    tipo_factorizacion: str,
    dificultad:         int,
    tiempo_respuesta:   float,
    intentos:           int
) -> str:
    """
    Predice el tipo de error de un estudiante.

    Parámetros:
        tipo_factorizacion : diferencia_cuadrados |
                             factor_comun |
                             trinomio |
                             trinomio_cuadrado_perfecto
        dificultad         : 1, 2, 3, 4 o 5
        tiempo_respuesta   : segundos
        intentos           : número de intentos

    Retorna:
        tipo_error : "signo" | "identificacion" | "procedimiento"
    """

    # Construir fila base
    data = {
        "dificultad":      [dificultad],
        "tiempo_respuesta":[tiempo_respuesta],
        "intentos":        [intentos]
    }

    X_new = pd.DataFrame(data)

    # Agregar columnas dummy del tipo de factorización
    tipos_posibles = [
        col.replace("tipo_factorizacion_", "")
        for col in feature_columns
        if col.startswith("tipo_factorizacion_")
    ]

    for tipo in tipos_posibles:
        col_name = f"tipo_factorizacion_{tipo}"
        X_new[col_name] = 1 if tipo == tipo_factorizacion else 0

    # Asegurar orden y columnas correctas
    X_new = X_new.reindex(
        columns=feature_columns,
        fill_value=0
    )

    # Predicción
    pred_encoded  = model.predict(X_new)
    pred_proba    = model.predict_proba(X_new)
    tipo_error    = encoder.inverse_transform(pred_encoded)[0]

    # Probabilidades por clase
    probabilidades = {
        clase: round(float(prob), 4)
        for clase, prob in zip(
            encoder.classes_,
            pred_proba[0]
        )
    }

    return tipo_error, probabilidades


# =========================
# PRUEBA
# =========================
if __name__ == "__main__":

    tipo_error, probabilidades = predecir_error(
        tipo_factorizacion="factor_comun",
        dificultad=1,
        tiempo_respuesta=40.0,
        intentos=2
    )

    print("\nPREDICCIÓN DE ERROR\n")
    print(f"Tipo de error predicho : {tipo_error}")
    print("\nProbabilidades por clase:")

    for clase, prob in probabilidades.items():
        print(f"  {clase}: {prob:.2%}")