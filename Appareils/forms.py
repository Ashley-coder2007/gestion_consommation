from django import forms


class AppareilForm(forms.Form):
    """
    Formulaire temporaire (pas encore un ModelForm) le temps que le vrai
    model Appareil de ton ami soit branché. Une fois le model prêt,
    remplace `forms.Form` par `forms.ModelForm` avec `class Meta: model = Appareil`.
    """
    CATEGORIES = [
        ("Climatisation", "Climatisation"),
        ("Électroménager", "Électroménager"),
        ("Éclairage", "Éclairage"),
        ("Audiovisuel", "Audiovisuel"),
        ("Informatique", "Informatique"),
        ("Autre", "Autre"),
    ]

    nom = forms.CharField(max_length=100)
    categorie = forms.ChoiceField(choices=CATEGORIES)
    puissance = forms.IntegerField(min_value=1)
    heures_par_jour = forms.DateTimeField()
    icone = forms.CharField(max_length=4, required=False)