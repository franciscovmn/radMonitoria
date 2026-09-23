from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField("código", max_length=20, unique=True)
    ativa = models.BooleanField(default=True)
    monitores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="disciplinas_monitoradas",
    )

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class DuvidaQuerySet(models.QuerySet):
    def visiveis_para(self, usuario):
        if usuario.has_perm("duvidas.ver_todas_duvidas"):
            return self
        return self.filter(
            Q(autor=usuario) | Q(disciplina__monitores=usuario)
        ).distinct()


class Duvida(models.Model):
    class Situacao(models.TextChoices):
        ABERTA = "aberta", "Aberta"
        EM_ATENDIMENTO = "em_atendimento", "Em atendimento"
        RESPONDIDA = "respondida", "Respondida"
        ENCERRADA = "encerrada", "Encerrada"

    titulo = models.CharField("título", max_length=200)
    descricao = models.TextField("descrição")
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.PROTECT, related_name="duvidas"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="duvidas_abertas",
    )
    monitor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duvidas_atendidas",
        verbose_name="monitor responsável",
    )
    resposta = models.TextField(blank=True)
    situacao = models.CharField(
        "situação",
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.ABERTA,
    )
    criada_em = models.DateTimeField("aberta em", auto_now_add=True)
    atualizada_em = models.DateTimeField("atualizada em", auto_now=True)

    objects = DuvidaQuerySet.as_manager()

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "dúvida"
        permissions = [
            ("ver_todas_duvidas", "Pode ver todas as dúvidas"),
        ]

    def __str__(self):
        return self.titulo


class HorarioAtendimento(models.Model):
    class DiaSemana(models.IntegerChoices):
        SEGUNDA = 0, "Segunda-feira"
        TERCA = 1, "Terça-feira"
        QUARTA = 2, "Quarta-feira"
        QUINTA = 3, "Quinta-feira"
        SEXTA = 4, "Sexta-feira"
        SABADO = 5, "Sábado"

    monitor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="horarios_atendimento",
    )
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name="horarios"
    )
    dia_semana = models.IntegerField("dia da semana", choices=DiaSemana.choices)
    inicio = models.TimeField("início")
    fim = models.TimeField()

    class Meta:
        ordering = ["dia_semana", "inicio"]
        verbose_name = "horário de atendimento"
        verbose_name_plural = "horários de atendimento"

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.inicio:%H:%M} às {self.fim:%H:%M}"

    def clean(self):
        if self.inicio is None or self.fim is None or self.dia_semana is None:
            return
        if self.fim <= self.inicio:
            raise ValidationError({"fim": "O fim precisa ser depois do início."})
        if not self.monitor_id or not self.disciplina_id:
            return

        if not self.disciplina.monitores.filter(pk=self.monitor_id).exists():
            raise ValidationError({"disciplina": "Você não é monitor desta disciplina."})

        conflito = HorarioAtendimento.objects.filter(
            monitor_id=self.monitor_id,
            dia_semana=self.dia_semana,
            inicio__lt=self.fim,
            fim__gt=self.inicio,
        ).exclude(pk=self.pk)
        if conflito.exists():
            raise ValidationError("Já existe um horário seu nesse dia que se sobrepõe a este.")
