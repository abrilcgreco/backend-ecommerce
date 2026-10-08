from django.db import models



class Mensaje(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.nombre} ({self.correo})"