# Generated by Django 5.0.1 on 2024-05-27 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0008_warehouseproduct_total_sum'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouseproductarrival',
            name='invalids',
            field=models.IntegerField(default=0),
        ),
    ]