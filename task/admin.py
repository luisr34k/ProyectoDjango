from django.contrib import admin
from .models import Tienda, Producto, Proveedor, Color, Marca, Tamano, Vendedor, Cliente, Comprobante, Venta, VentaCredito, DetalleVenta, PagoCredito

# Registrar los modelos en el sitio de administración
admin.site.register(Tienda)
admin.site.register(Producto)
admin.site.register(Proveedor)
admin.site.register(Color)
admin.site.register(Marca)
admin.site.register(Tamano)

# Nuevos modelos agregados
admin.site.register(Vendedor)
admin.site.register(Cliente)
admin.site.register(Comprobante)
admin.site.register(Venta)
admin.site.register(VentaCredito)
admin.site.register(DetalleVenta)
admin.site.register(PagoCredito)

# Register your models here.
