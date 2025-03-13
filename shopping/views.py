import json
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Product, Commande, LigneCommande
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