from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()  # Changé de FloatField à DecimalField
    description = models.TextField()
    image_url = models.URLField(max_length=2083)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')  # Changé 'category' à 'Category'
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return self.name

class Category(models.Model):  # Renommé de 'category' à 'Category'
    name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return self.name

class Commande(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"Commande #{self.id} - {self.nom}"

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)  # Corrigé ForeignKey
    nom = models.CharField(max_length=255)  # Nom du produit au moment de la commande
    prix = models.FloatField()
    quantite = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantite} x {self.nom}"
    
    @property
    def sous_total(self):
        return self.prix * self.quantite