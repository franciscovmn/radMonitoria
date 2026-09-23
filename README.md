# Sistema de Apoio à Monitoria

Atividade de ponto extra da disciplina de Rapid Application Development (TSI, IFPB).

## Integrantes

- Francisco Neto
- Felipe Macedo

## Contas de teste

Todas as contas usam a senha `Monitoria@2026`.

| Conta  | Usuário      | Papel                        |
| ------ | ------------ | ---------------------------- |
| Uma    | `admin`      | Superusuário                 |
| Duas   | `aluno2`     | Aluno                        |
| Três   | `aluno3`     | Aluno                        |
| Quatro | `monitor4`   | Monitor de RAD               |
| Cinco  | `professor5` | Professor                    |

Os alunos estão no grupo `Alunos`. O professor está no grupo `Professores`, que tem a permissão `ver_todas_duvidas`.

## Disciplinas e monitores

| Código | Nome                          | Ativa | Monitor    |
| ------ | ----------------------------- | ----- | ---------- |
| RAD    | Rapid Application Development | Sim   | `monitor4` |
| PWEB   | Programação Web               | Sim   | Nenhum     |
| BD1    | Banco de Dados I              | Não   | Nenhum     |

## Requisitos pendentes

Nenhum.

## Método HTTP das ações

Assumir, responder e encerrar alteram a situação da dúvida. Por isso, essas ações usam POST com token CSRF. GET serve apenas para consultar informações e não deve alterar dados.
