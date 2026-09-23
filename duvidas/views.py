from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .forms import DuvidaForm, HorarioAtendimentoForm, RespostaForm
from .models import Disciplina, Duvida, HorarioAtendimento


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
        contexto["pode_responder"] = (
            self.object.monitor_id == self.request.user.pk
            and self.object.situacao == Duvida.Situacao.EM_ATENDIMENTO
        )
        contexto["pode_encerrar"] = (
            self.object.autor_id == self.request.user.pk
            and self.object.situacao == Duvida.Situacao.RESPONDIDA
        )
        if contexto["pode_responder"]:
            contexto["form_resposta"] = RespostaForm()
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


@login_required
def responder_duvida(request, pk):
    duvida = get_object_or_404(Duvida, pk=pk)
    if duvida.monitor_id != request.user.pk:
        raise PermissionDenied
    if duvida.situacao != Duvida.Situacao.EM_ATENDIMENTO:
        messages.error(request, "Esta dúvida não está em atendimento.")
        return redirect("duvidas:detalhe", pk=pk)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    form = RespostaForm(request.POST, instance=duvida)
    if not form.is_valid():
        messages.error(request, "A resposta não pode ficar em branco.")
        return redirect("duvidas:detalhe", pk=pk)

    duvida = form.save(commit=False)
    duvida.situacao = Duvida.Situacao.RESPONDIDA
    duvida.save(update_fields=["resposta", "situacao", "atualizada_em"])
    messages.success(request, "Dúvida respondida.")
    return redirect("duvidas:detalhe", pk=pk)


@login_required
def encerrar_duvida(request, pk):
    duvida = get_object_or_404(Duvida, pk=pk)
    if duvida.autor_id != request.user.pk:
        raise PermissionDenied
    if duvida.situacao != Duvida.Situacao.RESPONDIDA:
        messages.error(request, "Esta dúvida não pode ser encerrada.")
        return redirect("duvidas:detalhe", pk=pk)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    duvida.situacao = Duvida.Situacao.ENCERRADA
    duvida.save(update_fields=["situacao", "atualizada_em"])
    messages.success(request, "Dúvida encerrada.")
    return redirect("duvidas:detalhe", pk=pk)


class BaseConhecimentoListView(LoginRequiredMixin, ListView):
    model = Duvida
    template_name = "duvidas/base_conhecimento.html"
    context_object_name = "duvidas"

    def get_queryset(self):
        duvidas = Duvida.objects.filter(
            situacao__in=[Duvida.Situacao.RESPONDIDA, Duvida.Situacao.ENCERRADA]
        ).select_related("disciplina")
        termo = self.request.GET.get("q", "").strip()
        if termo:
            duvidas = duvidas.filter(
                Q(titulo__icontains=termo) | Q(descricao__icontains=termo)
            )
        return duvidas

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["termo"] = self.request.GET.get("q", "").strip()
        return contexto


class HorarioAtendimentoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = HorarioAtendimentoForm
    template_name = "duvidas/meus_horarios.html"
    success_url = reverse_lazy("duvidas:meus_horarios")

    def test_func(self):
        return self.request.user.disciplinas_monitoradas.exists()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        kwargs["instance"] = HorarioAtendimento(monitor=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["horarios"] = HorarioAtendimento.objects.filter(
            monitor=self.request.user
        ).select_related("disciplina")
        return contexto

    def form_valid(self, form):
        messages.success(self.request, "Horário cadastrado.")
        return super().form_valid(form)
