from rest_framework import serializers
from .models import Carrito, ItemCarrito
from productos.serializers import ProductoSerializer


class ItemCarritoSerializer(serializers.ModelSerializer):
    # Muestra los datos completos del producto (solo lectura)
    producto = ProductoSerializer(read_only=True)
    # El subtotal de este ítem (precio x cantidad)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ['id', 'producto', 'cantidad', 'subtotal']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return obj.get_total()