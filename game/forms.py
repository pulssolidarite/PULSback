from django import forms
from .models import BiosFile, GameFile, CoreFile


class GameFileForm(forms.ModelForm):
    class Meta:
        model = GameFile
        fields = ['file']

class CoreFileForm(forms.ModelForm):
    class Meta:
        model = CoreFile
        fields = ['file']

class BiosFileForm(forms.ModelForm):
    class Meta:
        model = BiosFile
        fields = ['file']