from django.contrib import admin
from .models import Mensaje


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'correo', 'fecha']
    search_fields = ['nombre', 'correo']