from django.contrib import admin
from .models import (
    CategoriaProducto,
    Producto,
    Proveedor,
    Pedido,
    DetallePedido,
    Cliente,
    Venta,
    DetalleVenta,
    Farmacia,
    Sucursal,
    Empleado,
    CategoriaHorario,
    TurnosEmpleado,
    Inventario,
)

admin.site.register(CategoriaProducto)
admin.site.register(Producto)
admin.site.register(Proveedor)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Cliente)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Farmacia)
admin.site.register(Sucursal)
admin.site.register(Empleado)
admin.site.register(CategoriaHorario)
admin.site.register(TurnosEmpleado)
admin.site.register(Inventario)

# luis
# luis8080