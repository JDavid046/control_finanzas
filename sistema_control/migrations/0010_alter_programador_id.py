# Generated by Django 4.1.1 on 2022-09-20 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_control', '0009_programador'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programador',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
