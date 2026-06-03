from datetime import datetime


# =========================
# PERFIL DEL ESTUDIANTE
# =========================
class StudentProfile:

    def __init__(self, student_id: int):

        self.student_id        = student_id
        self.nivel_actual      = 1
        self.precision         = 0.0
        self.errores_frecuentes = []
        self.ejercicios_resueltos = 0
        self.aciertos          = 0
        self.errores           = 0
        self.tiempo_promedio   = 0.0
        self.historial         = []
        self.fecha_creacion    = datetime.now().isoformat()
        self.ultima_actividad  = datetime.now().isoformat()

    # =========================
    # REGISTRAR RESPUESTA
    # =========================
    def registrar_respuesta(
        self,
        ejercicio_id: int,
        correcto: bool,
        tiempo_respuesta: float,
        tipo_error: str = None
        ):
        self.ejercicios_resueltos += 1
        self.ultima_actividad = datetime.now().isoformat()

        if correcto:
            self.aciertos += 1
        else:
            self.errores += 1

            if tipo_error:
                self.errores_frecuentes.append(tipo_error)

        # Actualizar tiempo promedio
        total = self.ejercicios_resueltos
        self.tiempo_promedio = (
            (self.tiempo_promedio * (total - 1) + tiempo_respuesta)
            / total
        )

        # Actualizar precisión
        self.precision = (
            self.aciertos / self.ejercicios_resueltos
        )

        # Guardar en historial
        self.historial.append({
            "ejercicio_id":    ejercicio_id,
            "correcto":        correcto,
            "tiempo":          tiempo_respuesta,
            "tipo_error":      tipo_error,
            "timestamp":       datetime.now().isoformat()
        })

    # =========================
    # ERROR MÁS FRECUENTE
    # =========================
    def error_mas_frecuente(self) -> str:

        if not self.errores_frecuentes:
            return None

        return max(
            set(self.errores_frecuentes),
            key=self.errores_frecuentes.count
        )

    # =========================
    # RESUMEN DEL PERFIL
    # =========================
    def resumen(self) -> dict:

        return {
            "student_id":           self.student_id,
            "nivel_actual":         self.nivel_actual,
            "precision":            round(self.precision, 2),
            "ejercicios_resueltos": self.ejercicios_resueltos,
            "aciertos":             self.aciertos,
            "errores":              self.errores,
            "tiempo_promedio":      round(self.tiempo_promedio, 2),
            "error_mas_frecuente":  self.error_mas_frecuente(),
            "ultima_actividad":     self.ultima_actividad
        }

    # =========================
    # REPRESENTACIÓN
    # =========================
    def __repr__(self):
        return (
            f"StudentProfile("
            f"id={self.student_id}, "
            f"nivel={self.nivel_actual}, "
            f"precision={self.precision:.2f})"
        )


# =========================
# PRUEBA
# =========================
if __name__ == "__main__":

    perfil = StudentProfile(student_id=1)

    perfil.registrar_respuesta(
        ejercicio_id=1,
        correcto=True,
        tiempo_respuesta=40.0
    )

    perfil.registrar_respuesta(
        ejercicio_id=2,
        correcto=False,
        tiempo_respuesta=70.0,
        tipo_error="signo"
    )

    perfil.registrar_respuesta(
        ejercicio_id=3,
        correcto=False,
        tiempo_respuesta=65.0,
        tipo_error="signo"
    )

    print("\nRESUMEN DEL PERFIL\n")

    for clave, valor in perfil.resumen().items():
        print(f"{clave}: {valor}")