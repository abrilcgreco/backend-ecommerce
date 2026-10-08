from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('id')
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        # Listar y ver: cualquiera. Crear/editar/borrar: solo admin.
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('id')
    serializer_class = ProductoSerializer
    search_fields = ['nombre']
    filterset_fields = ['categoria']
    ordering_fields = ['precio', 'nombre']

    def get_permissions(self):
        # Listar y ver detalle: cualquiera puede.
        # Crear, editar, borrar: solo usuario administrador.
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]