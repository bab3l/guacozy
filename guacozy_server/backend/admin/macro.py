from django.contrib import admin
from django.forms import ModelForm, TextInput, Textarea
from backend.models import Macro

class MacroForm(ModelForm):
    class Meta:
        fields = '__all__'
        
        model = Macro
        
        help_texts = {
            'sequence':
                'Macro sequence as defined in the help file - JSON compliant',
        }

        widgets = {
            'name': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'sequence': Textarea(attrs={'autocomplete': 'off', 'data-lpignore': 'true', 'rows': 20, 'cols': 60}),
        }

@admin.register(Macro)
class MacroModelAdmin(admin.ModelAdmin):
    model = Macro
    form = MacroForm

