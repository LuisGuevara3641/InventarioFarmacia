from django import forms
from .models import Producto, Proveedor, Cliente, Venta, CategoriaProducto, Pedido

# ---------------------------------- Formulario para Producto ----------------------------------
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo_categoria', 'nombre', 'descripcion', 'precio_venta', 'precio_compra', 'stock', 'stock_minimo', 'fecha_vencimiento']
        widgets = {
            'codigo_categoria': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del producto'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio de venta'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio de compra'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock mínimo'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# ---------------------------------- Formulario para Proveedor ----------------------------------
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_proveedor', 'direccion', 'telefono', 'correo']
        widgets = {
            'nombre_proveedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

# ---------------------------------- Formulario para Cliente ----------------------------------
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'nit', 'direccion', 'telefono', 'correo']
        widgets = {
            'primer_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer nombre'}),
            'segundo_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo nombre'}),
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer apellido'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo apellido'}),
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

# ---------------------------------- Formulario para Venta ----------------------------------
class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['nit', 'total_venta']  # Puedes agregar más campos según sea necesario
        widgets = {
            'nit': forms.Select(attrs={'class': 'form-control'}),
            'total_venta': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total de la venta'}),
        }

# ---------------------------------- Forms para Pedidos ----------------------------------
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['id_proveedor', 'fecha']
        labels = {
            'id_proveedor': 'Proveedor',
            'fecha': 'Fecha del Pedido',
        }
        widgets = {
            'id_proveedor': forms.Select(
                attrs={
                    'class': 'form-control',
                    'required': True
                }
            ),
            'fecha': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'required': True
                }
            )
        }

class DetallePedidoFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        productos = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                producto = form.cleaned_data.get('id_producto')
                if producto in productos:
                    raise forms.ValidationError(
                        'No puedes agregar el mismo producto más de una vez.'
                    )
                productos.append(producto)

# ---------------------------------- Formulario para Categoría ----------------------------------
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre_categoria', 'descripcion_categoria']  # Cambiado para coincidir con el modelo
        widgets = {
            'nombre_categoria': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre de la categoría',
                'required': True
            }),
            'descripcion_categoria': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Descripción de la categoría',
                'rows': '3'
            }),
        }
        labels = {
            'nombre_categoria': 'Nombre de la Categoría',
            'descripcion_categoria': 'Descripción',
        }
        error_messages = {
            'nombre_categoria': {
                'required': 'El nombre de la categoría es obligatorio.',
                'unique': 'Ya existe una categoría con este nombre.'
            }
        }