import datetime
from ASP.models import ClinicManager, MedicineSupply, Order, UserData
from django.shortcuts import redirect
from django.views.generic.list import ListView
from ASP.views.UserWeb import UserWeb

# Roles.
class ClinicManagerWeb(UserWeb):
    user = None

    def authenticate(request):
        if not ClinicManagerWeb.user_test(request, 'CM'):
            return False
        else:
            user_data = UserData.objects.get(user_name=request.user)
            ClinicManagerWeb.user = ClinicManager.objects.get(user=user_data)
            return True

    class CMViewsSupply(ListView):
        template_name = 'ASP/clinicmanager.html'
        model = MedicineSupply
        max_weight = 23.8 # 25 - 1.2

        def show(request):
            if not ClinicManagerWeb.authenticate(request):
                return redirect('login')
            else:
                response = ClinicManagerWeb.CMViewsSupply.as_view()
                return response(request)

        # make an order
        def construct_order(request):
            if not ClinicManagerWeb.authenticate(request):
                return redirect('login')

            items = ''
            weight = 0.0
            no_of_item = request.POST.get('no_of_item')
            for i in range(1, int(no_of_item) + 1):
                amount = request.POST.get('amount' + str(i))
                if amount is None:
                    break
                if amount != '':
                    amount = int(amount)
                    id = request.POST.get('id' + str(i))
                    name = request.POST.get('name' + str(i))
                    weight += float(request.POST.get('weight' + str(i))) * amount
                    items += "id: %s; name: %s; amount: %s.\n" %(id, name, amount)
                priority = request.POST.get('priority')
            if items != '' and weight < ClinicManagerWeb.CMViewsSupply.max_weight:
                ClinicManagerWeb.CMViewsSupply.add_order(ClinicManagerWeb.CMViewsSupply, items, weight, priority)

            return redirect('CM-view-supply')

        # save the order to database
        def add_order(self, items, weight, priority):
            order = Order()

            clinic_manager = ClinicManagerWeb.user
            order.clinic_manager = clinic_manager
            order.location = clinic_manager.location
            order.items = items
            order.weight = weight
            order.priority = priority
            order.timeQP = datetime.datetime.now()

            order.save()

            return

    class CMViewsOrder(ListView):
        template_name = 'ASP/view_order.html'

        def show(request):
            if not ClinicManagerWeb.authenticate(request):
                return redirect('login')
            else:
                response = ClinicManagerWeb.CMViewsOrder.as_view()
                return response(request)

        def get_queryset(self):
            return Order.objects.filter(clinic_manager=ClinicManagerWeb.user).order_by('-id')

        def receive_order(request):
            if not ClinicManagerWeb.authenticate(request):
                return redirect('login')

            order_id = request.POST.get('deliver')
            order = Order.objects.get(id=order_id)
            if order.status == 'DI':
                order.status = 'DE'
                order.timeDE = datetime.datetime.now()
                order.save()
            return redirect('CM-view-order')

        def cancel_order(request):
            if not ClinicManagerWeb.authenticate(request):
                return redirect('login')

            order_id = request.POST.get('remove')
            order = Order.objects.get(id=order_id)
            order.delete()
            return redirect('CM-view-order')

