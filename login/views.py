from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from login.models import Formulario

# Create your views here.
#Login
def iniciar(request):
    if request.method=='GET':
        return render(request,"iniciar.html", {'form':AuthenticationForm})
    else:
        name= request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=name, password=password)
        if user is None:
            return render(request,"iniciar.html", {'form':AuthenticationForm, 'error':"Usuario y/o Password incorrecto"})
        else:
            login(request,user)
            return redirect("home/")

    
#Registrarse
def registro(request):
    if request.method=='GET':
        return render(request, "registro.html", {'form' : UserCreationForm})
    else:
        if request.POST["password1"]!=request.POST["password2"]:
            return render(request, "registro.html", {'form' : UserCreationForm, 'error': "Las contraseñas no coinciden"})
        else:
            name= request.POST["username"]
            password = request.POST["password1"]
            user = User.objects.create_user(username=name,password=password)
            user.save()
            return render(request, "registro.html", {'form' : UserCreationForm, 'error': "Usuario registrado"})

@login_required
def home(request):
    return render(request,"home.html")

#Desloguearse
def salir(request):
    logout(request)
    return redirect('../')

def listado(request):
    registros = Formulario.objects.all()
    return render(request,"listado.html", {
        'registros': registros
    })

def guardar(request):
    cliente= request.POST["cliente"]
    rut= request.POST["rut"]
    direccion= request.POST["direccion"]
    fono= request.POST["fono"]
    descripcion= request.POST["descripcion"]

    r = Formulario(cliente=cliente,rut=rut,direccion=direccion,fono=fono,descripcion=descripcion)
    r.save()
    return redirect('listado')