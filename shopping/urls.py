from django.urls import path
from shopping.views import index, product_detail,checkout,process_checkout,confirmation,category_view,product_detail_by_category
from . import views


urlpatterns = [
    path('', index, name='home'),
    path('<int:product_id>', product_detail, name='details'),
    path('checkout', checkout, name='checkout'),
    path('process_checkout', process_checkout, name='process_checkout'),
    path('confirmation/<int:commande_id>/', confirmation, name='confirmation'),
    path('cinetpay/notification/', views.cinetpay_notification, name='cinetpay_notification'),
    path('cinetpay/return/', views.cinetpay_return, name='cinetpay_return'),
    # path('payment/success/', views.payment_success, name='payment_success'),
    # path('payment/error/', views.payment_error, name='payment_error'),
    # path('category/<slug:slug>/', views.category_view, name='category'),
    path("category/<slug:slug>/", category_view, name="category"),
    path('category/<slug:category_slug>/product/<int:product_id>/', product_detail_by_category, name='product_detail_by_category'),
    path('product/<int:id>/', views.product_detail_view, name='product_detail')
]
