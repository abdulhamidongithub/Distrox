# Generated by Django 5.0.1 on 2024-04-08 04:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0003_alter_warehouseproduct_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouseproduct',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='warehouseproduct',
            name='date_time',
        ),
        migrations.CreateModel(
            name='WarehouseProductArrival',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('warehouse_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouses.warehouseproduct')),
            ],
        ),
    ]
