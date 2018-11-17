import datetime, hashlib
from django.conf import settings
from ASP.models import UserData, ClinicManager, Dispatcher, Location, Warehouse
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail

class AccessWeb():
    class Token(ListView):
        template_name = 'ASP/token.html'
        model = UserData
        token = None

        def create_token(request):
            email = request.POST.get('email')
            time = datetime.datetime.now()
            text = f'{email}{time}'
            hash_text = hashlib.sha256(text.encode('utf-8'))
            AccessWeb.Token.token = hash_text.hexdigest()
            send_mail('Token', f'Token is: {AccessWeb.Token.token}', settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
            return redirect('get-token')

        def verify_token(request):
            token = request.POST.get('token')
            if token == AccessWeb.Token.token and AccessWeb.Token.token is not None:
                AccessWeb.Register.verify = True
                return redirect('register')
            return redirect('get-token')

    class Register(ListView):
        verify = False
        template_name = 'ASP/register.html'
        model = Location

        def create_user(request):
            if AccessWeb.Register.verify == False:
                return redirect('get-token')
            AccessWeb.Register.verify = False
            if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')
                email = "temp@asp.com"
                #email = request.POST.get['email']
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                name = f'{first_name} {last_name}'
                type = request.POST.get('role')

                user = User.objects.create_user(username, email, password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                new_data = UserData.objects.create(user_name=username, type=type)
                if type == 'CM':
                    clinic_id = request.POST.get('location')
                    clinic = Location.objects.get(id=clinic_id)
                    ClinicManager.objects.create(user=new_data, name=name, location=clinic)
                elif type == 'WP':
                    Warehouse.objects.create(user=new_data, name=name)
                elif type == 'DP':
                    Dispatcher.objects.create(user=new_data, name=name)

                return HttpResponse('Register successed!')

    class Login(ListView):
        template_name = 'ASP/login.html'
        model = UserData

        def validate(request):
            if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')

                user = authenticate(request, username=username, password=password)
                user_data = UserData.objects.filter(user_name__exact=username)

                if user is not None:
                    login(request, user)
                    if user_data:
                        for data in user_data:
                            type = data.type
                        if type == 'CM':
                            index = 'CM-view-supply'
                        elif type == 'WP':
                            index = 'WP-view-order'
                        elif type == 'DP':
                            index = 'DP-view-order'
                        return redirect(index)
                return redirect('login')

        def logout(request):
            logout(request)
            return redirect('login')

    class Modify(ListView):
        model = UserData
        template_name = 'ASP/account.html'
        user = None

        def show(request):
            if request.user.is_authenticated:
                AccessWeb.Modify.user = request.user
                response = AccessWeb.Modify.as_view()
                return response(request)
            else:
                return redirect('login')

        def get_queryset(self):
            if AccessWeb.Modify.user is None:
                return None
            else:
                return User.objects.filter(username=AccessWeb.Modify.user)

        def modify_account(request):
            if request.user.is_authenticated:
                AccessWeb.Modify.user = request.user
            password = request.POST.get('password')
            re_password = request.POST.get('re_password')
            firstname = request.POST.get('first_name')
            lastname = request.POST.get('last_name')
            address = request.POST.get('address')
            host = request.POST.get('host')
            email = f'{address}@{host}'
            user = User.objects.get(username=AccessWeb.Modify.user)
            if password != "" and password == re_password:
                user.set_password(password)
            if firstname != "":
                user.first_name = firstname
            if lastname != "":
                user.last_name = lastname
            if address != "" and host != "":
                user.eamil = email
            user.save()

            return redirect('account')
