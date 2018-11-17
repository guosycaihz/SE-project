from django.urls import path

from ASP.views.access import AccessWeb
from ASP.views.clinicmanager import ClinicManagerWeb
from ASP.views.warehouse import WarehouseWeb
from ASP.views.dispatcher import DispatcherWeb

from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.conf import settings

urlpatterns =\
[
    path('', AccessWeb.Login.as_view(), name='login'),
    path('login_validate', AccessWeb.Login.validate, name='login-validate'),
    path('logout', AccessWeb.Login.logout, name='logout'),

    path('get_token', AccessWeb.Token.as_view(), name='get-token'),
    path('send_token', AccessWeb.Token.create_token, name='send-token'),
    path('verify_token', AccessWeb.Token.verify_token, name='verify-token'),

    path('register', AccessWeb.Register.as_view(), name='register'),
    path('register_create', AccessWeb.Register.create_user, name='register-create'),

    path('account', AccessWeb.Modify.show, name='account'),
    path('modify_account', AccessWeb.Modify.modify_account, name='modify-account'),

    path('cm_view_supply', ClinicManagerWeb.CMViewsSupply.show, name='CM-view-supply'),
    path('cm_add_order', ClinicManagerWeb.CMViewsSupply.construct_order, name='CM-add-order'),

    path('cm_view_order', ClinicManagerWeb.CMViewsOrder.show, name='CM-view-order'),
    path('cm_receive_order', ClinicManagerWeb.CMViewsOrder.receive_order, name='CM-receive-order'),
    path('cm_cancel_order', ClinicManagerWeb.CMViewsOrder.cancel_order, name='CM-cancel-order'),

    path('wp_view_order', WarehouseWeb.WPViewsQueue.show, name='WP-view-order'),
    path('wp_update', WarehouseWeb.WPViewsQueue.update, name='WP-update'),
    path('wp_generate_rfid', WarehouseWeb.WPViewsQueue.get_rfid, name='WP-generate_rfid'),

    path('dp_view_order', DispatcherWeb.DPViewsOrder.show, name='DP-view-order'),
    path('dp_update_order', DispatcherWeb.DPViewsOrder.update_order, name='DP-update-order'),
    path('dp_generate_csv', DispatcherWeb.DPViewsOrder.get_csv, name='DP-generate-csv'),
]

# showing image
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
