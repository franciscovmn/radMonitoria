from django.conf import settings
from django.db import models


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

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "dúvida"
        permissions = [
            ("ver_todas_duvidas", "Pode ver todas as dúvidas"),
        ]

    def __str__(self):
        return self.titulo
