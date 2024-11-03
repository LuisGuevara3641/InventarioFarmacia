from django.urls import path
from .views import (
    login_view,
    logout_view,
    lista_productos,
    detalle_producto,
    crear_producto,
    editar_producto,
    eliminar_producto,
    lista_proveedores,
    detalle_proveedor,
    crear_proveedor,
    editar_proveedor,
    eliminar_proveedor,
    lista_clientes,
    detalle_cliente,
    crear_cliente,
    editar_cliente,
    eliminar_cliente,
    lista_ventas,
    crear_venta,
    editar_venta,
    eliminar_venta,
    lista_categorias,
    crear_categoria,
    editar_categoria,
    eliminar_categoria,
    reporte_ventas,
    reporte_stock,
    reporte_vencimientos,
    lista_pedidos,
    crear_pedido,
    detalle_pedido,
    editar_pedido,
    eliminar_pedido,
)

urlpatterns = [
    # URLs para autenticación
    path('login/', login_view, name='login'),  # URL para iniciar sesión
    path('logout/', logout_view, name='logout'),  # URL para cerrar sesión

    # URLs para productos
    path('productos/', lista_productos, name='lista_productos'),
    path('productos/<int:producto_id>/', detalle_producto, name='detalle_producto'),
    path('productos/nuevo/', crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/editar/', editar_producto, name='editar_producto'),
    path('productos/<int:producto_id>/eliminar/', eliminar_producto, name='eliminar_producto'),

    # URLs para proveedores
    path('proveedores/', lista_proveedores, name='lista_proveedores'),
    path('proveedores/<int:proveedor_id>/', detalle_proveedor, name='detalle_proveedor'),
    path('proveedores/nuevo/', crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:proveedor_id>/editar/', editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:proveedor_id>/eliminar/', eliminar_proveedor, name='eliminar_proveedor'),

    # URLs para clientes
    path('clientes/', lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', crear_cliente, name='crear_cliente'),  
    path('clientes/<str:nit>/', detalle_cliente, name='detalle_cliente'),
    path('clientes/<str:nit>/editar/', editar_cliente, name='editar_cliente'),
    path('clientes/<str:nit>/eliminar/', eliminar_cliente, name='eliminar_cliente'),

    # URLs para ventas
    path('ventas/', lista_ventas, name='lista_ventas'),
    path('ventas/nueva/', crear_venta, name='crear_venta'),
    path('ventas/<int:venta_id>/editar/', editar_venta, name='editar_venta'),
    path('ventas/<int:venta_id>/eliminar/', eliminar_venta, name='eliminar_venta'),

    # URLs para categorías
    path('categorias/', lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', crear_categoria, name='crear_categoria'),
    path('categorias/<int:categoria_id>/editar/', editar_categoria, name='editar_categoria'),
    path('categorias/<int:categoria_id>/eliminar/', eliminar_categoria, name='eliminar_categoria'),

    # URLs para reportes
    path('reportes/ventas/', reporte_ventas, name='reporte_ventas'),
    path('reportes/stock/', reporte_stock, name='reporte_stock'),
    path('reportes/vencimientos/', reporte_vencimientos, name='reporte_vencimientos'),

    # URLs para pedidos
    path('pedidos/', lista_pedidos, name='lista_pedidos'),
    path('pedidos/crear/', crear_pedido, name='crear_pedido'),
    path('pedidos/<int:pedido_id>/', detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pedido_id>/editar/', editar_pedido, name='editar_pedido'),
    path('pedidos/<int:pedido_id>/eliminar/', eliminar_pedido, name='eliminar_pedido'),
]