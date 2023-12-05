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
from django.db.models import Max, F
from django.db.models.functions import TruncMonth
from django.db.models import Min
import json
import uuid
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_control






# Create your views here.
#Login
def iniciar(request):
    if request.user.is_authenticated:
        logout(request)

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
            return redirect("inicio/")

    
#Registrarse

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
@staff_member_required
def registro(request):
    if request.method=='GET':
        return render(request, "registro.html", {'form' : UserCreationForm})
    else:
        if request.POST["password1"]!=request.POST["password2"]:
            return render(request, "registro.html", {'form' : UserCreationForm, 'error': "Las contraseñas no coinciden"})
        

        else:
            foto = request.FILES.get('foto')
            name= request.POST["username"]
            email= request.POST["email"]
            password = request.POST["password1"]
            nombre = request.POST["nombre"]
            apellido = request.POST["apellido"]
            telefono = request.POST["telefono"]
            direccio= request.POST["direccio"]

            if len(telefono) !=9:
                messages.error(request,'El teléfono debe tener 9 dígitos')
                return redirect('registro')
            
            user = User.objects.create_user(username=name,email=email,password=password)
            user_profile= UserProfile.objects.create(user=user, email=email, nombre=nombre,apellido=apellido,telefono=telefono,direccio=direccio,foto=foto)
            
            user.save()
            user_profile.save()
            return render(request, "registro.html", {'form' : UserCreationForm, 'error': "Usuario registrado"})
        
class AtomicCounter:
    counter = 1000

    @classmethod
    def increment_and_get(cls):
        with transaction.atomic():
            cls.counter += 1
            return cls.counter
@login_required
def home(request):
    nombre= None
    apellido = None
    nuevo_id =  AtomicCounter.increment_and_get()

    if request.user.is_authenticated:
        try:
            user_profile= UserProfile.objects.get(user=request.user)
            nombre= user_profile.nombre
            apellido = user_profile.apellido
        except UserProfile.DoesNotExist:
            pass

    if request.method == 'POST':
        rut= request.POST.get('rut', '')
        usuario_encontrado = Formulario.objects.filter(rut=rut).first()

        if usuario_encontrado:
            return render(request, 'home.html', {'nombre': nombre, 'apellido':apellido,'usuario':usuario_encontrado,'nuevo_id': nuevo_id})
        else:
            messages.info(request,'El rut no está registrado.')
            return render(request, 'home.html', {'nombre': nombre, 'apellido':apellido,'nuevo_id': nuevo_id })

    return render(request,"home.html", {'nombre': nombre, 'apellido':apellido,'nuevo_id': nuevo_id})

#Desloguearse
def salir(request):
    logout(request)
    return redirect('../')
@login_required
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
    campo2 = request.GET.get('campo2','')
    valor2= request.GET.get('valor2','')
    orden = request.GET.get('orden', 'id')
    direccion = request.GET.get('direccion','asc')

    campos_permitidos= ['id', 'name', 'cliente', 'fecha', 'rut','direccion', 'fono']

    if campo in campos_permitidos and valor:
            if campo == 'fecha':
                try:
                    fecha_busqueda = datetime.strptime(valor,'%d/%m/%Y').date()
                    registros= registros.filter(Q(**{f'{campo}__date':fecha_busqueda}))
                except ValueError:
                    messages.error(request, 'Formato de fecha no válida')
                    
            else:
                registros= registros.filter(
                Q(**{f'{campo}__icontains':valor})
            )

    if campo2 in campos_permitidos and valor2:
        if campo2 == 'fecha':
                try:
                    fecha_busqueda = datetime.strptime(valor2,'%d/%m/%Y').date()
                    registros= registros.filter(Q(**{f'{campo2}__date':fecha_busqueda}))
                except ValueError:
                    messages.error(request, 'Formato de fecha no válida')
        else:
            registros=registros.filter(
                Q(**{f'{campo2}__icontains': valor2})
         )

    if direccion== 'asc':
        registros= registros.order_by(orden)
    else:
        registros = registros.order_by(f'-{orden}')

    paginator = Paginator(registros, 10)
    page = request.GET.get('page')

    try:
        registros = paginator.page(page)
    except PageNotAnInteger:
        registros = paginator.page(1)
    except EmptyPage:
        registros = paginator.page(paginator.num_pages)



    if direccion == 'asc':
        orden_asc = 'desc'
        orden_desc = 'asc'
    else:
        orden_asc = 'asc'
        orden_desc = 'desc'

    url_ordenacion_asc = f'?campo={campo}&valor={valor}&orden={orden}&direccion={orden_asc}'
    url_ordenacion_desc = f'?campo={campo}&valor={valor}&orden={orden}&direccion={orden_desc}'


                                                  
    return render(request,"listado.html", {
        'registros': registros,
        'nombre':nombre,
        'apellido':apellido,
        'campo':campo,
        'valor':valor,
        'orden':orden,
        'direccion':direccion,
        'url_ordenacion_asc': url_ordenacion_asc,
        'url_ordenacion_desc': url_ordenacion_desc,
    })


@login_required
def guardar(request):
    cliente= request.POST["cliente"]
    rut= request.POST["rut"]
    direccion= request.POST["direccion"]
    fono= request.POST["fono"]
    descripcion= request.POST["descripcion"]
    contacto= request.POST["contacto"]

    if len(fono) !=9:
        messages.error(request,'El teléfono debe tener 9 dígitos')
        return redirect('home')

    def validar_rut(rut):

        rut=rut.replace("-","").replace(".","").upper()
        print(f"Rut sin formato: {rut}")

        if not rut[:-1].isdigit() or not rut[-1] in ('0','1','2','3','4','5','6','7','8','9','K','k'):
            print("Error: No es un digito o el digito verificador no es 'K' ")
            return False
        
        
        reversed_digits= map(int,reversed(rut[:-1]))
        factors=[2,3,4,5,6,7,2,3,4,5,6,7]
        s=sum(d*f for d, f in zip(reversed_digits,factors))
        expected_digit=(11-s % 11)% 11
        expected_digit='K' if expected_digit == 10 else str(expected_digit)

        print(f"Valor esperado del digito verificador: {expected_digit}")
        print(f"Dígito verificador ingresado: {rut[-1].upper()}")

        return expected_digit == rut[-1].upper()
    
    rut_valido= validar_rut(rut)
    
    if rut_valido:
            formulario_id =  AtomicCounter.increment_and_get()
            r = Formulario( id=formulario_id,cliente=cliente,rut=rut,direccion=direccion,fono=fono,descripcion=descripcion,contacto=contacto,user=request.user)
            r.save()
            messages.success(request, 'Registro agregado')
            return redirect('listado')
    else:
            messages.error(request,'El rut es inválido')
            return redirect('home')
           
@login_required
def detalle(request,id):
    registro= Formulario.objects.get(pk=id)
    return render(request,"listadoEditar.html",{
        'registro': registro
    })
@login_required
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
@login_required
def eliminar(request, id):
    registro = Formulario.objects.filter(pk=id)
    registro.delete()
    messages.success(request,'Registro eliminado')
    return redirect('listado')

@login_required
def inicio(request):
    today = datetime.now().date()

    usuarios_registrados= User.objects.all().order_by('-date_joined')[:5]



    trabajador_con_mas_registros = Formulario.objects.filter(
        user__isnull=False
    ).values('user__username').annotate(
        registros=Count('id')
    ).order_by('-registros').first()


    registros_mes= Formulario.objects.annotate(
        month=TruncMonth('fecha')
    ).values('user__username').annotate(
        registros=Count('id')
    ).filter(
        month=datetime(today.year, today.month, 1).date(),
        user__isnull=False
    ).order_by('-registros').first()

    #Usuario con menos registros.
    registros_menos_por_mes = Formulario.objects.annotate(
        month=TruncMonth('fecha')
    ).values('user__username').annotate(
        registros=Count('id')
    ).filter(
        month=datetime(today.year, today.month,1).date(),
        user__isnull=False
    ).order_by('registros').first()

    nombre_mes_actual = today.strftime("%B")


    labels= [nombre_mes_actual]
    data = [registros_mes['registros'] if registros_mes else 0 ]

    

    return render(request, 'inicio.html',{
        'usuarios_registrados':usuarios_registrados,
        'usuarios_registrados_count': User.objects.count(),
        'total_registros_count': Formulario.objects.count(),
        'labels':labels,
        'data':json.dumps(data),
        'registros_mes': registros_mes,
        'trabajador_con_mas_registros': trabajador_con_mas_registros,
        'registros_menos_por_mes':registros_menos_por_mes,
    })
