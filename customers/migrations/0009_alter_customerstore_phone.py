# Generated by Django 5.0.1 on 2024-06-08 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0008_customerstore_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerstore',
            name='phone',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
