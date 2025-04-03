from django.contrib import admin
from django.db.models import Sum, Count
from .models import Product, Category, Commande, LigneCommande

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def changelist_view(self, request, extra_context=None):
        # Calcul des métriques pour le tableau de bord
        extra_context = extra_context or {}
        
        # Métriques Produits
        extra_context['total_products'] = Product.objects.count()
        extra_context['total_product_value'] = sum(
            product.price for product in Product.objects.all()
        )
        
        # Métriques Commandes
        extra_context['total_orders'] = Commande.objects.count()
        extra_context['total_revenue'] = Commande.objects.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        # Métriques Catégories
        extra_context['total_categories'] = Category.objects.count()
        
        return super().changelist_view(request, extra_context)

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'total', 'status', 'date')
    list_filter = ('status', 'date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_product_count')
    prepopulated_fields = {'slug': ('name',)}