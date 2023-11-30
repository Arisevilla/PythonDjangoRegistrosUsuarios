from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from login.models import Formulario
from django.contrib import messages




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
    
    if len(fono) !=8:
        messages.error(request,'El teléfono debe tener 8 dígitos')
        return redirect('home')

    def validar_rut(rut):

        rut=rut.replace(".","").replace("-","").lower()
        if not rut[:-1].isdigit() or not rut[-1] in ('0-9kK'):
            return False
        reversed_digits= map(int,reversed(rut[:-1]))
        factors=[2,3,4,5,6,7,2,3,4,5,6,7]
        s=sum(d*f for d, f in zip(reversed_digits,factors))
        expected_digit=(11-s % 11)% 11
        expected_digit='k' if expected_digit == 10 else str(expected_digit)
        return expected_digit== rut[-1].lower()
    
    if not validar_rut(rut):
            messages.error(request,'El rut es inválido')
            return redirect('home')
    else:
        r = Formulario(cliente=cliente,rut=rut,direccion=direccion,fono=fono,descripcion=descripcion)
        r.save()
        messages.success(request, 'Producto agregado')
        return redirect('listado')

def detalle(request,id):
    registro= Formulario.objects.get(pk=id)
    return render(request,"listadoEditar.html",{
        'registro': registro
    })

def editar(request):
    cliente= request.POST["cliente"]
    rut= request.POST["rut"]
    direccion= request.POST["direccion"]
    fono= request.POST["fono"]
    descripcion= request.POST["descripcion"]
    id= request.POST["id"]
    Formulario.objects.filter(pk=id).update(id=id,cliente=cliente,rut=rut,direccion=direccion,fono=fono,descripcion=descripcion)
    messages.success(request, 'Producto actualizado')
    return redirect('listado')