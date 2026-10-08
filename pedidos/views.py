from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Pedido, ItemPedido
from .serializers import PedidoSerializer
from carrito.models import Carrito


class PedidoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # GET /api/pedidos/  -> historial de pedidos del usuario logueado
    def list(self, request):
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

    # POST /api/pedidos/  -> finalizar compra (checkout)
    def create(self, request):
        # Busca el carrito del usuario
        try:
            carrito = Carrito.objects.get(usuario=request.user)
        except Carrito.DoesNotExist:
            return Response(
                {"error": "No tenés un carrito."},
                status=status.HTTP_400_BAD_REQUEST
            )

        items_carrito = carrito.items.all()
        if not items_carrito.exists():
            return Response(
                {"error": "El carrito está vacío."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO lo de abajo ocurre dentro de una transacción:
        # o se hace TODO, o no se hace NADA.
        try:
            with transaction.atomic():
                # 1. Crear el pedido
                pedido = Pedido.objects.create(usuario=request.user, total=0)
                total = 0

                # 2. Pasar cada item del carrito al pedido
                for item in items_carrito:
                    producto = item.producto

                    # Validar stock otra vez (por si cambió)
                    if item.cantidad > producto.stock:
                        # Esto corta la transacción y deshace todo
                        raise ValueError(
                            f"No hay stock suficiente de {producto.nombre}. "
                            f"Disponible: {producto.stock}"
                        )

                    # Crear el item del pedido (guardando el precio actual)
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=item.cantidad,
                        precio_unitario=producto.precio
                    )

                    # Descontar el stock
                    producto.stock -= item.cantidad
                    producto.save()

                    # Sumar al total
                    total += producto.precio * item.cantidad

                # 3. Guardar el total del pedido
                pedido.total = total
                pedido.save()

                # 4. Vaciar el carrito
                carrito.items.all().delete()

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Devolver el pedido creado
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)