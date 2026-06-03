import json
import pickle
import pandas as pd

from learning_logic  import evaluate_student
from student_profile import StudentProfile


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
# CARGAR EJERCICIOS
# =========================
with open("dataset/ejercicios.json", "r", encoding="utf-8") as f:
    ejercicios = json.load(f)


# =========================
# MOTOR ADAPTATIVO
# =========================
class AdaptiveEngine:

    def __init__(self, student: StudentProfile):
        self.student    = student
        self.ejercicios = ejercicios

    # =========================
    # PREDECIR ERROR
    # =========================
    def predecir_error(
        self,
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

        pred        = model.predict(X_new)
        tipo_error  = encoder.inverse_transform(pred)[0]

        return tipo_error

    # =========================
    # RECOMENDAR EJERCICIOS
    # =========================
    def recomendar_ejercicios(
        self,
        tipo_factorizacion: str,
        dificultad:         int,
        tiempo_respuesta:   float,
        intentos:           int,
        max_ejercicios:     int = 5
    ) -> list:

        # Predecir error probable
        tipo_error = self.predecir_error(
            tipo_factorizacion,
            dificultad,
            tiempo_respuesta,
            intentos
        )

        nivel = self.student.nivel_actual

        # Filtrar por nivel y error predicho
        recomendados = [
            ej for ej in self.ejercicios
            if (
                ej["nivel"] == nivel
                and tipo_error in ej["errores_asociados"]
            )
        ]

        # Si no hay suficientes, ampliar solo por nivel
        if len(recomendados) < max_ejercicios:
            extras = [
                ej for ej in self.ejercicios
                if (
                    ej["nivel"] == nivel
                    and ej not in recomendados
                )
            ]
            recomendados += extras

        return recomendados[:max_ejercicios], tipo_error

    # =========================
    # ACTUALIZAR NIVEL
    # =========================
    def actualizar_nivel(self) -> dict:

        resultado = evaluate_student(
            aciertos=self.student.aciertos,
            errores=self.student.errores,
            tiempo_promedio=self.student.tiempo_promedio,
            nivel_actual=self.student.nivel_actual
        )

        self.student.nivel_actual = resultado["nuevo_nivel"]

        return resultado


# =========================
# PRUEBA
# =========================
if __name__ == "__main__":

    # Crear perfil de estudiante
    estudiante = StudentProfile(student_id=1)

    # Simular respuestas previas
    respuestas = [
        (1, True,  40.0, None),
        (2, True,  38.0, None),
        (3, False, 70.0, "signo"),
        (4, True,  42.0, None),
        (5, False, 80.0, "identificacion"),
        (6, True,  35.0, None),
        (7, True,  41.0, None),
        (8, False, 75.0, "signo"),
        (9, True,  39.0, None),
        (10, True, 44.0, None),
    ]

    for ej_id, correcto, tiempo, error in respuestas:
        estudiante.registrar_respuesta(ej_id, correcto, tiempo, error)

    # Crear motor adaptativo
    engine = AdaptiveEngine(student=estudiante)

    # Actualizar nivel
    print("\n" + "="*40)
    resultado = engine.actualizar_nivel()

    # Recomendar ejercicios
    recomendados, error_predicho = engine.recomendar_ejercicios(
        tipo_factorizacion="diferencia_cuadrados",
        dificultad=1,
        tiempo_respuesta=50.0,
        intentos=2
    )

    print("\n" + "="*40)
    print(f"\nERROR PREDICHO    : {error_predicho}")
    print(f"NIVEL DEL ALUMNO  : {estudiante.nivel_actual}")
    print("\nEJERCICIOS RECOMENDADOS:\n")

    for ej in recomendados:
        print(f"  [{ej['nivel']}] {ej['pregunta']}")
        print(f"       Respuesta: {ej['respuesta_correcta']}\n")

    # Mostrar resumen del perfil
    print("="*40)
    print("\nRESUMEN DEL ESTUDIANTE\n")

    for clave, valor in estudiante.resumen().items():
        print(f"  {clave}: {valor}")