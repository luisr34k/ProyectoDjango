#urls.py from task
from django.contrib import admin
from django.urls import path
from . import views
from .views import MarcaListCreate, ColorListCreate, descargar_comprobante_pdf


urlpatterns = [
    #path('admin', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('listar/', views.listar, name='listar'),
    path('pagos/', views.pagos, name='pagos'),
    path('crear_cliente/', views.crear_cliente, name='crear_cliente'),
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('buscar_cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('venta_contado/', views.venta_contado, name='venta_contado'),
    path('venta_credito/', views.venta_credito, name='venta_credito'),
    path('abonar/<int:venta_id>/', views.abonar, name='abonar'),
    path('pendiente_pago/', views.pendiente_pago, name='pendiente_pago'),
    path('alertas/', views.alertas, name='alertas'),
    path('productos/', views.productos, name='productos'),
    path('categorias/', views.categorias, name='categorias'),
    path('AgregarProducto/', views.agregarProducto, name='AgregarProducto'),
    path('obtener_producto/', views.obtener_producto, name='obtener_producto'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    path('marcas/', MarcaListCreate.as_view(), name='marcas'),
    path('marcas/agregar/', views.agregar_marca, name='agregar_marca'),
    path('colores/', ColorListCreate.as_view(), name='colores'),
    path('colores/agregar/', views.agregar_color, name='agregar_color'),  
    path('descargar_comprobante/<int:venta_id>/', descargar_comprobante_pdf, name='descargar_comprobante'),
    path('descargar_comprobante_pago/<int:pago_id>/', views.descargar_comprobante_pago, name='descargar_comprobante_pago'),
    path('obtener_notificaciones/', views.obtener_notificaciones, name='obtener_notificaciones'), 
]
