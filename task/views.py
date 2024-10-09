#views.py
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse

# Third-party imports
from rest_framework import generics

# Local app imports
from .forms import CrearVentaForm, DetalleVentaFormSet, AgregarProductoForm, MarcaForm, ColorForm, CrearVentaCreditoForm, DetalleVentaFormSetCredito
from .models import Comprobante, Venta, Producto, Marca, Color, VentaCredito
from .serializers import MarcaSerializer, ColorSerializer




TEMPLATE_DIRS = (
    
    'os.path.join(BASE_DIR, "templates")'
)


@login_required
def home(request):
    return render (request, "index.html")

#funciones signin, signup, logout

@login_required
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, 'signup.html', {"form": UserCreationForm, "error": "Username already exists."})

        return render(request, 'signup.html', {"form": UserCreationForm, "error": "Passwords did not match."})
   
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        return redirect('home') 
    
@login_required
def logout_view(request):
    logout(request)
    return redirect('signin')  # Redirige a la página de inicio de sesión

#funciones crud ventas

@login_required       
def listar(request):
    
    venta = Venta.objects.all()
         
    return render (request, 'crud_ventas/listar.html', {
        'venta' : venta
    }) 

@login_required
def productos(request):
    
    producto = Producto.objects.all()
    
    return render (request, 'crud_ventas/productos.html', {
        'producto' : producto
    })

@login_required    
def credito(request):
    return render (request, 'crud_ventas/credito.html') 

@login_required   
def ventas(request):
    return render (request, 'crud_ventas/ventas.html')   

@login_required 
def alertas(request):
    return render (request, 'crud_ventas/alertas.html')  


@login_required
def agregarProducto(request):
    if request.method == 'POST':
        form = AgregarProductoForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo producto en la base de datos
            return redirect('productos')  # Redirige a la página de lista de productos después de guardar
        else:
            print(form.errors)  # Imprimir errores en la consola
    else:
        form = AgregarProductoForm()
    
    return render(request, 'crud_ventas/AgregarProducto.html', {
        'form': form
    })


@login_required
def pagos(request):
    return render (request, 'crud_ventas/pagos.html')   

@login_required
def marcas(request):
    return render (request, 'elementos/marcas.html') 

@login_required
def venta_contado(request):
    if request.method == 'POST':
        print("Formulario enviado correctamente")  # Verifica que el POST se está ejecutando
        form = CrearVentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    print("Formulario y formset válidos")  # Verifica que los formularios son válidos
                    # Lógica de guardar la venta
                    comprobante_number = generate_comprobante_number()

                    comprobante = Comprobante(
                        nombre='Comprobante de Venta',
                        tipo_comprobante='Venta Contado',
                        numero_comprobante=comprobante_number,
                        fecha_emision=timezone.now()
                    )
                    comprobante.save()

                    # Guardar la venta con el tipo de venta 'Contado'
                    venta = form.save(commit=False)
                    venta.comprobante = comprobante
                    venta.tipo_venta = 'Contado'  # Establecer el tipo de venta a 'Contado'
                    venta.save()

                    # Guardar los detalles de la venta
                    detalles = formset.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        
                        # Disminuir la cantidad de stock del producto
                        producto = detalle.producto
                        if producto.stock >= detalle.cantidad:
                            producto.stock -= detalle.cantidad
                            producto.save()
                        else:
                            # Lanza un error si el stock no es suficiente
                            raise ValueError(f"Stock insuficiente para el producto: {producto.nombre}")
                        
                        detalle.save()

                # Si todo fue bien, redirigir a la página de listado
                return redirect('listar')

            except Exception as e:
                # Si ocurre cualquier error, se hará un rollback y se mostrará el error
                form.add_error(None, str(e))
                print(f"Error al procesar la venta: {e}")
        else:
            print("Formulario o formset no válidos")  # Debug en caso de error de validación
            print(form.errors)  # Muestra los errores del formulario principal
            print(formset.errors)  # Muestra los errores del formset
    else:
        # Inicializar el formulario con tipo_venta='Contado'
        form = CrearVentaForm(initial={'tipo_venta': 'Contado'})  # Asegurar que tipo_venta es 'Contado'
        formset = DetalleVentaFormSet()
    
    return render(request, 'crud_ventas/venta_contado.html', {
        'form': form,
        'formset': formset
    })

@login_required
def venta_credito(request):
    if request.method == 'POST':
        form_venta = CrearVentaForm(request.POST)
        form_credito = CrearVentaCreditoForm(request.POST)
        formset = DetalleVentaFormSetCredito(request.POST)

        # Obtener el nuevo total calculado desde el formulario
        nuevo_total = request.POST.get('nuevo_total_input')

        if form_venta.is_valid() and form_credito.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Generar número de comprobante
                    comprobante_number = generate_comprobante_number()

                    # Crear y guardar el comprobante
                    comprobante = Comprobante(
                        nombre='Comprobante de Venta a Crédito',
                        tipo_comprobante='Venta Crédito',
                        numero_comprobante=comprobante_number,
                        fecha_emision=timezone.now()
                    )
                    comprobante.save()

                    # Guardar la venta con el tipo de venta 'Crédito'
                    venta = form_venta.save(commit=False)
                    venta.comprobante = comprobante
                    venta.tipo_venta = 'Crédito'
                    venta.total = nuevo_total  # Asignar el nuevo total calculado
                    venta.save()

                    # Guardar los detalles de la venta
                    detalles = formset.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        producto = detalle.producto
                        if producto.stock >= detalle.cantidad:
                            producto.stock -= detalle.cantidad
                            producto.save()
                        else:
                            raise ValueError(f"Stock insuficiente para el producto: {producto.nombre}")
                        detalle.save()

                    # Guardar la información del crédito
                    venta_credito = form_credito.save(commit=False)
                    venta_credito.venta = venta
                    venta_credito.saldo_restante = float(nuevo_total) - float(venta_credito.monto_inicial)
                    venta_credito.save()

                return redirect('listar')

            except Exception as e:
                form_venta.add_error(None, str(e))

    else:
        # Inicializar el formulario de venta con tipo_venta='Crédito'
        form_venta = CrearVentaForm(initial={'tipo_venta': 'Crédito'})
        form_credito = CrearVentaCreditoForm()
        formset = DetalleVentaFormSetCredito()

    return render(request, 'crud_ventas/venta_credito.html', {
        'form_venta': form_venta,
        'form_credito': form_credito,
        'formset': formset,
    })

@login_required
def pendiente_pago(request):
    # Obtener todas las ventas que aún tienen saldo pendiente
    ventas_pendientes = VentaCredito.objects.filter(saldo_restante__gt=0)
    
    return render(request, 'crud_ventas/pendiente_pago.html', {
        'ventas_pendientes': ventas_pendientes
    })
  
class MarcaListCreate(generics.ListCreateAPIView):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    
def agregar_marca(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('marcas')  # Redirige a la lista de marcas después de guardar
    else:
        form = MarcaForm()
    return render(request, 'elementos/marcas.html', {'form': form})

class ColorListCreate(generics.ListCreateAPIView):
    queryset = Color.objects.all()  # Cambia Marca a Color
    serializer_class = ColorSerializer
    
def agregar_color(request):
    if request.method == 'POST':
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('colores')  # Redirige a la lista de marcas después de guardar
    else:
        form = ColorForm()
    return render(request, 'elementos/colores.html', {'form': form})

@login_required
def descargar_comprobante_pdf(request, venta_id):
    # Obtener la venta seleccionada
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Definir el contexto para la plantilla
    context = {
        'venta': venta,
        'detalles': venta.detalleventa_set.all(),  # Obtener los detalles de la venta
    }
    
    # Renderizar la plantilla a un string
    template = render_to_string('elementos/pdf_comprobante.html', context)

    # Crear el objeto HttpResponse con el contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante_{venta.comprobante.numero_comprobante}.pdf"'

    # Convertir el HTML a PDF
    pisa_status = pisa.CreatePDF(template, dest=response)

    # Verificar si hubo errores
    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF', status=400)
    
    return response

#funciones Logicas

def generate_comprobante_number():
    last_comprobante = Comprobante.objects.aggregate(Max('numero_comprobante'))
    last_number = last_comprobante['numero_comprobante__max']
    
    if last_number:
        # Extrae la parte numérica del último número
        prefix = 'ABC'  # Prefijo fijo para la parte alfabética
        last_numeric_part = last_number[len(prefix):]  # Obtén la parte numérica
        new_number = str(int(last_numeric_part) + 1).zfill(len(last_numeric_part))
        new_comprobante_number = prefix + new_number
    else:
        new_comprobante_number = 'ABC00001'
    
    return new_comprobante_number

def obtener_producto(request):
    producto_id = request.GET.get('producto_id')
    if producto_id:
        producto = Producto.objects.get(id=producto_id)
        data = {
            'precio': str(producto.precio_venta),
            'color': producto.color.nombre,
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Producto no encontrado'}, status=404)

def buscar_producto(request):
    query = request.GET.get('query', '')
    if query:
        productos = Producto.objects.filter(nombre__icontains=query)  # Filtrar productos por nombre
        resultados = []
        for producto in productos:
            resultados.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio_venta),
                'color': producto.color.nombre,  # Asumiendo que tienes un campo relacionado llamado 'color'
                'stock': producto.stock,  # Agregar el stock disponible
                
            })
        return JsonResponse({'resultados': resultados})
    return JsonResponse({'resultados': []})

def obtener_notificaciones(request):
    # Productos con stock crítico
    stock_urgente = Producto.objects.filter(stock=0)
    stock_alerta = Producto.objects.filter(stock__lte=3, stock__gt=0) 
    
    notificaciones = []
    
    # Agrega notificación de stock urgente
    for producto in stock_urgente:
        notificaciones.append({
            'mensaje': f'El producto {producto.nombre} está agotado.',
            'tipo': 'urgente'
        })

    # Agrega notificación de stock bajo
    for producto in stock_alerta:
        notificaciones.append({
            'mensaje': f'El producto {producto.nombre} tiene un stock bajo.',
            'tipo': 'alerta'
        })
    
    # Limita las notificaciones a mostrar
    max_notificaciones = 7
    notificaciones_limitadas = notificaciones[:max_notificaciones]
    
    # Comprueba si hay más notificaciones que las mostradas
    hay_mas_notificaciones = len(notificaciones) > max_notificaciones

    response_data = {
        'notificaciones': notificaciones_limitadas,
        'hay_mas': hay_mas_notificaciones,
        'total_notificaciones': len(notificaciones)  # Devuelve el total real de notificaciones
    }

    return JsonResponse(response_data, safe=False)
