from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import DuvidaForm
from .models import Disciplina, Duvida


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


class DuvidaCreateView(LoginRequiredMixin, CreateView):
    form_class = DuvidaForm
    template_name = "duvidas/nova.html"
    success_url = reverse_lazy("duvidas:nova")

    def get_disciplina(self):
        return Disciplina.objects.filter(
            ativa=True, pk=self.request.GET.get("disciplina") or None
        ).first()

    def get_initial(self):
        return {"disciplina": self.get_disciplina()}

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["disciplinas"] = Disciplina.objects.filter(ativa=True)
        contexto["disciplina"] = self.get_disciplina()
        return contexto

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.instance.situacao = Duvida.Situacao.ABERTA
        messages.success(self.request, "Dúvida aberta.")
        return super().form_valid(form)
