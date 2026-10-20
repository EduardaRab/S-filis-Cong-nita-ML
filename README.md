# Modelo Preditivo de Sífilis Congênita com Arquitetura Adaptável por Configuração Externa

![Status](https://img.shields.io/badge/status-em%20andamento-yellow)
![Tipo](https://img.shields.io/badge/tipo-inicia%C3%A7%C3%A3o%20cient%C3%ADfica-blue)
![Institui%C3%A7%C3%A3o](https://img.shields.io/badge/institui%C3%A7%C3%A3o-USF-004a8f)
![Edital](https://img.shields.io/badge/edital-2026%2F2027-lightgrey)

Projeto de Iniciação Científica (IC) da Universidade São Francisco (USF), campi Itatiba e Sagrado Coração. Edital 2026/2027.

> 📄 Para o detalhamento completo (dicionário de dados campo a campo, metodologia passo a passo, arquitetura proposta, glossário etc.), veja a [Documentação Técnica](DOCUMENTACAO_TECNICA.md).

## Sumário

- [Equipe](#equipe)
- [Resumo](#resumo)
- [Objetivos](#objetivos)
- [Dados](#dados)
- [Primeiros passos](#primeiros-passos)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Metodologia](#metodologia)
- [Cronograma (2026/2027)](#cronograma-20262027)
- [Referências](#referências)

## Equipe

| Papel | Nome |
|---|---|
| Coordenadora | Profª Dra. Grace Miriam de Almeida Pfaffenbach |
| Colaboradora | Profª Msc. Débora Meyhofer Ferreira |
| Aluno de IC: Modelo Preditivo | Lucas Marques Custodio (Eng. Computação, Itatiba) |
| Aluna de IC: Engenharia de Dados | Eduarda Rabelo Oliveira (Eng. Computação, Sagrado) |
| Aluna de IC: Fundamentação Epidemiológica | Ester França Simenes (Enfermagem, Sagrado Coração) |
| Aluna de IC: Projeto relacionado | Naylla Gabriely Silva Fernandes (Enfermagem, Sagrado Coração) |

O projeto guarda-chuva se divide em três planos de trabalho complementares:

1. **Desenvolvimento de Modelo Preditivo com Arquitetura Adaptável para Sífilis Congênita** (Lucas): construção e avaliação de modelos de aprendizado de máquina para estimar o risco de sífilis congênita, com arquitetura configurável externamente (algoritmo, variáveis e hiperparâmetros definidos por arquivo de configuração, sem alterar o código-fonte).
2. **Desenvolvimento de Banco de Dados com Arquitetura Adaptável para Sífilis Congênita** (Eduarda): pipeline de engenharia de dados (ETL/ELT) que extrai, limpa, padroniza e armazena os dados públicos que alimentam o modelo preditivo.
3. **Calibração Contextual de API Preditiva de Sífilis Congênita a partir de Dados Agregados de Vigilância** (Ester): fundamentação epidemiológica do projeto, com revisão sistemática de fatores de risco populacionais, análise de completude e consistência das variáveis do SINAN (2015–2025) e definição de indicadores agregados com limiares de alerta (verde/amarelo/vermelho) que orientam o preenchimento do arquivo de configuração.

> **Sobre a Naylla:** o plano dela, *"Telemonitoramento para Apoio ao Aleitamento Materno e Cuidados com o Recém-Nascido nos Primeiros Seis Meses de Vida"*, pertence a um **projeto de pesquisa distinto** da mesma coordenadora, descrito no próprio plano como complementar ao projeto guarda-chuva. Não usa as bases DATASUS deste repositório, mas faz parte do grupo de pesquisa e é coautora do artigo metodológico.

## Resumo

A sífilis congênita é um relevante problema de saúde pública, apesar de ser uma condição amplamente evitável com diagnóstico precoce e tratamento adequado no pré-natal. A transmissão vertical, decorrente de infecção materna não tratada ou tratada de forma inadequada, pode levar a abortamento, natimortalidade, prematuridade e sequelas neonatais.

Este projeto propõe o desenvolvimento e a avaliação de modelos preditivos de sífilis congênita a partir de dados epidemiológicos públicos (DATASUS/SINASC e SINAN), com uma arquitetura computacional modular e adaptável por configuração externa, que permite selecionar algoritmos, variáveis de entrada e hiperparâmetros sem alterar a estrutura do código.

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
- Definição de indicadores epidemiológicos agregados (ex.: cobertura de pré-natal, tratamento de parceiros, vulnerabilidade social, oportunidade da notificação) e seus limiares de alerta, para calibrar o arquivo de configuração (Ester).
- Documentação do sistema e dos resultados, com produção de relatórios técnicos e possível publicação científica.

## Dados

Os dados utilizados são públicos, disponibilizados pelo Ministério da Saúde (DATASUS), e ficam em `data/raw/` (fora do Git):

| Base | Sistema | Conteúdo | Abrangência | Arquivos | Registros |
|---|---|---|---|---|---:|
| **DNSP** | SINASC: Sistema de Informações sobre Nascidos Vivos | Declarações de Nascido Vivo (DN): idade materna, escolaridade, pré-natal, gestação, parto, peso, Apgar etc. | **Só mães residentes em SP** | `DNSP2015.csv` a `DNSP2024.csv` | 5.601.469 |
| **SIFCBR** | SINAN: Sistema de Informação de Agravos de Notificação | Notificações de sífilis congênita: diagnóstico, exames laboratoriais, tratamento, evolução do caso. | **Brasil** (dados preliminares; 2025 parcial) | `SIFCBR15.csv` a `SIFCBR25.csv` | 258.372 |

> **Atenção:**
> - As duas bases têm abrangências diferentes: para cruzá-las, filtre o SINAN para residentes em SP (`SG_UF = 35`).
> - Os CSVs pesam entre ~2 MB e ~140 MB cada e **não são versionados** no Git (ver `.gitignore`). Mesmo sendo públicos e anonimizados, trate-os com o cuidado de dados sensíveis de saúde.
> - Onde baixar, como converter os `.dbc` do DATASUS e como ler corretamente: seções [6.2](DOCUMENTACAO_TECNICA.md#62-como-obter-os-dados) e [6.3](DOCUMENTACAO_TECNICA.md#63-como-usar-os-dados-leitura-correta-em-python) da documentação técnica.

## Primeiros passos

Ambiente testado em 2026-10-20 com **Python 3.14.7** no Windows 11: instalação completa e leitura dos CSVs reais conferida com as contagens da tabela acima.

1. **Instale o Python 3.14** ([python.org](https://www.python.org/downloads/), marcando "Add python.exe to PATH").
2. **Clone o repositório** e entre na pasta:

   ```bash
   git clone https://github.com/EduardaRab/S-filis-Cong-nita-ML.git
   ```

3. **Crie e ative o ambiente virtual** (PowerShell, dentro da pasta do repositório):

   ```bash
   python -m venv .venv
   ```

   ```bash
   .venv\Scripts\Activate.ps1
   ```

   > Se o PowerShell bloquear o script, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

4. **Instale as dependências** (versões fixadas no `requirements.txt`):

   ```bash
   pip install -r requirements.txt
   ```

   > O `pyreaddbc`, usado só para converter arquivos `.dbc` novos do DATASUS, não está na instalação padrão: no Windows ele precisa do "Microsoft C++ Build Tools". Os CSVs atuais já estão convertidos.

5. **Coloque os dados** (`DNSP*.csv` e `SIFCBR*.csv`) em `data/raw/`. Veja [`data/README.md`](data/README.md).
6. **No PyCharm**, selecione `.venv\Scripts\python.exe` como interpretador.
7. **Teste a leitura** com o exemplo da [seção 6.3](DOCUMENTACAO_TECNICA.md#63-como-usar-os-dados-leitura-correta-em-python), apontando `PASTA` para `data/raw`, e confira as contagens da tabela acima.

Detalhes e solução de problemas: [seção 13.2 da documentação técnica](DOCUMENTACAO_TECNICA.md#132-configurando-o-ambiente-python). Decisões já tomadas e próximos passos: [seção 20](DOCUMENTACAO_TECNICA.md#20-roadmap-técnico--próximos-passos).

## Estrutura do repositório

```
S-filis-Cong-nita-ML/
├── README.md                  # este arquivo
├── DOCUMENTACAO_TECNICA.md    # documentação técnica completa (fonte oficial)
├── ROTEIRO_POWER_BI.md        # modelo e páginas do painel do Power BI (o painel fica na pasta local)
├── requirements.txt           # dependências Python com versões testadas
├── .gitignore                 # o que fica fora do Git (dados, PDFs, ambiente, cache)
├── data/                      # dados (conteúdo NÃO versionado; ver data/README.md)
│   ├── raw/                   # originais do DATASUS, sem alteração (DNSP*.csv, SIFCBR*.csv)
│   ├── processed/             # dados tratados pelo pipeline, prontos para modelagem
│   └── outputs/               # resultados: métricas, modelos treinados, tabelas e figuras
├── src/                       # código-fonte Python (pipeline, modelagem, utilitários)
├── notebooks/                 # notebooks Jupyter de análise exploratória
└── config/                    # arquivos YAML de configuração externa (experimentos e indicadores)
```

Cada pasta tem um `README.md` explicando o que vai nela e quem grava. Regras principais:

- **`data/raw/` é somente leitura:** os arquivos originais nunca são editados; correções vão para `data/processed/`.
- **Nenhum dado vai para o Git:** o `.gitignore` ignora o conteúdo de `data/` e arquivos `*.csv`, `*.dbc`, `*.parquet`, `*.pkl`, mantendo só as pastas.
- **Configuração fora do código:** algoritmos, variáveis e hiperparâmetros ficam em `config/`, não em `src/`.

Ainda não há código implementado. Quando o pipeline e o modelo existirem, este README receberá as instruções de execução.

## Metodologia

Pesquisa aplicada, de caráter quantitativo e experimental, dividida em três frentes que se retroalimentam:

1. **Engenharia de dados (pipeline ETL/ELT):** extração das bases SINASC/SINAN, tratamento de inconsistências e valores ausentes, padronização de variáveis categóricas, integração das duas fontes e armazenamento estruturado (banco de dados relacional/analítico).
2. **Modelagem preditiva:** treinamento e validação cruzada de diferentes algoritmos de classificação, comparação de desempenho e ajuste de hiperparâmetros, com módulos desacoplados e configuração externa.
3. **Fundamentação epidemiológica:** revisão sistemática, análise de completude do SINAN e definição de indicadores agregados com limiares de alerta que calibram o arquivo de configuração.

## Cronograma (2026/2027)

| Período | Atividades |
|---|---|
| Ago–Out/2026 | Levantamento bibliográfico; estudo das bases públicas e definição de variáveis; planejamento da arquitetura do sistema/pipeline. |
| Nov/2026–Jan/2027 | Pré-processamento e limpeza dos dados; análise exploratória; implementação inicial do pipeline e dos primeiros modelos; testes iniciais de treinamento/validação. |
| Fev–Abr/2027 | Ajuste de parâmetros e comparação entre algoritmos; implementação da arquitetura adaptável por configuração externa; testes robustos de desempenho; apresentação de resultados parciais em evento de IC. |
| Mai–Jul/2027 | Finalização do modelo e do pipeline; validação do sistema; relatório final; preparação de artigo científico. |

Cronograma detalhado por frente (Eduarda, Lucas e Ester) na [seção 16 da documentação técnica](DOCUMENTACAO_TECNICA.md#16-cronograma-detalhado).

## Referências

- BRASIL. Ministério da Saúde. *Protocolo Clínico e Diretrizes Terapêuticas para Atenção Integral às Pessoas com Infecções Sexualmente Transmissíveis (IST)*. Brasília: Ministério da Saúde, 2022.
- WORLD HEALTH ORGANIZATION (WHO). *Global progress report on HIV, viral hepatitis and sexually transmitted infections*. Geneva: WHO, 2021.
- KOURENTZES, N.; BARROW, D. K.; CRONE, S. F. Neural network ensemble operators for time series forecasting. *Expert Systems with Applications*, v. 41, n. 9, p. 4235–4244, 2014.
- OBERMEYER, Z.; EMANUEL, E. J. Predicting the future: big data, machine learning, and clinical medicine. *The New England Journal of Medicine*, v. 375, n. 13, p. 1216–1219, 2016.
- SOMMERVILLE, I. *Engenharia de Software*. 10. ed. São Paulo: Pearson, 2019.
- ALURA. *O que é engenharia de dados*. 2023.
- ACCURATE. *Engenharia de dados e sua importância para BI e BA*. 2024.
- BRASIL. Ministério da Saúde. *Boletim Epidemiológico: Sífilis 2021*. Brasília: MS, 2021.
- BRASIL. Ministério da Saúde. Secretaria de Vigilância em Saúde. *Caderno de Análise: Roteiro para uso do SINAN Net, análise da qualidade da base de dados e cálculo de indicadores epidemiológicos e operacionais*. Brasília: MS, 2019.
- DOMINGUES, C. S. B. et al. Protocolo Brasileiro para Infecções Sexualmente Transmissíveis 2020: sífilis congênita e criança exposta à sífilis. *Epidemiologia e Serviços de Saúde*, v. 30, spe1, e2020597, 2021.
- MAURINA, E. et al. Perfil epidemiológico dos casos notificados de Sífilis Congênita na Cidade de Caxias do Sul/RS. *Revista Eletrônica Acervo Saúde*, v. 25, n. 1, 2025.
- MONTEIRO NETA, A. M. S. et al. Sífilis gestacional e congênita: limitações na completude dos registros de notificação. *ARevis7*, v. 7, n. 11, 2025.
- SOARES, M. A. S.; AQUINO, R. Completude e caracterização dos registros de sífilis gestacional e congênita na Bahia, 2007-2017. *Epidemiologia e Serviços de Saúde*, v. 30, n. 4, 2021.
- TEIXEIRA, K. K. S. et al. Qualidade dos dados do sistema de vigilância epidemiológica de sífilis congênita. *Journal of Human Growth and Development*, v. 35, n. 2, p. 210-220, 2025.
