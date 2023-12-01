from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Count

# Create your models here.
class Formulario(models.Model):
    name= models.CharField(max_length=30,null=True, blank=True)
    cliente = models.CharField(max_length=30)
    fecha = models.DateTimeField(auto_now_add=True)
    rut = models.CharField(max_length=12,unique=True)
    direccion = models.CharField(max_length=100)
    fono = models.CharField(max_length=8, validators=[MaxLengthValidator(limit_value=8,message='El teléfono debe ser de 8 caracteres')])
    descripcion = models.CharField(max_length=200)

    @classmethod
    def trabajador_con_mas_ot_mes(cls):
        today= datetime.now().date()
        resultado= cls.objects.filter(
            fecha__year=today.year,
            fecha__month=today.month,
            name__userprofile__isnull=False
        ).values('name__userprofile__user__username').annotate(registros=Count('name__userprofile__user__username')).order_by('-registros').first()
        return resultado['name__userprofile__user__username'] if resultado else None
    
class UserProfile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    nombre= models.CharField(max_length=30,null=True, blank=True)
    apellido=models.CharField(max_length=30,null=True, blank=True)



User.email=models.EmailField()