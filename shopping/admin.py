# admin.py
from django.contrib import admin
from .models import Product, Category, Commande
from django.utils.html import mark_safe

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'date']
    list_filter = ['category', 'date']
    list_editable = ['price']
    search_fields = ['name', 'description']
    list_per_page = 15  
    ordering = ['-date']  
    readonly_fields = ['date'] 

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'date','slug','description']
    search_fields = ['name','slug']
    list_per_page = 10

class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'email', 'total', 'status_display', 'date']
    list_filter = ['status', 'date']
    search_fields = ['nom', 'email', 'telephone']
    readonly_fields = ['date']
    fieldsets = (
        ('Informations client', {
            'fields': ('nom', 'email', 'telephone', 'adresse')
        }),
        ('Détails commande', {
            'fields': ('total', 'status', 'date')
        }),
    )
    list_per_page = 20
    
    def get_list_display_links(self, request, list_display):
        return ['id', 'nom']
    
    def status_display(self, obj):
        if hasattr(obj, 'status') and obj.status:
            return mark_safe(f'<span class="status-{obj.status}">{obj.get_status_display()}</span>')
        return "-"
    status_display.short_description = "Statut"
    status_display.admin_order_field = 'status'

# Enregistrement des modèles
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Commande, CommandeAdmin)