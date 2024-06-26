# Generated by Django 5.0.1 on 2024-05-23 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_alter_task_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salarypayment',
            options={'ordering': ['-year', '-month', '-paid_at']},
        ),
        migrations.AddField(
            model_name='customuser',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
