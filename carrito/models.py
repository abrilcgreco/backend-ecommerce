from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto


class Carrito(models.Model):
    # Cada usuario tiene UN carrito (relación uno a uno)
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="carrito"
    )
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    def get_total(self):
        # Suma el subtotal de todos los items
        return sum(item.get_subtotal() for item in self.items.all())


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name="items"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        # Un producto no puede estar repetido en el mismo carrito
        unique_together = ['carrito', 'producto']

    def get_subtotal(self):
        # Precio del producto por la cantidad
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"