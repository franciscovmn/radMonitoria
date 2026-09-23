from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import CreateView


class CadastroView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/cadastro.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        resposta = super().form_valid(form)
        alunos, _ = Group.objects.get_or_create(name="Alunos")
        self.object.groups.add(alunos)
        messages.success(self.request, "Conta criada. Entre com seu usuário e senha.")
        return resposta
