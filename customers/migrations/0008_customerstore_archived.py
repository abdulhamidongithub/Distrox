# Generated by Django 5.0.1 on 2024-05-23 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0007_alter_customerstore_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerstore',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
