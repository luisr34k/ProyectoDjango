#urls.py from task
from django.contrib import admin
from django.urls import path
from . import views
from .views import MarcaListCreate, descargar_comprobante_pdf


urlpatterns = [
    #path('admin', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('listar/', views.listar, name='listar'),
    path('pagos/', views.pagos, name='pagos'),
    path('contado/', views.contado, name='contado'),
    path('credito/', views.credito, name='credito'),
    path('alertas/', views.alertas, name='alertas'),
    path('productos/', views.productos, name='productos'),
    path('AgregarProducto/', views.agregarProducto, name='AgregarProducto'),
    path('obtener_producto/', views.obtener_producto, name='obtener_producto'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    path('marcas/', MarcaListCreate.as_view(), name='marcas'),
    path('marcas/agregar/', views.agregar_marca, name='agregar_marca'),
    path('descargar_comprobante/<int:venta_id>/', descargar_comprobante_pdf, name='descargar_comprobante'),
    
]
