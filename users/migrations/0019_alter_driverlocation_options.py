# Generated by Django 5.0.1 on 2024-05-25 09:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_salarypayment_options_customuser_archived'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='driverlocation',
            options={'ordering': ['-id']},
        ),
    ]
