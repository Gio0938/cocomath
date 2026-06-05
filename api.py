import json
import pickle
import pandas as pd

from fastapi             import FastAPI, HTTPException
from pydantic            import BaseModel, Field
from typing              import List, Optional

from learning_logic      import evaluate_student
from student_profile     import StudentProfile


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
# APLICACIÓN
# =========================
app = FastAPI(
    title="CocoMath API",
    description=(
        "API del motor adaptativo CocoMath. "
        "Predice errores de factorización y recomienda ejercicios."
    ),
    version="1.0.0"
)

# Almacenamiento en memoria de perfiles
# (en producción se reemplaza por una base de datos)
perfiles: dict[int, StudentProfile] = {}


# =========================
# SCHEMAS
# =========================
class PredictRequest(BaseModel):
    tipo_factorizacion: str  = Field(
        ...,
        example="diferencia_cuadrados",
        description=(
            "diferencia_cuadrados | factor_comun | "
            "trinomio | trinomio_cuadrado_perfecto"
        )
    )
    dificultad:         int   = Field(..., ge=1, le=5, example=1)
    tiempo_respuesta:   float = Field(..., gt=0, example=50.0)
    intentos:           int   = Field(..., ge=1, example=2)


class PredictResponse(BaseModel):
    tipo_error:     str
    probabilidades: dict


class RecomendarRequest(BaseModel):
    student_id:         int
    tipo_factorizacion: str
    dificultad:         int   = Field(..., ge=1, le=5)
    tiempo_respuesta:   float = Field(..., gt=0)
    intentos:           int   = Field(..., ge=1)
    max_ejercicios:     int   = Field(5, ge=1, le=20)


class EjercicioResponse(BaseModel):
    id:                 int
    pregunta:           str
    nivel:              int
    tipo_factorizacion: str
    errores_asociados:  List[str]


class RegistrarRespuestaRequest(BaseModel):
    student_id:    int
    ejercicio_id:  int
    correcto:      bool
    tiempo:        float
    tipo_error:    Optional[str] = None


class EvaluarRequest(BaseModel):
    student_id: int


# =========================
# HELPER: PREDECIR ERROR
# =========================
def _predecir_error(
    tipo_factorizacion: str,
    dificultad:         int,
    tiempo_respuesta:   float,
    intentos:           int
) -> tuple[str, dict]:

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

    pred         = model.predict(X_new)
    pred_proba   = model.predict_proba(X_new)
    tipo_error   = encoder.inverse_transform(pred)[0]

    probabilidades = {
        clase: round(float(prob), 4)
        for clase, prob in zip(encoder.classes_, pred_proba[0])
    }

    return tipo_error, probabilidades


# =========================
# ENDPOINTS
# =========================

@app.get("/")
def root():
    return {
        "app":     "CocoMath API",
        "version": "1.0.0",
        "status":  "running"
    }


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Predice el tipo de error más probable de un estudiante
    en función de sus métricas de respuesta.
    """
    tipo_error, probabilidades = _predecir_error(
        request.tipo_factorizacion,
        request.dificultad,
        request.tiempo_respuesta,
        request.intentos
    )

    return PredictResponse(
        tipo_error=tipo_error,
        probabilidades=probabilidades
    )


@app.post("/recomendar", response_model=List[EjercicioResponse])
def recomendar(request: RecomendarRequest):
    """
    Recomienda ejercicios personalizados según el nivel
    del estudiante y el error predicho.
    """
    # Obtener o crear perfil
    if request.student_id not in perfiles:
        perfiles[request.student_id] = StudentProfile(
            request.student_id
        )

    estudiante = perfiles[request.student_id]

    tipo_error, _ = _predecir_error(
        request.tipo_factorizacion,
        request.dificultad,
        request.tiempo_respuesta,
        request.intentos
    )

    nivel = estudiante.nivel_actual

    recomendados = [
        ej for ej in ejercicios
        if (
            ej["nivel"] == nivel
            and tipo_error in ej["errores_asociados"]
        )
    ]

    if len(recomendados) < request.max_ejercicios:
        extras = [
            ej for ej in ejercicios
            if ej["nivel"] == nivel and ej not in recomendados
        ]
        recomendados += extras

    return recomendados[:request.max_ejercicios]


@app.post("/registrar-respuesta")
def registrar_respuesta(request: RegistrarRespuestaRequest):
    """
    Registra la respuesta de un estudiante a un ejercicio
    y actualiza su perfil.
    """
    if request.student_id not in perfiles:
        perfiles[request.student_id] = StudentProfile(
            request.student_id
        )

    estudiante = perfiles[request.student_id]

    estudiante.registrar_respuesta(
        ejercicio_id=request.ejercicio_id,
        correcto=request.correcto,
        tiempo_respuesta=request.tiempo,
        tipo_error=request.tipo_error
    )

    return {
        "mensaje":  "Respuesta registrada",
        "resumen":  estudiante.resumen()
    }


@app.post("/evaluar")
def evaluar(request: EvaluarRequest):
    """
    Evalúa el desempeño del estudiante y actualiza su nivel.
    """
    if request.student_id not in perfiles:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado"
        )

    estudiante = perfiles[request.student_id]

    resultado = evaluate_student(
        aciertos=estudiante.aciertos,
        errores=estudiante.errores,
        tiempo_promedio=estudiante.tiempo_promedio,
        nivel_actual=estudiante.nivel_actual
    )

    estudiante.nivel_actual = resultado["nuevo_nivel"]

    return resultado


@app.get("/perfil/{student_id}")
def perfil(student_id: int):
    """
    Devuelve el resumen del perfil de un estudiante.
    """
    if student_id not in perfiles:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado"
        )

    return perfiles[student_id].resumen()


@app.get("/ejercicios")
def listar_ejercicios(
    nivel: Optional[int] = None,
    tipo:  Optional[str] = None
):
    """
    Lista todos los ejercicios disponibles.
    Acepta filtros opcionales por nivel y tipo de factorización.
    """
    resultado = ejercicios

    if nivel is not None:
        resultado = [
            ej for ej in resultado
            if ej["nivel"] == nivel
        ]

    if tipo is not None:
        resultado = [
            ej for ej in resultado
            if ej["tipo_factorizacion"] == tipo
        ]

    return resultado