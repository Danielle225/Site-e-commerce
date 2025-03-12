from django.shortcuts import render
from .models import Product
from django.core.paginator import Paginator

def index(request):
    productobjects = Product.objects.all()
    item_name = request.GET.get('name')

    if item_name and item_name.strip():
        productobjects = productobjects.filter(name__icontains=item_name)

    
    paginator = Paginator(productobjects, 6)  
    page = request.GET.get('page')
    products = paginator.get_page(page)  

    return render(request, 'shopping/index.html', {'products': products})  

def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)
    return render(request, 'shopping/details.html', {'product': product})

def checkout(request):
    return render(request,'shopping/checkout.html')
