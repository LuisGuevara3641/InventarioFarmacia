# Generated by Django 5.1.2 on 2024-11-03 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0005_remove_detalleventa_precio_unitario_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='fecha',
            field=models.DateTimeField(),
        ),
    ]
