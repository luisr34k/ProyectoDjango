from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import CrearVentaForm, DetalleVentaFormSet, AgregarProductoForm
from django.utils import timezone
from .models import Comprobante, Venta, Producto
from django.db.models import Max
from django.http import JsonResponse



TEMPLATE_DIRS = (
    
    'os.path.join(BASE_DIR, "templates")'
)

@login_required
def home(request):
    return render (request, "index.html")

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
def contado(request):
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

                    venta = form.save(commit=False)
                    venta.comprobante = comprobante
                    venta.save()

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

                # Si todo fue bien, redirigir a la página de contado
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
        form = CrearVentaForm()
        formset = DetalleVentaFormSet()
    
    return render(request, 'crud_ventas/contado.html', {
        'form': form,
        'formset': formset
    })

#funciones Logicas

# Luego, usa esta función para asignar el número de comprobante
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
