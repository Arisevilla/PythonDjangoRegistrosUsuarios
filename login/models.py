from django.db import models

# Create your models here.
class Formulario(models.Model):
    cliente = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)
    rut = models.CharField(max_length=12)
    direccion = models.CharField(max_length=100)
    fono = models.FloatField()
    descripcion = models.CharField(max_length=200)
    
