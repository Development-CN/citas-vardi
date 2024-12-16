from django.db import models


class VTracker(models.Model):
    no_orden = models.CharField(max_length=25, blank=True, null=False, primary_key=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    tecnico = models.CharField(max_length=60, blank=True, null=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)
    vehiculo = models.CharField(max_length=250, blank=True, null=True)
    hora_llegada = models.DateTimeField(blank=True, null=True)
    hora_inicio_asesor = models.DateTimeField(blank=True, null=True)
    hora_fin_asesor = models.DateTimeField(blank=True, null=True)
    hora_promesa = models.DateTimeField(blank=True, null=True)
    hora_grabado = models.CharField(max_length=5, blank=True, null=True)
    inicio_tecnico = models.DateTimeField(blank=True, null=True)
    fin_tecnico = models.DateTimeField(blank=True, null=True)
    detenido = models.CharField(max_length=5)
    servicio_capturado = models.CharField(max_length=500, blank=True, null=True)
    inicio_tecnico_lavado = models.DateTimeField(blank=True, null=True)
    fin_tecnico_lavado = models.DateTimeField(blank=True, null=True)
    ultima_actualizacion = models.IntegerField(blank=True, null=True)
    motivo_paro = models.CharField(max_length=22, blank=True, null=True)
    id_hd = models.CharField(max_length=25, blank=False, null=False)
    telefono_agencia = models.CharField(max_length=25, blank=False, null=False)

    def __str__(self):
        return "Orden: " + str(self.no_orden) + " | Fecha: " + str(self.fecha)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_tracker"
        verbose_name = "Ordenes con tracker"
        verbose_name_plural = "Ordenes con tracker"


class ActividadesPreinventario(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_cita = models.CharField(max_length=100, blank=True, null=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.CharField(max_length=400, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    comentarios = models.CharField(max_length=400, blank=True, null=True)
    evidencia = models.CharField(max_length=400, blank=True, null=True)
    existencia = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "actividades_preinventario"


class ListaItemsPreinventario(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    familia = models.CharField(max_length=50, blank=True, null=True)
    orden = models.BigIntegerField(blank=True, null=True)
    comentarios = models.BooleanField(blank=True, null=True)
    evidencia = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_preinventario"
        verbose_name = "item de pre-inventario"
        verbose_name_plural = "Items de pre-inventario"


class ListaItemsFamiliasPreinventario(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    orden = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_familias_preinventario"
        verbose_name = "familia de items de pre-inventario"
        verbose_name_plural = "Familias de items de pre-inventario"


class ActividadesPrediagnostico(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_cita = models.CharField(max_length=100, blank=True, null=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.CharField(max_length=400, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    comentarios = models.CharField(max_length=400, blank=True, null=True)
    evidencia = models.CharField(max_length=400, blank=True, null=True)
    existencia = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "actividades_prediagnostico"


class ListaItemsPrediagnostico(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    familia = models.CharField(max_length=50, blank=True, null=True)
    orden = models.BigIntegerField(blank=True, null=True)
    comentarios = models.BooleanField(blank=True, null=True)
    evidencia = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_prediagnostico"
        verbose_name = "item de pre-diagnostico"
        verbose_name_plural = "Items de pre-diagnostico"


class ListaItemsFamiliasPrediagnostico(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=50, blank=True, null=True)
    orden = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_familias_prediagnostico"
        verbose_name = "familia de items de pre-diagnostico"
        verbose_name_plural = "Familias de items de pre-diagnostico"


class VInformacionCitas(models.Model):
    id_hd = models.AutoField(primary_key=True)
    no_cita = models.CharField(max_length=25)
    no_orden = models.CharField(max_length=25)
    cliente = models.CharField(max_length=200, blank=True, null=True)
    hora_llegada = models.DateTimeField(blank=True, null=True)
    hora_retiro = models.DateTimeField(blank=True, null=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    vehiculo = models.CharField(max_length=250, blank=True, null=True)
    color = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_informacion_citas"


class VInformacionHistorica(models.Model):
    id_hd = models.AutoField(primary_key=True)
    numcita = models.CharField(db_column="NUMCITA", max_length=25)  # Field name made lowercase.
    noorden = models.CharField(db_column="NOORDEN", max_length=25)  # Field name made lowercase.
    fecha = models.DateTimeField()
    horaasesor = models.DateTimeField(db_column="horaAsesor", blank=True, null=True)  # Field name made lowercase.
    idasesor = models.CharField(max_length=10)
    noplacas = models.CharField(
        db_column="noPlacas", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    vin = models.CharField(max_length=50, blank=True, null=True)
    colorprisma = models.CharField(
        db_column="colorPrisma", max_length=25, blank=True, null=True
    )  # Field name made lowercase.
    vehiculo = models.CharField(
        db_column="Vehiculo", max_length=250, blank=True, null=True
    )  # Field name made lowercase.
    color = models.CharField(db_column="Color", max_length=25, blank=True, null=True)  # Field name made lowercase.
    ano = models.IntegerField(db_column="Ano", blank=True, null=True)  # Field name made lowercase.
    cilindros = models.IntegerField(db_column="Cilindros", blank=True, null=True)  # Field name made lowercase.
    kilometraje = models.IntegerField(db_column="Kilometraje", blank=True, null=True)  # Field name made lowercase.
    idcliente = models.CharField(
        db_column="idCliente", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    cliente = models.CharField(db_column="Cliente", max_length=200, blank=True, null=True)  # Field name made lowercase.
    tipocliente = models.CharField(
        db_column="tipoCliente", max_length=25, blank=True, null=True
    )  # Field name made lowercase.
    telefonos = models.CharField(max_length=50, blank=True, null=True)
    contactonombre = models.CharField(
        db_column="ContactoNombre", max_length=100, blank=True, null=True
    )  # Field name made lowercase.
    contactotelefono = models.CharField(
        db_column="ContactoTelefono", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    horatolerancia = models.DateTimeField(
        db_column="horaTolerancia", blank=True, null=True
    )  # Field name made lowercase.
    horallegada = models.DateTimeField(db_column="Horallegada", blank=True, null=True)  # Field name made lowercase.
    horairecepcion = models.DateTimeField(
        db_column="HoraIRecepcion", blank=True, null=True
    )  # Field name made lowercase.
    horafrecepcion = models.DateTimeField(
        db_column="HoraFRecepcion", blank=True, null=True
    )  # Field name made lowercase.
    horaientrega = models.DateTimeField(db_column="HoraIEntrega", blank=True, null=True)  # Field name made lowercase.
    horafentrega = models.DateTimeField(db_column="HoraFEntrega", blank=True, null=True)  # Field name made lowercase.
    horaretiro = models.DateTimeField(db_column="HoraRetiro", blank=True, null=True)  # Field name made lowercase.
    horarampa = models.DateTimeField(db_column="horaRampa", blank=True, null=True)  # Field name made lowercase.
    fechahorapromesa = models.DateTimeField(
        db_column="fechaHoraPromesa", blank=True, null=True
    )  # Field name made lowercase.
    status = models.CharField(db_column="Status", max_length=30, blank=True, null=True)  # Field name made lowercase.
    fecha_hora_status = models.DateTimeField(
        db_column="Fecha_hora_Status", blank=True, null=True
    )  # Field name made lowercase.
    idop = models.DecimalField(db_column="idOp", max_digits=18, decimal_places=0)  # Field name made lowercase.
    bahia = models.IntegerField(blank=True, null=True)
    observaciones = models.CharField(
        db_column="OBSERVACIONES", max_length=250, blank=True, null=True
    )  # Field name made lowercase.
    usuario = models.CharField(db_column="USUARIO", max_length=50, blank=True, null=True)  # Field name made lowercase.
    fecha_agendado = models.DateTimeField(
        db_column="FECHA_AGENDADO", blank=True, null=True
    )  # Field name made lowercase.
    fecha_original = models.DateTimeField(
        db_column="FECHA_ORIGINAL", blank=True, null=True
    )  # Field name made lowercase.
    fecha_hora_apertura_os = models.DateTimeField(blank=True, null=True)
    fecha_hora_cierre_os = models.DateTimeField(blank=True, null=True)
    fecha_hora_com = models.DateTimeField(
        db_column="Fecha_hora_com", blank=True, null=True
    )  # Field name made lowercase.
    status_os = models.CharField(
        db_column="Status_OS", max_length=15, blank=True, null=True
    )  # Field name made lowercase.
    seriecolorprisma = models.IntegerField(blank=True, null=True)
    testqa = models.DateTimeField(db_column="testQA", blank=True, null=True)  # Field name made lowercase.
    tipolavado = models.CharField(max_length=2, blank=True, null=True)
    comentarioslavado = models.CharField(max_length=250, blank=True, null=True)
    tipollegada = models.CharField(
        db_column="tipoLlegada", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    tiporetiro = models.CharField(
        db_column="tipoRetiro", max_length=5, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_informacion_historica"
