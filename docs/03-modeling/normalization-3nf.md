# Evidencia de Normalizacao ate 3FN

## 1FN
Todas as tabelas possuem atributos atomicos, sem grupos repetidos. Procedimentos realizados nao ficam em uma lista dentro de ATENDIMENTO; eles foram separados na tabela associativa PROCEDIMENTO_REALIZADO.

## 2FN
As tabelas com chave simples possuem todos os atributos dependentes da chave primaria. Na tabela PROCEDIMENTO_REALIZADO, que possui chave composta (`id_atendimento`, `id_procedimento`), os atributos quantidade, tempo_real_minutos, observacao e faturado dependem da combinacao completa entre atendimento e procedimento.

## 3FN
Nao ha dependencia transitiva relevante dentro das tabelas. Dados de pessoa ficam em PESSOA; dados especificos de paciente ficam em PACIENTE; dados profissionais ficam em PROFISSIONAL; dados de residente e preceptor ficam em suas tabelas especializadas. Assim, por exemplo, o nome do residente nao e armazenado em ATENDIMENTO, apenas sua FK.

## BCNF - Observacao
As principais dependencias funcionais usam chaves candidatas como determinantes, por exemplo CPF em PESSOA, CRM em PROFISSIONAL, codigo em PROCEDIMENTO e num_convenio em PACIENTE. A modelagem evita redundancia e anomalias de atualizacao.
