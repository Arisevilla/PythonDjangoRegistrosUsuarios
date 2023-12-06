from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Count
from django.utils import timezone


# Create your models here.
class Formulario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    name= models.CharField(max_length=30,null=True, blank=True)
    cliente = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)
    rut = models.CharField(max_length=12,unique=True)
    direccion = models.CharField(max_length=100)
    contacto=models.CharField(max_length=30,null=True, blank=True)
    fono = models.CharField(max_length=9, validators=[MaxLengthValidator(limit_value=9,message='El teléfono debe ser de 9 caracteres')])
    descripcion = models.CharField(max_length=200)
    formulario_id = models.BigIntegerField(unique=True,null=True, blank=True)
    mail=models.EmailField(null=True, blank=True)
    
class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    nombre= models.CharField(max_length=30,null=True, blank=True)
    apellido=models.CharField(max_length=30,null=True, blank=True)
    telefono= models.CharField(max_length=9,null=True, blank=True, validators=[MaxLengthValidator(limit_value=9,message='El teléfono debe ser de 9 caracteres')])
    direccio= models.CharField(max_length=100,null=True, blank=True)
    foto = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    rut = models.CharField(max_length=12,unique=True, null=True, blank=True)


User.email=models.EmailField()