# Generated by Django 4.1.1 on 2023-01-23 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_control', '0019_programador'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programador',
            name='fechaMovimientoProgramado',
            field=models.IntegerField(max_length=2),
        ),
    ]
