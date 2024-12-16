from django.contrib import admin

from .models import (
    ListaItemsFamiliasPrediagnostico,
    ListaItemsFamiliasPreinventario,
    ListaItemsPrediagnostico,
    ListaItemsPreinventario,
)

"""
@admin.register(ListaItemsPrediagnostico)
class ListaItemsPrediagnosticoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion", "familia", "orden", "comentarios", "evidencia")


@admin.register(ListaItemsFamiliasPrediagnostico)
class ListaItemsFamiliasPrediagnosticoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion", "orden")


@admin.register(ListaItemsPreinventario)
class ListaItemsPreinventarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion", "familia", "orden", "comentarios", "evidencia")


@admin.register(ListaItemsFamiliasPreinventario)
class ListaItemsFamiliasPreinventarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion", "orden")
"""