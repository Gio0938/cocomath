# 🥥 CocoMath AI

Sistema de aprendizaje adaptativo para ejercicios de **factorización algebraica**, impulsado por un modelo de **Regresión Logística Multiclase** que detecta los errores más frecuentes de cada estudiante y personaliza su ruta de aprendizaje.

---

## 📌 ¿Qué es CocoMath?

CocoMath es una plataforma educativa inteligente que:

- Aplica un **examen diagnóstico** al estudiante
- Usa **Machine Learning** para predecir el tipo de error que comete
- **Adapta los ejercicios** según el nivel y los errores detectados
- Genera una **ruta de aprendizaje personalizada**

---

## 🧠 Modelo de Inteligencia Artificial

Se utilizó un modelo de **Regresión Logística Multiclase** entrenado con **50,000 registros** de interacciones simuladas de estudiantes.

### Variables de entrada

| Variable | Descripción |
|---|---|
| `tipo_factorizacion` | Tipo de ejercicio (diferencia de cuadrados, factor común, trinomio, etc.) |
| `dificultad` | Nivel del ejercicio (1 al 5) |
| `tiempo_respuesta` | Tiempo en segundos que tardó el estudiante |
| `intentos` | Número de intentos realizados |

### Tipos de error que predice

| Error | Descripción |
|---|---|
| `signo` | Error al manejar signos positivos/negativos |
| `identificacion` | No identifica correctamente el método de factorización |
| `procedimiento` | Error en el proceso algebraico |

---

## 📁 Estructura del proyecto

```
CocoMath/
├── dataset/
│   ├── cocomath_dataset_50000.csv   # Dataset de entrenamiento
│   └── ejercicios.json              # Banco de ejercicios
├── models/                          # Se genera al entrenar
│   ├── logistic_model.pkl
│   ├── encoder.pkl
│   └── feature_columns.pkl
├── preprocessing.py                 # Preprocesamiento del dataset
├── train_model.py                   # Entrenamiento del modelo
├── predict_student.py               # Predicción de errores
├── student_profile.py               # Perfil del estudiante
├── learning_logic.py                # Lógica pedagógica de niveles
├── diagnostic_exam.py               # Examen diagnóstico inicial
├── adaptive_engine.py               # Motor de recomendación adaptativa
├── cocomath_ai.py                   # Orquestador principal
└── api.py                           # API REST con FastAPI
```

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/cocomath.git
cd cocomath
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear carpetas necesarias

```bash
mkdir models
```

---

## 🚀 Uso

### Paso 1 — Entrenar el modelo

```bash
python train_model.py
```

Genera los archivos en `models/`:
- `logistic_model.pkl`
- `encoder.pkl`
- `feature_columns.pkl`

### Paso 2 — Iniciar sesión de estudiante

```bash
python cocomath_ai.py
```

Flujo completo:
1. El estudiante responde el examen diagnóstico
2. La IA analiza su comportamiento
3. Se asigna un nivel
4. Se recomiendan ejercicios personalizados

### Paso 3 — Levantar la API (opcional)

```bash
uvicorn api:app --reload
```

Accede a la documentación interactiva en:

```
http://127.0.0.1:8000/docs
```

---

## 🌐 Endpoints de la API

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Estado de la API |
| `POST` | `/predict` | Predice el tipo de error del estudiante |
| `POST` | `/recomendar` | Recomienda ejercicios personalizados |
| `POST` | `/registrar-respuesta` | Registra una respuesta del estudiante |
| `POST` | `/evaluar` | Evalúa y actualiza el nivel del estudiante |
| `GET` | `/perfil/{student_id}` | Obtiene el perfil del estudiante |
| `GET` | `/ejercicios` | Lista ejercicios (filtra por nivel o tipo) |

### Ejemplo de uso — `/predict`

**Request:**
```json
{
  "tipo_factorizacion": "diferencia_cuadrados",
  "dificultad": 1,
  "tiempo_respuesta": 55.0,
  "intentos": 2
}
```

**Response:**
```json
{
  "tipo_error": "signo",
  "probabilidades": {
    "identificacion": 0.2134,
    "procedimiento": 0.3021,
    "signo": 0.4845
  }
}
```

---

## 🔄 Flujo del sistema

```
Estudiante responde examen diagnóstico
                ↓
   Se registran respuestas y tiempos
                ↓
  Modelo de Regresión Logística Multiclase
                ↓
       Predicción del tipo de error
                ↓
          Motor Adaptativo
                ↓
   Ejercicios personalizados por nivel
```

---

## 📦 Dependencias

```
fastapi
uvicorn
scikit-learn
pandas
numpy
pydantic
```

Genera el archivo `requirements.txt` con:

```bash
pip freeze > requirements.txt
```

---

## 🗂️ Tipos de factorización

| Tipo | Ejemplo | Niveles |
|---|---|---|
| Diferencia de cuadrados | `x² - 9 = (x+3)(x-3)` | 1 y 2 |
| Factor común | `x² + 4x = x(x+4)` | 1 y 2 |
| Trinomio cuadrado perfecto | `x² + 6x + 9 = (x+3)²` | 1 y 2 |
| Trinomio general | `x² + 5x + 6 = (x+2)(x+3)` | 3 |

---

## 📊 Niveles de aprendizaje

| Condición | Decisión |
|---|---|
| Precisión ≥ 80% y tiempo promedio < 120s | ⬆️ Subir nivel |
| Precisión ≥ 50% | ➡️ Mantener nivel |
| Precisión < 50% | ⬇️ Reforzar temas |

---

## 👨‍💻 Desarrollado por

**CocoMath Team**  
Proyecto de aprendizaje adaptativo con IA para álgebra.

---

## 📄 Licencia

Este proyecto está bajo la licencia incluida en el archivo `LICENSE`.
