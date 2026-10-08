from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from productos.models import Categoria, Producto


class EcommerceTests(APITestCase):

    def setUp(self):
        # Esto se ejecuta ANTES de cada test: prepara datos de prueba
        self.categoria = Categoria.objects.create(nombre="Calzado")
        self.producto = Producto.objects.create(
            nombre="Botines Test",
            descripcion="Botines de prueba",
            marca="TestMarca",
            precio=100000,
            stock=10,
            categoria=self.categoria
        )
        # Un usuario para las pruebas que necesitan login
        self.usuario = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="TestPassword2026"
        )

    # TEST 1: Registro de un usuario nuevo
    def test_registro_usuario(self):
        data = {
            "username": "nuevo",
            "email": "nuevo@test.com",
            "password": "ClaveSegura2026"
        }
        response = self.client.post('/api/auth/registro/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="nuevo").count(), 1)

    # TEST 2: Login devuelve los tokens JWT
    def test_login_devuelve_tokens(self):
        data = {"username": "testuser", "password": "TestPassword2026"}
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    # TEST 3: Listar productos con filtro por categoría
    def test_listar_productos_con_filtro(self):
        response = self.client.get('/api/productos/', {'categoria': self.categoria.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    # TEST 4: Agregar un producto al carrito (requiere login)
    def test_agregar_al_carrito(self):
        self.client.force_authenticate(user=self.usuario)
        data = {"producto_id": self.producto.id, "cantidad": 2}
        response = self.client.post('/api/carrito/agregar/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 200000)  # 2 x 100000

    # TEST 5: Finalizar compra (checkout) descuenta stock y crea el pedido
    def test_finalizar_compra(self):
        self.client.force_authenticate(user=self.usuario)
        # Primero agrego al carrito
        self.client.post('/api/carrito/agregar/', {"producto_id": self.producto.id, "cantidad": 3})
        # Hago el checkout
        response = self.client.post('/api/pedidos/', {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verifico que el stock bajó de 10 a 7
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)