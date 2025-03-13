from django.contrib import admin
from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'date']
    list_filter = ['category', 'date']
    search_fields = ['name', 'description']
class categoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']
    search_fields = ['name']
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, categoryAdmin)
# Compare this snippet from shopping/views.py:

# Register your models here.
