# Generated by Django 5.0.1 on 2024-04-08 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_alter_order_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kpiearning',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]