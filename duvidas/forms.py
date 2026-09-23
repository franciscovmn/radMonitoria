from django import forms

from .models import Disciplina, Duvida


class DuvidaForm(forms.ModelForm):
    class Meta:
        model = Duvida
        fields = ["disciplina", "titulo", "descricao"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["disciplina"].queryset = Disciplina.objects.filter(ativa=True)


class RespostaForm(forms.ModelForm):
    resposta = forms.CharField(label="Resposta", widget=forms.Textarea, required=True)

    class Meta:
        model = Duvida
        fields = ["resposta"]
