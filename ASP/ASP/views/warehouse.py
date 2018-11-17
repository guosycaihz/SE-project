import io, datetime
from ASP.models import Order, Warehouse, UserData
from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from ASP.views.UserWeb import UserWeb

# Roles.
class WarehouseWeb(UserWeb):
    user = None

    def authenticate(request):
        if not WarehouseWeb.user_test(request, 'WP'):
            return False
        else:
            user_data = UserData.objects.get(user_name=request.user)
            WarehouseWeb.user = Warehouse.objects.get(user=user_data)
            return True

    class WPViewsQueue(ListView):
        template_name = 'ASP/warehouse.html'
        ready_queue = []

        def show(request):
            if not WarehouseWeb.authenticate(request):
                return redirect('login')
            else:
                response = WarehouseWeb.WPViewsQueue.as_view()
                return response(request)

        def get_queryset(self):
            return Order.objects.filter(status__contains='P').order_by('-priority')

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            pw_order = Order.objects.filter(status__exact='PW')
            if pw_order is not None:
                context['process'] = "T"
            else:
                context['process'] = "F"

            return context


        def update(request):
            if not WarehouseWeb.authenticate(request):
                return redirect('login')

            order_id = request.POST.get('order')
            order = Order.objects.get(id=order_id)

            if order.status == 'QP':
                order.status = 'PW'
                order.timePW = datetime.datetime.now()
            elif order.status == 'PW':
                if order_id not in WarehouseWeb.WPViewsQueue.ready_queue:
                    return redirect('WP-view-order')
                order.status = 'QD'
                order.timeQD = datetime.datetime.now()

            order.save()
            return redirect('WP-view-order')

        def get_rfid(request):
            if not WarehouseWeb.authenticate(request):
                return redirect('login')

            order_id = request.POST.get('order')
            order = Order.objects.get(id=order_id)

            if order.status == 'PW':
                WarehouseWeb.WPViewsQueue.ready_queue.append(order_id)

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="RFID.pdf"'
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer)
                p.drawString(100, 300, "Shipping Label.")
                p.drawString(100, 200, f'{order.clinic_manager}')
                p.drawString(100, 100, f'{order.location}')
                p.showPage()
                p.save()
                pdf = buffer.getvalue()
                buffer.close()
                response.write(pdf)
                return response

            return redirect('WP-View-order')