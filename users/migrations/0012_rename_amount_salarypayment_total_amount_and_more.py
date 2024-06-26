# Generated by Django 5.0.1 on 2024-05-06 07:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_salarypayment_month_salarypayment_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salarypayment',
            old_name='amount',
            new_name='total_amount',
        ),
        migrations.AddField(
            model_name='salarypayment',
            name='bonus',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='salarypayment',
            name='fixed_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='salarypayment',
            name='kpi_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='salarypayment',
            name='paid_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
