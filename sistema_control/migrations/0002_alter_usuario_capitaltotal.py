# Generated by Django 3.2.1 on 2021-06-30 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_control', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='capitalTotal',
            field=models.DecimalField(decimal_places=3, max_digits=20),
        ),
    ]