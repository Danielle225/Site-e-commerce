from django.urls import path
from shopping.views import index, product_detail,checkout,process_checkout
from . import views


urlpatterns = [
    path('', index, name='home'),
    path('<int:product_id>', product_detail, name='details'),
    path('checkout', checkout, name='checkout'),
    path('process_checkout', process_checkout, name='process_checkout'),
]
