#forms.py
from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import Venta, DetalleVenta, Producto, Marca

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre']  # Cambia esto según tus necesidades
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Marca'}),
        }

class AgregarProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_compra', 'precio_venta', 'stock', 'color', 'marca', 'tamano', 'proveedor', 'tienda']  # Incluye 'tienda'
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.Select(attrs={'class': 'form-control'}),
            'tamano': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'tienda': forms.Select(attrs={'class': 'form-control'}),  # Incluye 'tienda' con su widget
        }


class DetalleVentaForm(forms.ModelForm):
    producto_busqueda = forms.CharField(label='Buscar Producto', widget=forms.TextInput(attrs={'class': 'producto-buscador'}))
    
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.HiddenInput(),
            'cantidad': forms.NumberInput(attrs={'value': '1', 'readonly': True}),
        }


class CrearVentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['descripcion', 'fecha_venta', 'tipo_venta', 'total', 'tienda', 'vendedor', 'cliente']
        widgets = {
            'fecha_venta': forms.DateInput(attrs={'type': 'date'}),
            'tipo_venta': forms.TextInput(attrs={'value': 'Contado', 'readonly': True}),
        }


DetalleVentaFormSet = inlineformset_factory(Venta, DetalleVenta, form=DetalleVentaForm, extra=1)

