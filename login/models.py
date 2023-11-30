from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User

# Create your models here.
class Formulario(models.Model):
    cliente = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)
    rut = models.CharField(max_length=12,unique=True)
    direccion = models.CharField(max_length=100)
    fono = models.CharField(max_length=8, validators=[MaxLengthValidator(limit_value=8,message='El teléfono debe ser de 8 caracteres')])
    descripcion = models.CharField(max_length=200)
    
class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
User.email=models.EmailField()