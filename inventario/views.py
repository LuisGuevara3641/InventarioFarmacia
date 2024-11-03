from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Sum, Count, F, Value, DurationField, ExpressionWrapper
from django.db.models.functions import TruncDate, Abs
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.http import FileResponse
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import group_required
import os

# ---------------------------------- Vista para iniciar sesión ----------------------------------
def login_view(request):
    # Si el usuario ya está autenticado
    if request.user.is_authenticated:
        # Agregar mensaje de depuración
        print(f"Usuario autenticado: {request.user.username}")
        print(f"Grupos del usuario: {list(request.user.groups.all())}")
        
        if request.user.groups.filter(name='Administradores').exists():
            print("Usuario es Administrador")
            return redirect('lista_productos')
        elif request.user.groups.filter(name='Empleados').exists():
            print("Usuario es Empleado")
            return redirect('lista_clientes')
        else:
            print("Usuario sin grupo")
            messages.warning(request, 'Usuario no asignado a ningún grupo.')
            logout(request)
            return redirect('login')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Agregar mensaje de depuración antes del login
            print(f"Usuario autenticado: {user.username}")
            print(f"Grupos del usuario: {list(user.groups.all())}")
            
            login(request, user)
            
            # Verificar grupo después del login
            if user.groups.filter(name='Administradores').exists():
                print("Usuario es Administrador")
                return redirect('lista_productos')
            elif user.groups.filter(name='Empleados').exists():
                print("Usuario es Empleado")
                return redirect('lista_clientes')
            else:
                print("Usuario sin grupo")
                messages.warning(request, 'Usuario no asignado a ningún grupo.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    
    return render(request, 'inventario/login.html')

# ---------------------------------- Vista para cerrar sesión ----------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')  # Redirige a la página de login

# ---------------------------------- Vista para listar productos ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def lista_productos(request):
    productos = Producto.objects.select_related('codigo_categoria').all()  # Optimización de consulta
    return render(request, 'inventario/lista_productos.html', {'productos': productos})

# ---------------------------------- Vista para ver detalles de un producto ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    return render(request, 'inventario/detalle_producto.html', {'producto': producto})

# ---------------------------------- Vista para crear un nuevo producto ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Error al crear el producto. Verifica los datos ingresados.')
    else:
        form = ProductoForm()
    return render(request, 'inventario/crear_producto.html', {'form': form})

# ---------------------------------- Vista para editar un producto ----------------------------------
@login_required
@group_required('Administradores')
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Producto actualizado exitosamente.')
                return redirect('lista_productos')
            except Exception as e:
                messages.error(request, f'Error al guardar el producto: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
            print("Form errors:", form.errors)  # Para debugging
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'inventario/editar_producto.html', {
        'form': form,
        'producto': producto,
        'now': timezone.now().date()
    })

# ---------------------------------- Vista para eliminar un producto ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado exitosamente.')
    return redirect('lista_productos')

# ---------------------------------- Vista para listar proveedores ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'inventario/lista_proveedores.html', {'proveedores': proveedores})

# ---------------------------------- Vista para ver detalles de un proveedor ----------------------------------
@login_required
@group_required('Administradores')
def detalle_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    # Obtener todos los productos únicos de los pedidos del proveedor
    productos_suministrados = Producto.objects.filter(
        detallepedido__id_pedido__id_proveedor=proveedor
    ).distinct()
    
    context = {
        'proveedor': proveedor,
        'productos_suministrados': productos_suministrados,
    }
    return render(request, 'inventario/detalle_proveedor.html', context)

# ---------------------------------- Vista para crear un nuevo proveedor ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente.')
            return redirect('lista_proveedores')
        else:
            messages.error(request, 'Error al crear el proveedor. Verifica los datos ingresados.')
    else:
        form = ProveedorForm()
    return render(request, 'inventario/crear_proveedor.html', {'form': form})

# ---------------------------------- Vista para editar un proveedor ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
            return redirect('lista_proveedores')
        else:
            messages.error(request, 'Error al actualizar el proveedor. Verifica los datos ingresados.')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'inventario/editar_proveedor.html', {'form': form})

# ---------------------------------- Vista para eliminar un proveedor ----------------------------------
@login_required
@group_required('Administradores')  # Solo accesible para administradores
def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id_proveedor=proveedor_id)
    proveedor.delete()
    messages.success(request, 'Proveedor eliminado exitosamente.')
    return redirect('lista_proveedores')

# ---------------------------------- Vista para listar clientes ----------------------------------
@login_required
@group_required('Administradores','Empleados')  # Accesible para empleados
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'inventario/lista_clientes.html', {'clientes': clientes})

# ---------------------------------- Vista para ver detalles de un cliente ----------------------------------
@login_required
@group_required('Administradores','Empleados') # Accesible para empleados
def detalle_cliente(request, nit):
    cliente = get_object_or_404(Cliente, nit=nit)
    return render(request, 'inventario/detalle_cliente.html', {'cliente': cliente})

# ---------------------------------- Vista para crear un nuevo cliente ----------------------------------
@login_required
@group_required('Administradores','Empleados')  # Accesible para empleados
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('lista_clientes')
        else:
            messages.error(request, 'Error al crear el cliente. Verifica los datos ingresados.')
    else:
        form = ClienteForm()
    return render(request, 'inventario/crear_cliente.html', {'form': form})

# ---------------------------------- Vista para editar un cliente ----------------------------------
@login_required
@group_required('Administradores','Empleados') # Accesible para empleados
def editar_cliente(request, nit):
    cliente = get_object_or_404(Cliente, nit=nit)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('lista_clientes')
        else:
            messages.error(request, 'Error al actualizar el cliente. Verifica los datos ingresados.')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'inventario/editar_cliente.html', {'form': form})

# ---------------------------------- Vista para eliminar un cliente ----------------------------------
@login_required
@group_required('Administradores','Empleados')  # Accesible para empleados
def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, nit=cliente_id)
    cliente.delete()
    messages.success(request, 'Cliente eliminado exitosamente.')
    return redirect('lista_clientes')

# ---------------------------------- Vista para listar ventas ----------------------------------
@login_required
@group_required('Administradores','Empleados')  # Accesible para empleados
def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'inventario/lista_ventas.html', {'ventas': ventas})

# ---------------------------------- Vista para crear una nueva venta ----------------------------------
@login_required
@group_required('Administradores','Empleados')
def crear_venta(request):
    clientes = Cliente.objects.all()
    productos = Producto.objects.filter(stock__gt=0)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear la venta
                venta = Venta.objects.create(
                    nit_id=request.POST.get('cliente'),  
                    total_venta=0
                )

                producto_id = request.POST.get('productos')
                cantidad = int(request.POST.get('cantidad'))
                producto = Producto.objects.get(id_producto=producto_id)

                # Verificar stock
                if producto.stock < cantidad:
                    raise ValidationError('Stock insuficiente')

                # Crear detalle de venta
                detalle = DetalleVenta.objects.create(
                    id_venta=venta,
                    id_producto=producto,
                    cantidad_producto=cantidad,
                    precio_venta=producto.precio_venta
                )

                # Actualizar stock
                producto.stock -= cantidad
                producto.save()

                # Actualizar total de la venta
                venta.total_venta = detalle.subtotal
                venta.save()

                messages.success(request, 'Venta creada exitosamente')
                return redirect('lista_ventas')

        except ValidationError as e:
            messages.error(request, str(e))
            if 'venta' in locals():
                venta.delete()
            return redirect('crear_venta')
        except Exception as e:
            messages.error(request, f'Error al crear la venta: {str(e)}')
            if 'venta' in locals():
                venta.delete()
            return redirect('crear_venta')

    return render(request, 'inventario/crear_venta.html', {
        'clientes': clientes,
        'productos': productos
    })
# ---------------------------------- Vista para editar una venta ----------------------------------
@login_required
@group_required('Administradores','Empleados')
def editar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id_venta=venta_id)
    clientes = Cliente.objects.all()
    productos = Producto.objects.all()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                venta.nit_id = request.POST.get('cliente')
                
                productos_nuevos = request.POST.getlist('productos[]')
                cantidades = request.POST.getlist('cantidad[]')

                # Crear un diccionario de los nuevos datos
                nuevos_detalles = dict(zip(productos_nuevos, cantidades))

                # Manejar detalles existentes
                for detalle in venta.detalleventa_set.all():
                    producto_id = str(detalle.id_producto.id_producto)
                    
                    if producto_id not in productos_nuevos:
                        # Devolver stock si el producto fue eliminado
                        detalle.id_producto.stock += detalle.cantidad_producto
                        detalle.id_producto.save()
                        detalle.delete()
                    else:
                        # Actualizar cantidad si cambió
                        nueva_cantidad = int(nuevos_detalles[producto_id])
                        if nueva_cantidad != detalle.cantidad_producto:
                            # Actualizar stock
                            diferencia = nueva_cantidad - detalle.cantidad_producto
                            if diferencia > 0:
                                if detalle.id_producto.stock < diferencia:
                                    raise ValidationError(f'Stock insuficiente para {detalle.id_producto.nombre}')
                                detalle.id_producto.stock -= diferencia
                            else:
                                detalle.id_producto.stock -= diferencia
                            detalle.id_producto.save()
                            detalle.cantidad_producto = nueva_cantidad
                            detalle.save()
                        
                        # Remover este producto del diccionario de nuevos detalles
                        del nuevos_detalles[producto_id]

                # Agregar nuevos productos
                for producto_id, cantidad in nuevos_detalles.items():
                    producto = Producto.objects.get(id_producto=producto_id)
                    cantidad = int(cantidad)
                    
                    if producto.stock < cantidad:
                        raise ValidationError(f'Stock insuficiente para {producto.nombre}')
                    
                    # Crear nuevo detalle
                    DetalleVenta.objects.create(
                        id_venta=venta,
                        id_producto=producto,
                        cantidad_producto=cantidad,
                        precio_venta=producto.precio_venta
                    )
                    
                    # Actualizar stock
                    producto.stock -= cantidad
                    producto.save()

                messages.success(request, 'Venta actualizada exitosamente')
                return redirect('lista_ventas')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al actualizar la venta: {str(e)}')

    return render(request, 'inventario/editar_venta.html', {
        'venta': venta,
        'clientes': clientes,
        'productos': productos
    })

# ---------------------------------- Vista para eliminar una venta ----------------------------------
@login_required
@group_required('Administradores','Empleados')  # Accesible para empleados
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id_venta=venta_id)
    venta.delete()
    messages.success(request, 'Venta eliminada exitosamente.')
    return redirect('lista_ventas')

# ---------------------------------- Vistas de Reportes ----------------------------------
@login_required
@group_required('Administradores')
def reporte_ventas(request):
    # Obtener fechas del filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Query base
    ventas = Venta.objects.all()
    
    # Aplicar filtros si existen
    if fecha_inicio and fecha_fin:
        ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
    
    # Calcular totales
    total_ventas = ventas.count()
    total_ingresos = ventas.aggregate(Sum('total_venta'))['total_venta__sum'] or 0
    
    # Agrupar ventas por día
    ventas_por_dia = ventas.annotate(
        dia=TruncDate('fecha')
    ).values('dia').annotate(
        total=Sum('total_venta'),
        cantidad=Count('id_venta')
    ).order_by('dia')

    context = {
        'ventas': ventas,
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'ventas_por_dia': ventas_por_dia,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'inventario/reportes/ventas.html', context)

@login_required
@group_required('Administradores')
def reporte_stock(request):
    productos = Producto.objects.all().select_related('codigo_categoria')
    
    # Productos con stock bajo
    productos_stock_bajo = productos.filter(stock__lte=F('stock_minimo'))
    
    # Productos agotados
    productos_agotados = productos.filter(stock=0)
    
    # Productos por categoría
    categorias = CategoriaProducto.objects.annotate(
        total_productos=Count('producto'),
        valor_total=Sum(F('producto__stock') * F('producto__precio_venta'), default=0)
    )

    context = {
        'productos': productos,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_agotados': productos_agotados,
        'categorias': categorias,
    }
    return render(request, 'inventario/reportes/stock.html', context)

@login_required
@group_required('Administradores')
def reporte_vencimientos(request):
    # Obtener la fecha actual
    hoy = get_current_time().date()
    
    # Productos próximos a vencer (30 días)
    proximos_a_vencer = Producto.objects.filter(
        fecha_vencimiento__gt=hoy,
        fecha_vencimiento__lte=hoy + timezone.timedelta(days=30)
    ).order_by('fecha_vencimiento')

    # Productos ya vencidos
    productos_vencidos = Producto.objects.filter(
        fecha_vencimiento__lt=hoy
    ).order_by('fecha_vencimiento')

    # Contar productos
    total_proximos = proximos_a_vencer.count()
    total_vencidos = productos_vencidos.count()

    context = {
        'proximos_a_vencer': proximos_a_vencer,
        'productos_vencidos': productos_vencidos,
        'total_proximos': total_proximos,
        'total_vencidos': total_vencidos,
        'fecha_actual': hoy,
    }

    return render(request, 'inventario/reportes/vencimientos.html', context)

# ---------------------------------- Vista para listar pedidos ----------------------------------
@login_required
@group_required('Administradores')
def lista_pedidos(request):
    pedidos = Pedido.objects.select_related('id_proveedor').all()
    return render(request, 'inventario/pedidos/lista_pedidos.html', {'pedidos': pedidos})

# ---------------------------------- Vista para crear un nuevo pedido ----------------------------------
@login_required
@group_required('Administradores')
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    pedido = form.save(commit=False)
                    pedido.fecha = get_current_time()
                    pedido.total = 0
                    pedido.save()

                    productos = request.POST.getlist('productos[]')
                    cantidades = request.POST.getlist('cantidades[]')
                    total_pedido = 0

                    for producto_id, cantidad in zip(productos, cantidades):
                        producto = get_object_or_404(Producto, id_producto=producto_id)
                        cantidad = int(cantidad)
                        subtotal = producto.precio_compra * cantidad

                        # Crear detalle del pedido
                        DetallePedido.objects.create(
                            id_pedido=pedido,
                            id_producto=producto,
                            cantidad_pedido=cantidad,
                            total_del_producto=subtotal
                        )

                        # Actualizar el stock del producto
                        producto.stock += cantidad
                        producto.save()

                        total_pedido += subtotal

                    pedido.total = total_pedido
                    pedido.save()

                    messages.success(request, 'Pedido creado exitosamente y stock actualizado.')
                    return redirect('lista_pedidos')

            except Exception as e:
                messages.error(request, f'Error al crear el pedido: {str(e)}')
                return redirect('crear_pedido')
    else:
        form = PedidoForm()

    context = {
        'form': form,
        'proveedores': Proveedor.objects.all(),
        'productos': Producto.objects.all(),
    }
    return render(request, 'inventario/pedidos/crear_pedido.html', context)

# ---------------------------------- Vista para ver detalles de un pedido ----------------------------------
@login_required
@group_required('Administradores')
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    detalles = DetallePedido.objects.filter(id_pedido=pedido).select_related('id_producto')
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
    }
    return render(request, 'inventario/pedidos/detalle_pedido.html', context)

# ---------------------------------- Vista para editar un pedido ----------------------------------
@login_required
@group_required('Administradores')
def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    detalles = DetallePedido.objects.filter(id_pedido=pedido)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                cantidad_nueva = int(request.POST.get('cantidades[]', 0))
                if cantidad_nueva <= 0:
                    raise ValidationError('La cantidad debe ser mayor a 0')

                detalle = detalles.first()
                if not detalle:
                    raise ValidationError('No se encontró el detalle del pedido')

                # Guardar cantidad anterior para restaurar si hay error
                cantidad_anterior = detalle.cantidad_pedido
                
                try:
                    # Calcular la diferencia de cantidad
                    diferencia = cantidad_nueva - cantidad_anterior
                    
                    # Actualizar el stock del producto
                    producto = detalle.id_producto
                    producto.stock += diferencia  # Aumentamos el stock si es positivo, disminuimos si es negativo
                    producto.save()
                    
                    # Actualizar detalle y pedido
                    detalle.cantidad_pedido = cantidad_nueva
                    detalle.save()
                    
                    pedido.total = cantidad_nueva * detalle.id_producto.precio_compra
                    pedido.save()
                    
                    messages.success(request, 'Pedido actualizado exitosamente')
                    return redirect('lista_pedidos')
                except Exception as e:
                    # Restaurar cantidad anterior si hay error
                    detalle.cantidad_pedido = cantidad_anterior
                    producto.stock -= diferencia  # Revertir el cambio en el stock
                    producto.save()
                    raise e

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al actualizar el pedido: {str(e)}')

    context = {
        'pedido': pedido,
        'detalles': detalles,
    }
    
    return render(request, 'inventario/pedidos/editar_pedido.html', context)


# ---------------------------------- Vista para eliminar un pedido ----------------------------------
@login_required
@group_required('Administradores')
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    try:
        pedido.delete()
        messages.success(request, 'Pedido eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el pedido: {str(e)}')
    return redirect('lista_pedidos')

# ---------------------------------- Vista para listar categorías ----------------------------------
@login_required
@group_required('Administradores')
def lista_categorias(request):
    categorias = CategoriaProducto.objects.all().order_by('nombre_categoria')
    return render(request, 'inventario/categorias/lista_categorias.html', {'categorias': categorias})

# ---------------------------------- Vista para crear categoría ----------------------------------
@login_required
@group_required('Administradores')
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Categoría creada exitosamente.')
                return redirect('lista_categorias')
            except Exception as e:
                messages.error(request, f'Error al crear la categoría: {str(e)}')
    else:
        form = CategoriaForm()
    
    return render(request, 'inventario/categorias/crear_categoria.html', {'form': form})

# ---------------------------------- Vista para editar categoría ----------------------------------
@login_required
@group_required('Administradores')
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaProducto, codigo_categoria=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Categoría actualizada exitosamente.')
                return redirect('lista_categorias')
            except Exception as e:
                messages.error(request, f'Error al actualizar la categoría: {str(e)}')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'inventario/categorias/editar_categoria.html', {
        'form': form,
        'categoria': categoria
    })

# ---------------------------------- Vista para eliminar categoría ----------------------------------
@login_required
@group_required('Administradores')
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaProducto, codigo_categoria=categoria_id)
    try:
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    return redirect('lista_categorias')