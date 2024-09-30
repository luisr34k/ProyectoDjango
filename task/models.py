# models.py
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Tienda(models.Model):
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(max_length=255, blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    # Relaciones con otras tablas
    color = models.ForeignKey('Color', on_delete=models.CASCADE)
    marca = models.ForeignKey('Marca', on_delete=models.CASCADE)
    tamano = models.ForeignKey('Tamano', on_delete=models.CASCADE)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)  # Relación con Proveedor
    tienda = models.ForeignKey('Tienda', on_delete=models.CASCADE)        # Relación con Tienda

    def __str__(self):
        return f"{self.nombre} ({self.color.nombre})"


   
class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

# Atributos de los productos.

class Color(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class Marca(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Tamano(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
# Campos de la venta   
class DetalleVenta(models.Model):
    venta = models.ForeignKey('Venta', on_delete=models.CASCADE) 
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE) 
    cantidad = models.PositiveIntegerField()

    def __str__(self):
     return f"Detalle Venta {self.venta.id} - Producto: {self.producto.nombre}"
    
class Venta(models.Model):
    
    
    descripcion = models.TextField(blank=True)
    fecha_venta = models.DateField()
    tipo_venta = models.CharField(max_length=50)  # Por ejemplo, "Crédito" o "Contado"
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Relaciones con otras tablas
    tienda = models.ForeignKey('Tienda', on_delete=models.SET_NULL, null=True)
    vendedor = models.ForeignKey('Vendedor', on_delete=models.CASCADE)  # Relación con Vendedor
    comprobante = models.ForeignKey('Comprobante', on_delete=models.CASCADE)  # Relación con Comprobante
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)  # Relación con Cliente

    def __str__(self):
        return f"Venta {self.id} - Total: {self.total}"
 
class Comprobante(models.Model):
    id_comprobante = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    tipo_comprobante = models.CharField(max_length=50)
    numero_comprobante = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    
    def __str__(self):
        return f"Comprobante {self.numero_comprobante}"

    
class PagoCredito(models.Model):
    venta_credito = models.ForeignKey('VentaCredito', on_delete=models.CASCADE)
    fecha_pago = models.DateField()
    monto_pago = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2)
    


class Vendedor(models.Model):
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre
    
class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    nit = models.CharField(max_length=20, blank=True, null=True)  # Campo NIT agregado

    def __str__(self):
        return f"{self.nombre} - NIT: {self.nit}" if self.nit else self.nombre
    
    
class VentaCredito(models.Model):
    venta = models.OneToOneField('Venta', on_delete=models.CASCADE)  # Relación con Venta
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    numero_cuotas = models.IntegerField()
    interes = models.DecimalField(max_digits=4, decimal_places=2)  # Limita el interés al 99.99%
    fecha_limite = models.DateField()
    saldo_restante = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta Crédito - Cuotas: {self.numero_cuotas}"
    

    