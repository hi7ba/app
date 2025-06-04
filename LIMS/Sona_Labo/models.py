from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from datetime import date
from django.utils import timezone



class Client(models.Model):
    nameC = models.CharField(max_length=30 , verbose_name="Nom du client")
    code = models.CharField(max_length=6, unique=True, verbose_name="Code client")
    email= models.EmailField(verbose_name="Adresse e-mail", blank=True, null=True)
    phone_number = models.CharField(max_length=10 , verbose_name="Numéro de téléphone", blank=True, null=True)
    def __str__(self):
            return self.nameC

    class Meta:
        verbose_name = "Unité"
        

class Category(models.Model):
    namect = models.CharField(max_length=100, verbose_name="Nom catégorie")
    def __str__(self):
            return self.namect
    
    class Meta:
     verbose_name = "Catégorie"

class SampleType(models.Model): 
    nameST = models.CharField(max_length=70 , unique=True, verbose_name="Nom du type d'échantillon")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sample_types",verbose_name="Catégorie")
    description  = models.TextField(blank=True, null=True)
    prefix = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.nameST
    class Meta:
     verbose_name = "Type d’Échantillon"
 
class Lot(models.Model):
    lot_code = models.CharField(max_length=25 , unique=True, verbose_name="Code du lot")
    lot_name = models.CharField(max_length=50 , verbose_name="Nom du lot")
    
    def __str__(self):
        return f"{self.lot_code} - {self.lot_name}"  

class StorageLocation(models.Model):
    sale = models.CharField(max_length=30, verbose_name="Salle")
    armoire = models.CharField(max_length=30, verbose_name="Armoire")
    
    def __str__(self):
        return f"Salle {self.sale}, Armoire {self.armoire}"  
    class Meta:
     verbose_name = "Emplacement de stockage" 

class Shelf(models.Model):
    number = models.CharField(max_length=800, verbose_name="Numéro d'étagère")
    storage_location = models.ForeignKey(
        StorageLocation, 
        on_delete=models.CASCADE, 
        related_name="shelves",
        verbose_name="Emplacement de stockage"
    )
    
    def __str__(self):
        return f"Étagère {self.number} ({self.storage_location})" 
    class Meta:
     verbose_name = "Étagère" 
    
class Localisation(models.Model):
    etagere = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name='localisations', verbose_name="Étagère")
    emplacement = models.ForeignKey(StorageLocation, on_delete=models.CASCADE, related_name='localisations', verbose_name="Emplacement de stockage")
    quantite = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.etagere} in {self.emplacement}"

class Sample(models.Model):
    sample_type = models.ForeignKey(SampleType, on_delete=models.CASCADE, related_name="samples", verbose_name="Type d'échantillon")
    volume = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Volume (L)", blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="samples", verbose_name="Client")
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="samples", verbose_name="Lot", blank=True, null=True)
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name="samples", verbose_name="Étagère", blank=True, null=True)
    date= models.DateField(default=date.today)
    heure = models.TimeField(default=timezone.now)
    #timestamp = models.DateTimeField(auto_now_add=True) 
    PRIORITY_CHOICES = [
         ('haute', 'Haute'),
         ('moyenne', 'Moyenne'),
         ('basse', 'Basse'),
    ]
    priority = models.CharField(max_length=100, choices=PRIORITY_CHOICES, default='moyenne', verbose_name="Priorité")
    
    def __str__(self):
        return f"{self.sample_type} ({self.priority})"
    class Meta:
     verbose_name = "Échantillon" 
  
    
class Manufacturer(models.Model):
    nameF = models.CharField(max_length=80, verbose_name="Nom du fabricant")

    def __str__(self):
        return self.nameF
    class Meta:
     verbose_name = "Fabriquant" 
  


class Modele(models.Model):
    nameM = models.CharField(max_length=80, verbose_name="Nom du modèle")
    description = models.TextField(blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name="models", verbose_name="Fabriquant", null=True, blank=True)
    def __str__(self):
            return self.nameM

class Equipment(models.Model):
    nameE = models.CharField(max_length=80, verbose_name="Nom de l'équipement")
    observation = models.TextField(blank=True, null=True)
    model = models.ForeignKey(Modele, on_delete=models.CASCADE, related_name="equipments", verbose_name="Modèle", null=True, blank=True)
    def __str__(self):
            return self.nameE
    class Meta:
     verbose_name = "Équipment" 
  
    
class Methodology(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre de la méthodologie", unique=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description de la méthodologie")
    instruction = models.TextField(blank=True, null=True, verbose_name="Instructions de la méthodologie", help_text="Instructions pour l'utilisation de la méthodologie")
    equipment = models.ManyToManyField(Equipment, through='MethodologyRequirement', related_name='methodologies', verbose_name="Équipements nécessaires")
    def __str__(self):
            return self.titre
    class Meta:
     verbose_name = "Méthodologie"
  

class MethodologyRequirement(models.Model):
    methodology = models.ForeignKey(Methodology, on_delete=models.CASCADE, related_name="requirements", verbose_name="Méthodologie")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="requirements", verbose_name="Équipement")
    required = models.BooleanField(default=True, verbose_name="Obligatoire", help_text="Indique si l'équipement est obligatoire pour cette méthodologie", blank=True, null=True)
    def __str__(self):
        return f"{self.methodology} requires {self.equipment}"
    class Meta:
     verbose_name = "Exigence Méthodologique"
class Analyse(models.Model):
    Nameanl = models.CharField(max_length=80, unique=True, verbose_name="Nom d'analyse")
    observation = models.TextField(blank=True, null=True, verbose_name="Observations")
    min_norm = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        blank=True, 
        null=True,
        verbose_name="Norme minimale"
    )
    max_norm = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        blank=True, 
        null=True,
        verbose_name="Norme maximale"
    )
    methodology = models.ForeignKey(
        Methodology, 
        on_delete=models.CASCADE, 
        related_name="analyses",
        verbose_name="Méthodologie", blank=True, null=True
    )

    def __str__(self):
        norm_display = ""
        if self.min_norm is not None and self.max_norm is not None:
            norm_display = f" ({self.min_norm}-{self.max_norm})"
        elif self.min_norm is not None:
            norm_display = f" (≥{self.min_norm})"
        elif self.max_norm is not None:
            norm_display = f" (≤{self.max_norm})"
            
        return self.Nameanl


class Result(models.Model):
    analyse = models.ForeignKey(
        Analyse, 
        on_delete=models.CASCADE, 
        related_name="results",
        verbose_name="Analyse"
    )
    sample = models.ForeignKey(
        Sample, 
        on_delete=models.CASCADE, 
        related_name="results",
        verbose_name="Échantillon"
    )
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        verbose_name="Valeur"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date et heure"
    )

    def __str__(self):
        status = ""
        if self.analyse.min_norm is not None and self.value < self.analyse.min_norm:
            status = " (Trop bas)"
        elif self.analyse.max_norm is not None and self.value > self.analyse.max_norm:
            status = " (Trop haut)"
            
        return (
            f"{self.sample} >> {self.analyse.Nameanl}: "
            f"{self.value}{status} [{self.timestamp:%Y-%m-%d %H:%M}]"
        )

    class Meta:
        unique_together = ('analyse', 'sample')
        verbose_name = "Résultat"

class Report(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du rapport", unique=True)
    client= models.ForeignKey(Client, on_delete=models.CASCADE, related_name="results",verbose_name="Client", blank=True, null=True)
    analyse= models.ManyToManyField(Analyse, related_name="reports", verbose_name="Analyse")
    sample_type= models.ManyToManyField(SampleType, related_name="reports",verbose_name="Échantillon")
    class Meta:
        verbose_name = "Rapport"
    def __str__(self):
        return self.name