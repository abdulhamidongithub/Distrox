# Generated by Django 5.0.1 on 2024-03-18 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_usersalary_salaryparams_car_salarypayment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]