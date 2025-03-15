import json
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Category, Product, Commande, LigneCommande
from decimal import Decimal

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
    return render(request, 'shopping/checkout.html')

def process_checkout(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        panier_data = request.POST.get('panier_data')
        
        try:
            panier = json.loads(panier_data)
            
            if not panier:
                messages.error(request, 'Votre panier est vide')
                return redirect('checkout')
            
            # Calculer le total
            total = 0
            for item in panier:
                total += float(item['price']) * int(item['quantity'])
            
            # Créer la commande
            commande = Commande(
                nom=nom,
                email=email,
                adresse=adresse,
                telephone=telephone,
                total=total
            )
            commande.save()
            
            # Créer les lignes de commande
            for item in panier:
                produit_id = item['id']
                
                # Vérifier si le produit existe
                try:
                    produit = Product.objects.get(pk=produit_id)
                    prix = float(produit.price)  # Utilisez le prix du produit dans la BD
                    
                    LigneCommande.objects.create(
                        commande=commande,
                        produit=produit,  # Utiliser le champ produit selon votre modèle
                        nom=item['name'],
                        prix=prix,
                        quantite=item['quantity']
                    )
                except Product.DoesNotExist:
                    # Si le produit n'existe pas, créer la ligne sans référence au produit
                    prix = float(item['price'])
                    
                    LigneCommande.objects.create(
                        commande=commande,
                        nom=item['name'],
                        prix=prix,
                        quantite=item['quantity']
                    )
            
            # Rediriger vers la confirmation
            return redirect('confirmation', commande_id=commande.id)
            
        except json.JSONDecodeError:
            messages.error(request, 'Erreur lors du traitement du panier')
            return redirect('checkout')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
            return redirect('checkout')
    
    return redirect('checkout')

def confirmation(request, commande_id):
    try:
        commande = Commande.objects.get(id=commande_id)
        lignes = LigneCommande.objects.filter(commande=commande)
        return render(request, 'shopping/confirmation.html', {
            'commande': commande,
            'lignes': lignes
        })
    except Commande.DoesNotExist:
        messages.error(request, 'Commande introuvable')
        return redirect('home')
    
def base_context(request):
    """Contexte global pour inclure les catégories dans tous les templates"""
    categories = Category.objects.all().order_by('name')
    return {
        'categories': categories
    }

def home_view(request):
    """Vue de la page d'accueil"""
    featured_products = Product.objects.filter(featured=True)[:8] if hasattr(Product, 'featured') else Product.objects.all()[:8]
    categories = Category.objects.all()
    
    return render(request, 'shopping/home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })

def category_view(request, slug):
    """Vue pour afficher les produits d'une catégorie spécifique"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    
    
    return render(request, 'shopping/category.html', {
        'category': category,
        'products': products,
    })

def product_list_view(request):
    """Vue pour afficher tous les produits"""
    products = Product.objects.all().order_by('-date')
    
    return render(request, 'shopping/products.html', {
        'products': products,
    })

def product_detail_view(request, id):
    """Vue pour afficher les détails d'un produit"""
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    return render(request, 'shopping/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })
def product_detail_by_category(request, category_slug, product_id):
    try:
        category = Category.objects.get(slug=category_slug)
        product = Product.objects.get(id=product_id, category=category)
        return render(request, 'shopping/detail_cat.html', {
            'product': product,
            'category': category
        })
    except (Category.DoesNotExist, Product.DoesNotExist):
        raise Http404("Produit ou catégorie non trouvé")
    

# views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Commande
import json

@csrf_exempt
def cinetpay_notification(request):
    """Endpoint que CinetPay appelle pour notifier du statut du paiement"""
    if request.method == "POST":
        try:
            # Récupérer les données de la notification
            data = json.loads(request.body)
            transaction_id = data.get('cpm_trans_id')
            status = data.get('cpm_result')
            
            # Récupérer la commande correspondante
            commande = get_object_or_404(Commande, id=transaction_id)
            
            if status == '00':  # Code de succès CinetPay
                # Paiement réussi
                commande.status = 'payée'  # Ajustez selon votre modèle
                commande.save()
            else:
                # Paiement échoué
                commande.status = 'paiement_échoué'  # Ajustez selon votre modèle
                commande.save()
                
            return HttpResponse("OK")
        except Exception as e:
            # Logger l'erreur
            return HttpResponse("Error", status=500)
    
    return HttpResponse("Method Not Allowed", status=405)

def cinetpay_return(request):
    """Page vers laquelle l'utilisateur est redirigé après le paiement"""
    transaction_id = request.GET.get('cpm_trans_id')
    
    if not transaction_id:
        # Rediriger vers une page d'erreur si pas d'ID de transaction
        return redirect('payment_error')
        
    commande = get_object_or_404(Commande, id=transaction_id)
    
    if commande.status == 'payée':
        # Paiement réussi
        return render(request, 'shopping/payment_success.html', {'commande': commande})
    else:
        # Paiement échoué ou en attente
        return render(request, 'shopping/payment_failed.html', {'commande': commande})