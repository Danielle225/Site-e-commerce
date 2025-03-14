from django.db import models
from django.utils.text import slugify

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

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, default='default-slug')    
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Categories"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            # Générer un slug de base à partir du nom
            original_slug = slugify(self.name)
            
            # Vérifier si ce slug existe déjà
            queryset = Category.objects.all()
            if self.pk:
                # Si c'est une mise à jour, exclure l'instance actuelle
                queryset = queryset.exclude(pk=self.pk)
            
            # Générer un slug unique en ajoutant un suffixe numérique si nécessaire
            unique_slug = original_slug
            counter = 1
            
            while queryset.filter(slug=unique_slug).exists():
                unique_slug = f"{original_slug}-{counter}"
                counter += 1
            
            self.slug = unique_slug
        
        super().save(*args, **kwargs)
            
    def __str__(self):
        return self.name
        
    def get_product_count(self):
        return self.product_set.count()

class Commande(models.Model):
    class Status(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        CONFIRMEE = 'confirmee', 'Confirmée'
        EN_PREPARATION = 'en_preparation', 'En préparation'
        EXPEDIEE = 'expediee', 'Expédiée'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'
    
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EN_ATTENTE,
        verbose_name="Statut"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        
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