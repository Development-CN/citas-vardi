# Generated by Django 4.2.2 on 2023-07-14 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citas_dinissan', '0003_agenciatablero'),
    ]

    operations = [
        migrations.CreateModel(
            name='FallaSintoma',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False, unique=True)),
                ('descripcion_motivo', models.CharField(blank=True, max_length=50, null=True)),
                ('tipo', models.CharField(blank=True, max_length=50, null=True)),
                ('descripcion', models.CharField(max_length=240, null=True)),
                ('descripcion_auxiliar', models.CharField(blank=True, max_length=50, null=True)),
                ('estado', models.BooleanField()),
                ('modelo_tasa', models.CharField(max_length=10, null=True)),
            ],
            options={
                'db_table': 'falla_sintoma',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MotivoIngreso',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False, unique=True)),
                ('descripcion_motivo', models.CharField(blank=True, max_length=50, null=True)),
                ('estado', models.BooleanField()),
                ('categoria_paquete', models.CharField(blank=True, max_length=20, null=True)),
                ('nit_aseguradora', models.CharField(blank=True, max_length=100, null=True)),
                ('adjuntos', models.BooleanField()),
                ('observacion', models.CharField(blank=True, max_length=240, null=True)),
                ('tipo', models.CharField(blank=True, max_length=30, null=True)),
                ('grupo', models.CharField(blank=True, max_length=80, null=True)),
                ('sintoma', models.CharField(blank=True, max_length=120, null=True)),
            ],
            options={
                'db_table': 'motivos_ingreso',
                'managed': False,
            },
        ),
    ]
