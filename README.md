# Modelo Preditivo de Sífilis Congênita com Arquitetura Adaptável por Configuração Externa

![Status](https://img.shields.io/badge/status-em%20andamento-yellow)
![Tipo](https://img.shields.io/badge/tipo-inicia%C3%A7%C3%A3o%20cient%C3%ADfica-blue)
![Institui%C3%A7%C3%A3o](https://img.shields.io/badge/institui%C3%A7%C3%A3o-USF-004a8f)
![Edital](https://img.shields.io/badge/edital-2026%2F2027-lightgrey)

Projeto de Iniciação Científica (IC) — Universidade São Francisco (USF), campus Itatiba/Sagrado.
Edital 2026/2027.

## Sumário

- [Equipe](#equipe)
- [Resumo](#resumo)
- [Objetivos](#objetivos)
- [Dados](#dados)
- [Metodologia](#metodologia)
- [Cronograma (2026/2027)](#cronograma-20262027)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Referências](#referências)

## Equipe

| Papel | Nome |
|---|---|
| Coordenadora | Profª Dra. Grace Miriam de Almeida Pfaffenbach |
| Colaboradora | Profª Msc. Débora Meyhofer Ferreira |
| Aluno de IC — Modelo Preditivo | Lucas Marques Custodio (Eng. Computação, Itatiba) |
| Aluna de IC — Engenharia de Dados | Eduarda Rabelo Oliveira (Eng. Computação, Sagrado) |

O projeto guarda-chuva se divide em dois planos de trabalho complementares:

1. **Desenvolvimento de Modelo Preditivo com Arquitetura Adaptável para Sífilis Congênita** (Lucas) — construção e avaliação de modelos de aprendizado de máquina para estimar risco de sífilis congênita, com arquitetura configurável externamente (algoritmo, variáveis e hiperparâmetros definidos por arquivo de configuração, sem alterar o código-fonte).
2. **Desenvolvimento de Banco de Dados com Arquitetura Adaptável para Sífilis Congênita** (Eduarda) — construção do pipeline de engenharia de dados (ETL/ELT) que extrai, limpa, padroniza e armazena os dados públicos que alimentam o modelo preditivo.

## Resumo

A sífilis congênita é um relevante problema de saúde pública, apesar de ser uma condição amplamente evitável com diagnóstico precoce e tratamento adequado no pré-natal. A transmissão vertical, decorrente de infecção materna não tratada ou tratada de forma inadequada, pode levar a abortamento, natimortalidade, prematuridade e sequelas neonatais.

Este projeto propõe o desenvolvimento e a avaliação de modelos preditivos de sífilis congênita a partir de dados epidemiológicos públicos (DATASUS/SINASC e SINAN), utilizando uma arquitetura computacional modular e adaptável por configuração externa — permitindo selecionar algoritmos, variáveis de entrada e hiperparâmetros sem necessidade de alteração estrutural do código.

## Objetivos

**Objetivo geral:** desenvolver e avaliar um modelo preditivo baseado em aprendizado de máquina, com arquitetura modular adaptável por configuração externa, capaz de estimar o risco de ocorrência de sífilis congênita a partir de dados epidemiológicos, apoiando a análise e a tomada de decisão em saúde pública.

**Objetivos específicos:**

- Levantamento bibliográfico sobre sífilis congênita, fatores de risco associados e aplicações de ciência de dados/ML em saúde.
- Identificação e compreensão de variáveis epidemiológicas relevantes a partir de bases públicas.
- Construção do pipeline de dados (extração, tratamento, transformação e carregamento) e do banco de dados estruturado que servirá de base para o modelo.
- Pré-processamento dos dados: tratamento de valores ausentes, normalização, codificação de variáveis categóricas e balanceamento de classes.
- Implementação e comparação de diferentes algoritmos de classificação (Regressão Logística, Random Forest, Support Vector Machine, Redes Neurais Artificiais).
- Desenvolvimento da arquitetura adaptável por configuração externa (seleção de algoritmo, variáveis e hiperparâmetros via arquivo de configuração).
- Avaliação de desempenho com métricas de classificação: acurácia, precisão, recall, F1-score e área sob a curva ROC.
- Aplicação de técnicas de interpretabilidade (importância de variáveis) para relacionar resultados a fatores epidemiológicos conhecidos.
- Documentação do sistema e dos resultados, com produção de relatórios técnicos e possível publicação científica.

## Dados

Os dados utilizados são públicos, disponibilizados pelo Ministério da Saúde (DATASUS):

| Base | Sistema | Conteúdo | Arquivos neste repositório |
|---|---|---|---|
| **DNSP** | SINASC — Sistema de Informações sobre Nascidos Vivos | Declarações de Nascidos Vivo (DN): idade materna, escolaridade, pré-natal, gestação, parto, peso, Apgar etc. | `DNSP2015` a `DNSP2024` |
| **SIFCBR** | SINAN — Sistema de Informação de Agravos de Notificação | Notificações de sífilis congênita: diagnóstico, exames laboratoriais, tratamento, evolução do caso. | `SIFCBR15` a `SIFCBR25`  |

> **Atenção:** os arquivos CSV são bases brutas do DATASUS, pesam entre ~2 MB e ~140 MB cada e não devem ser versionados em um repositório Git (ver `.gitignore`). Ainda que os dados sejam públicos e anonimizados, recomenda-se tratá-los com o mesmo cuidado de dados sensíveis de saúde durante o desenvolvimento.

## Metodologia

Pesquisa aplicada, de caráter quantitativo e experimental, dividida em três frentes que se retroalimentam:

1. **Engenharia de dados (pipeline ETL/ELT):** extração das bases SINASC/SINAN, tratamento de inconsistências e valores ausentes, padronização de variáveis categóricas, integração das duas fontes e armazenamento estruturado (banco de dados relacional/analítico).
2. **Modelagem preditiva:** treinamento e validação cruzada de diferentes algoritmos de classificação, comparação de desempenho e ajuste de hiperparâmetros.
3. **Arquitetura adaptável por configuração externa:** módulos de carregamento de dados, pré-processamento, treinamento e avaliação desacoplados, com seleção de algoritmo/variáveis/hiperparâmetros via arquivo de configuração externo (sem alterar o código-fonte).

## Cronograma (2026/2027)

| Período | Atividades |
|---|---|
| Ago–Out/2026 | Levantamento bibliográfico; estudo das bases públicas e definição de variáveis; planejamento da arquitetura do sistema/pipeline. |
| Nov/2026–Jan/2027 | Pré-processamento e limpeza dos dados; análise exploratória; implementação inicial do pipeline e dos primeiros modelos; testes iniciais de treinamento/validação. |
| Fev–Abr/2027 | Ajuste de parâmetros e comparação entre algoritmos; implementação da arquitetura adaptável por configuração externa; testes robustos de desempenho; apresentação de resultados parciais em evento de IC. |
| Mai–Jul/2027 | Finalização do modelo e do pipeline; validação do sistema; relatório final; preparação de artigo científico. |

## Estrutura do repositório

```
Sifilis congenita/
├── README.md
├── DNSP20XX.csv                 # SINASC — nascidos vivos (2015-2024)
├── SIFCBR20XX.csv               # SINAN — sífilis congênita (2015-2025)
├── Lucas_-_Plano_de_Trabalho_...pdf     # plano de trabalho (modelo preditivo)
└── Plano_de_trabalho_Eduarda_Oliveira.pdf  # plano de trabalho (banco de dados/pipeline)
```

À medida que o pipeline e o modelo forem implementados, este README será atualizado com as instruções de execução (ambiente, dependências, arquivo de configuração e como rodar o treinamento/avaliação).

## Referências

- BRASIL. Ministério da Saúde. *Protocolo Clínico e Diretrizes Terapêuticas para Atenção Integral às Pessoas com Infecções Sexualmente Transmissíveis (IST)*. Brasília: Ministério da Saúde, 2022.
- WORLD HEALTH ORGANIZATION (WHO). *Global progress report on HIV, viral hepatitis and sexually transmitted infections*. Geneva: WHO, 2021.
- KOURENTZES, N.; BARROW, D. K.; CRONE, S. F. Neural network ensemble operators for time series forecasting. *Expert Systems with Applications*, v. 41, n. 9, p. 4235–4244, 2019.
- OBERMEYER, Z.; EMANUEL, E. J. Predicting the future — big data, machine learning, and clinical medicine. *The New England Journal of Medicine*, v. 375, n. 13, p. 1216–1219, 2016.
- SOMMERVILLE, I. *Engenharia de Software*. 10. ed. São Paulo: Pearson, 2019.
- ALURA. *O que é engenharia de dados*. 2023.
- ACCURATE. *Engenharia de dados e sua importância para BI e BA*. 2024.
