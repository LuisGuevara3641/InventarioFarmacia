from django.db import models
from django.utils import timezone
import pytz

def get_current_time():
    tz = pytz.timezone('America/Guatemala')
    return timezone.localtime(timezone.now(), timezone=tz)

# ---------------------------------- CategoriaProducto ----------------------------------
class CategoriaProducto(models.Model):
    codigo_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=20)
    descripcion_categoria = models.CharField(max_length=250)

    def __str__(self):
        return self.nombre_categoria


# ---------------------------------- Producto ----------------------------------
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    codigo_categoria = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT)  
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField()
    stock_minimo = models.IntegerField(default=10)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    def esta_vencido(self):
        if self.fecha_vencimiento is None:
            return False
        return self.fecha_vencimiento < get_current_time().date()

    def dias_hasta_vencimiento(self):
        if self.fecha_vencimiento:
            hoy = get_current_time().date()
            diferencia = self.fecha_vencimiento - hoy
            return diferencia.days
        return None

    def dias_vencido(self):
        if self.fecha_vencimiento:
            hoy = get_current_time().date()
            return (hoy - self.fecha_vencimiento).days
        return None


# ---------------------------------- Proveedor ----------------------------------
class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)  
    correo = models.EmailField(max_length=50)  

    def __str__(self):
        return self.nombre_proveedor


# ---------------------------------- Pedido ----------------------------------
class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateField()
    total = models.FloatField()

    def __str__(self):
        return f"Pedido {self.id_pedido} - Proveedor: {self.id_proveedor}"


# ---------------------------------- DetallePedido ----------------------------------
class DetallePedido(models.Model):
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_pedido = models.IntegerField()
    total_del_producto = models.FloatField()

    def __str__(self):
        return f"Detalle de Pedido {self.id_pedido} - Producto: {self.id_producto}"

    def save(self, *args, **kwargs):
        # Calcular el total del producto
        self.total_del_producto = self.cantidad_pedido * self.id_producto.precio_compra
        super().save(*args, **kwargs)
        
        # Actualizar el total del pedido sumando todos los detalles
        pedido = self.id_pedido
        pedido.total = DetallePedido.objects.filter(id_pedido=pedido).aggregate(
            total=models.Sum('total_del_producto'))['total'] or 0
        pedido.save()


# ---------------------------------- Cliente ----------------------------------
class Cliente(models.Model):
    nit = models.CharField(max_length=15, primary_key=True) 
    primer_nombre = models.CharField(max_length=25)
    segundo_nombre = models.CharField(max_length=25)
    tercer_nombre = models.CharField(max_length=25, null=True, blank=True)
    primer_apellido = models.CharField(max_length=25)
    segundo_apellido = models.CharField(max_length=25)
    direccion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)  
    correo = models.EmailField(max_length=45)  

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


# ---------------------------------- Venta ----------------------------------
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    nit = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    total_venta = models.FloatField()
    hora = models.TimeField()

    def save(self, *args, **kwargs):
        if not self.pk:  # Si es una nueva venta
            current_time = get_current_time()
            self.fecha = current_time
            self.hora = current_time.time()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Venta {self.id_venta} - Cliente: {self.nit}"


# ---------------------------------- DetalleVenta ----------------------------------
class DetalleVenta(models.Model):
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cantidad_producto = models.IntegerField()

    def __str__(self):
        return f"Detalle de Venta {self.id_venta} - Producto: {self.id_producto}"

    @property
    def subtotal(self):
        return float(self.precio_venta) * float(self.cantidad_producto)

    def save(self, *args, **kwargs):
        # Actualizar el total de la venta al guardar el detalle
        super().save(*args, **kwargs)
        self.id_venta.total_venta = sum(detalle.subtotal for detalle in self.id_venta.detalleventa_set.all())
        self.id_venta.save()

# ---------------------------------- Farmacia ----------------------------------
class Farmacia(models.Model):
    nit_farmacia = models.CharField(max_length=15, primary_key=True)  
    nombre_farmacia = models.CharField(max_length=45)
    telefono_farmacia = models.CharField(max_length=15)  

    def __str__(self):
        return self.nombre_farmacia


# ---------------------------------- Sucursal ----------------------------------
class Sucursal(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nit_farmacia = models.ForeignKey(Farmacia, on_delete=models.CASCADE)
    nombre_sucursal = models.CharField(max_length=45)
    direccion_sucursal = models.CharField(max_length=75)
    telefono_sucursal = models.CharField(max_length=15)  

    def __str__(self):
        return self.nombre_sucursal


# ---------------------------------- Empleado ----------------------------------
class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    primer_nombre = models.CharField(max_length=25)
    segundo_nombre = models.CharField(max_length=25)
    tercer_nombre = models.CharField(max_length=25, null=True, blank=True)
    primer_apellido = models.CharField(max_length=25)
    segundo_apellido = models.CharField(max_length=25)
    direccion_empleado = models.CharField(max_length=150)
    telefono_empleado = models.CharField(max_length=15)  
    correo_empleado = models.EmailField(max_length=50)  
    puesto = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


# ---------------------------------- CategoriaHorario ----------------------------------
class CategoriaHorario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    def __str__(self):
        return f"Horario {self.id_horario}"


# ---------------------------------- TurnosEmpleado ----------------------------------
class TurnosEmpleado(models.Model):
    correlativo = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    id_horario = models.ForeignKey(CategoriaHorario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Turno {self.correlativo} - Empleado: {self.id_empleado}"


# ---------------------------------- Inventario ----------------------------------
class Inventario(models.Model):
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_stock_sucursal = models.IntegerField()

    def __str__(self):
        return f"Inventario Sucursal: {self.id_sucursal} - Producto: {self.id_producto}"