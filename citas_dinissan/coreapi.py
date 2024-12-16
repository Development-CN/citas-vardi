import logging
from types import SimpleNamespace

import requests
from django.conf import settings


class CoreAPI:
    def __init__(self, endpoint: str):
        endpoints = {
            "asesores": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/lista_asesores/",
            "citas": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/info_citas/",
            "usuarios": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/usuarios/",
            "usuarios_detalle": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/usuarios/login/",
            "tecnicos": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/tecnicos/",
            "informacion_detalle": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/info/",
            "tracker_detalle": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/tracker/",
            "ordenes_activas": f"http://{settings.COREAPI_INFORMACION}/api/v1.2/tablero/ordenes_activas/",
        }
        self.endpoint = endpoints.get(endpoint)
        self.logger = logging.getLogger(__name__)
        return

    def post(self, **kwargs):
        url = self.endpoint
        response = requests.post(url, data=kwargs)
        self.query_object = SimpleNamespace(**response.json())

        self.logger.debug(response.json())
        self.logger.debug(response.status_code)
        self.logger.debug(self.query_object)
        return self

    def get(self):
        response = requests.get(self.endpoint)
        self.queryset = []
        for data in response.json():
            self.queryset.append(SimpleNamespace(**data))

        self.logger.debug(response.json())
        self.logger.debug(response.status_code)
        self.logger.debug(self.queryset)
        return self

    def get_list(self):
        response = requests.get(self.endpoint)
        self.queryset = response.json()

        self.logger.debug(response.json())
        self.logger.debug(response.status_code)
        self.logger.debug(self.queryset)
        return self

    def filter(self, **kwargs):
        queryset_copy = self.queryset.copy()
        self.queryset = []
        for obj in queryset_copy:
            for key, value in kwargs.items():
                if getattr(obj, key) == value and obj not in self.queryset:
                    self.queryset.append(obj)

        self.logger.debug(self.queryset)
        return self

    def exclude_null(self, field):
        queryset_copy = self.queryset.copy()
        self.queryset = []
        for obj in queryset_copy:
            if bool(getattr(obj, field)) and obj not in self.queryset:
                self.queryset.append(obj)

        self.logger.debug(self.queryset)
        return self

    def values_list(self, field):
        queryset_copy = self.queryset.copy()
        self.queryset = []
        for obj in queryset_copy:
            if getattr(obj, field) not in self.queryset:
                self.queryset.append(getattr(obj, field))

        self.logger.debug(self.queryset)
        return self
