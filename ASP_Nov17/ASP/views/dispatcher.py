import csv, datetime
from ASP.models import Order, Dispatcher, Location, UserData
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from ASP.views.UserWeb import UserWeb

# Roles.
class DispatcherWeb(UserWeb):
    user = None

    def authenticate(request):
        if not DispatcherWeb.user_test(request, 'DP'):
            return False
        else:
            user_data = UserData.objects.get(user_name=request.user)
            DispatcherWeb.user = Dispatcher.objects.get(user=user_data)
            return True

    class DPViewsOrder(ListView):
        template_name = 'ASP/dispatcher.html'

        order_list = []
        total_weight = 0.0
        container_weight = 1.2
        max_weight = 25

        def show(request):
            if not DispatcherWeb.authenticate(request):
                return redirect('login')
            else:
                response = DispatcherWeb.DPViewsOrder.as_view()
                return response(request)

        def get_queryset(self):
            return Order.objects.filter(status__exact='QD').order_by('-priority')

        def update_order(request):
            if not DispatcherWeb.authenticate(request):
                return redirect('login')

            order_id = request.POST.get('order')
            order = Order.objects.get(id=order_id)
            weight = float(order.weight)

            if DispatcherWeb.DPViewsOrder.total_weight + DispatcherWeb.DPViewsOrder.container_weight + weight > DispatcherWeb.DPViewsOrder.max_weight:
                return redirect('DP-view-order')

            DispatcherWeb.DPViewsOrder.total_weight += weight + DispatcherWeb.DPViewsOrder.container_weight
            order.status = 'DI'
            order.dispatcher = DispatcherWeb.user
            order.timeDI = datetime.datetime.now()
            order.save()
            DispatcherWeb.DPViewsOrder.order_list.append(order)
            return redirect('DP-view-order')

        def get_csv(request):
            if not DispatcherWeb.authenticate(request):
                return redirect('login')

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=dispacher_order.csv'
            writer = csv.writer(response)

            writer.writerow([f'Dispatcher {DispatcherWeb.user.id}', DispatcherWeb.user])

            hospital = Location.objects.get(name="Queen Mary Hospital")
            pre_location = hospital
            for order in DispatcherWeb.DPViewsOrder.order_list:
                user_name = order.clinic_manager.user.user_name
                user = User.objects.get(username=user_name)
                email = user.email
                send_mail('Notify', f'Order delivered: {order.id} {order.items}', settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)

                location = order.location
                latitude = location.latitude
                longtitude = location.longitude
                altitude = location.altitude
                if location == pre_location:
                    writer.writerow([order.id, location, latitude, longtitude, altitude])
                #distance = Distance.objects.get(start=pre_location, end=location) # recover after distance stored
                writer.writerow([order.id, location, latitude, longtitude, altitude])#, distance]) # recover after distance stored
                pre_location = location

            location = hospital
            if location == pre_location:
                return redirect('DP-view-order')
            latitude = location.latitude
            longtitude = location.longitude
            altitude = location.altitude

            # the last location is hosiptal
            #distance = Distance.objects.get(start=pre_location, end=location) # recover after distance stored
            writer.writerow([0, location, latitude, longtitude, altitude])#, distance]) # recover after distance stored

            DispatcherWeb.DPViewsOrder.order_list.clear()
            DispatcherWeb.DPViewsOrder.total_weight = 0
            return response
