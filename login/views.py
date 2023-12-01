from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from login.models import Formulario
from django.contrib import messages
from login.models import UserProfile
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from datetime import datetime





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
@staff_member_required
def registro(request):
    if request.method=='GET':
        return render(request, "registro.html", {'form' : UserCreationForm})
    else:
        if request.POST["password1"]!=request.POST["password2"]:
            return render(request, "registro.html", {'form' : UserCreationForm, 'error': "Las contraseñas no coinciden"})
        else:
            
            name= request.POST["username"]
            email= request.POST["email"]
            password = request.POST["password1"]
            nombre = request.POST["nombre"]
            apellido = request.POST["apellido"]
            user = User.objects.create_user(username=name,email=email,password=password)
            user_profile= UserProfile.objects.create(user=user, email=email, nombre=nombre,apellido=apellido)
            
            user.save()
            user_profile.save()
            return render(request, "registro.html", {'form' : UserCreationForm, 'error': "Usuario registrado"})

@login_required
def home(request):
    nombre= None
    apellido = None

    if request.user.is_authenticated:
        try:
            user_profile= UserProfile.objects.get(user=request.user)
            nombre= user_profile.nombre
            apellido = user_profile.apellido

        except UserProfile.DoesNotExist:
            pass
    return render(request,"home.html", {'nombre': nombre, 'apellido':apellido})

#Desloguearse
def salir(request):
    logout(request)
    return redirect('../')

def listado(request):
    registros = Formulario.objects.all()

    nombre=None
    apellido=None

    if request.user.is_authenticated:
        try:
            user_profile= UserProfile.objects.get(user=request.user)
            nombre= user_profile.nombre
            apellido= user_profile.apellido
        except UserProfile.DoesNotExist:
            pass

    campo = request.GET.get('campo','id')
    valor = request.GET.get('valor','')

    campos_permitidos= ['id', 'name', 'cliente', 'fecha', 'rut','direccion', 'fono']

    if campo in campos_permitidos:
        registros= Formulario.objects.filter(
            Q(**{f'{campo}__icontains':valor})
        )
    else:
        registros= Formulario.objects.all()
                                                  
    return render(request,"listado.html", {
        'registros': registros,
        'nombre':nombre,
        'apellido':apellido,
        'campo':campo,
        'valor':valor,
    })


@login_required
def guardar(request):
    cliente= request.POST["cliente"]
    rut= request.POST["rut"]
    direccion= request.POST["direccion"]
    fono= request.POST["fono"]
    descripcion= request.POST["descripcion"]
    name = request.POST["name"]

    if len(fono) !=9:
        messages.error(request,'El teléfono debe tener 9 dígitos')
        return redirect('home')

    def validar_rut(rut):

        rut=rut.replace("-","").replace(".","").upper()
        print(f"Rut sin formato: {rut}")

        if not rut[:-1].isdigit() or not rut[-1] in ('0-1-2-3-4-5-6-7-8-9K'):
            print("Error: No es un digito o el digito verificador no es 'K' ")
            return False
        
        
        reversed_digits= map(int,reversed(rut[:-1]))
        factors=[2,3,4,5,6,7,2,3,4,5,6,7]
        s=sum(d*f for d, f in zip(reversed_digits,factors))
        expected_digit=(11-s % 11)% 11
        expected_digit='K' if expected_digit == 10 else str(expected_digit)

        print(f"Valor esperado del digito verificador: {expected_digit}")
        return expected_digit == rut[-1].lower()
    
    rut_valido= validar_rut(rut)
    
    if rut_valido:
            r = Formulario(name=name, cliente=cliente,rut=rut,direccion=direccion,fono=fono,descripcion=descripcion)
            r.save()
            messages.success(request, 'Registro agregado')
            return redirect('listado')
    else:
            messages.error(request,'El rut es inválido')
            return redirect('home')
           

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
    messages.success(request, 'Registro actualizado')
    return redirect('listado')

def eliminar(request, id):
    registro = Formulario.objects.filter(pk=id)
    registro.delete()
    messages.success(request,'Registro eliminado')
    return redirect('listado')

def inicio(request):
    today = datetime.now().date()

    usuarios_registrados= User.objects.all().values_list('username', flat=True)

    registros_por_mes= Formulario.objects.filter(
        fecha__gte=datetime(today.year,1,1).date()
    ).annotate(month=Count('fecha')).values('month')

    trabajador_mas_ot= Formulario.trabajador_con_mas_ot_mes()

    

    labels= [today.strftime("%b")]
    data = [registros_por_mes[0]['month'] if registros_por_mes else 0 ]


    return render(request, 'inicio.html',{
        'usuarios_registrados':usuarios_registrados,
        'usuarios_registrados_count': User.objects.count(),
        'total_registros_count': Formulario.objects.count(),
        'labels':labels,
        'data':data,
        'registros_por_mes': registros_por_mes,
        'trabajador_mas_ot':trabajador_mas_ot,
    })
