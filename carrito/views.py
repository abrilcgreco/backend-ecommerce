from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Carrito, ItemCarrito
from .serializers import CarritoSerializer
from productos.models import Producto


class CarritoViewSet(viewsets.ViewSet):
    # Todos los endpoints del carrito requieren estar logueado
    permission_classes = [IsAuthenticated]

    def get_carrito(self, user):
        # Busca el carrito del usuario, o lo crea si no existe
        carrito, _ = Carrito.objects.get_or_create(usuario=user)
        return carrito

    # GET /api/carrito/  -> ver el carrito
    def list(self, request):
        carrito = self.get_carrito(request.user)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

    # POST /api/carrito/agregar/  -> agregar un producto
    @action(detail=False, methods=['post'])
    def agregar(self, request):
        carrito = self.get_carrito(request.user)
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        # Verifica que el producto exista
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response(
                {"error": "El producto no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Busca si ya está en el carrito
        item, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito, producto=producto
        )
        # Si ya estaba, suma; si es nuevo, usa la cantidad pedida
        nueva_cantidad = cantidad if creado else item.cantidad + cantidad

        # Valida que no supere el stock
        if nueva_cantidad > producto.stock:
            return Response(
                {"error": f"No hay stock suficiente. Stock disponible: {producto.stock}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.cantidad = nueva_cantidad
        item.save()
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)

    # PUT /api/carrito/actualizar/  -> cambiar la cantidad de un ítem
    @action(detail=False, methods=['put'])
    def actualizar(self, request):
        carrito = self.get_carrito(request.user)
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        try:
            item = ItemCarrito.objects.get(carrito=carrito, producto_id=producto_id)
        except ItemCarrito.DoesNotExist:
            return Response(
                {"error": "El producto no está en el carrito."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Valida stock
        if cantidad > item.producto.stock:
            return Response(
                {"error": f"No hay stock suficiente. Stock disponible: {item.producto.stock}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.cantidad = cantidad
        item.save()
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)

    # DELETE /api/carrito/eliminar/  -> quitar un ítem
    @action(detail=False, methods=['delete'])
    def eliminar(self, request):
        carrito = self.get_carrito(request.user)
        producto_id = request.data.get('producto_id')

        try:
            item = ItemCarrito.objects.get(carrito=carrito, producto_id=producto_id)
        except ItemCarrito.DoesNotExist:
            return Response(
                {"error": "El producto no está en el carrito."},
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)

    # DELETE /api/carrito/vaciar/  -> vaciar todo el carrito
    @action(detail=False, methods=['delete'])
    def vaciar(self, request):
        carrito = self.get_carrito(request.user)
        carrito.items.all().delete()
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)