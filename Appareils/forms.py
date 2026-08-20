from django import forms


CATEGORIES = [
    ("", "Choisir une catégorie..."),
    ("Cuisine", "Cuisine"),
    ("Climatisation", "Climatisation"),
    ("Eclairage", "Éclairage"),
    ("Audiovisuel", "Audiovisuel"),
    ("Electromenager", "Électroménager"),
    ("Informatique", "Informatique"),
    ("Autre", "Autre"),
]


class AppareilForm(forms.Form):
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Ex : Climatiseur Salon"}),
    )

    categorie = forms.ChoiceField(
        choices=CATEGORIES,
        required=True,
    )

    puissance = forms.FloatField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={"placeholder": "1500"}),
    )

    heures_par_jour = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={"placeholder": "8", "step": "0.01"}),
    )