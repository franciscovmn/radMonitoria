from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

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
    success_url = reverse_lazy("duvidas:lista")

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


class DuvidaListView(LoginRequiredMixin, ListView):
    model = Duvida
    template_name = "duvidas/lista.html"
    context_object_name = "duvidas"

    def get_queryset(self):
        return Duvida.objects.visiveis_para(self.request.user).select_related(
            "disciplina", "autor", "monitor"
        )


class DuvidaDetailView(LoginRequiredMixin, DetailView):
    model = Duvida
    template_name = "duvidas/detalhe.html"
    context_object_name = "duvida"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["pode_assumir"] = self.object.pode_ser_assumida_por(self.request.user)
        return contexto

    def get_queryset(self):
        return Duvida.objects.filter(
            Q(pk__in=Duvida.objects.visiveis_para(self.request.user))
            | Q(situacao__in=[Duvida.Situacao.RESPONDIDA, Duvida.Situacao.ENCERRADA])
        ).select_related("disciplina", "autor", "monitor")


@login_required
def assumir_duvida(request, pk):
    duvida = get_object_or_404(Duvida, pk=pk)
    if not duvida.eh_monitor_da_disciplina(request.user):
        raise PermissionDenied
    if not duvida.pode_ser_assumida_por(request.user):
        messages.error(request, "Esta dúvida não está aberta.")
        return redirect("duvidas:detalhe", pk=pk)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    duvida.monitor = request.user
    duvida.situacao = Duvida.Situacao.EM_ATENDIMENTO
    duvida.save(update_fields=["monitor", "situacao", "atualizada_em"])
    messages.success(request, "Dúvida assumida.")
    return redirect("duvidas:detalhe", pk=pk)
