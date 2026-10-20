# Documentação Técnica — Modelo Preditivo de Sífilis Congênita com Arquitetura Adaptável por Configuração Externa

> Documento de referência técnica completo do projeto. O [README.md](README.md) é a porta de entrada resumida; este arquivo detalha contexto, metodologia, arquitetura, dados e cronograma para quem for efetivamente implementar, revisar ou dar continuidade ao projeto.

**Última atualização:** 2026-10-20
**Versão do documento:** 1.3 (ver [histórico de revisões](#21-histórico-de-revisões))
**Status do projeto:** Fase de planejamento e organização inicial dos dados (nenhum código de pipeline/modelagem implementado ainda; dados brutos inspecionados, perfilados e carregados num painel do Power BI)

**Guia rápido de leitura:** objetivo e escopo → [seção 4](#4-objetivos) · como obter e ler os dados → [6.2](#62-como-obter-os-dados) e [6.3](#63-como-usar-os-dados-leitura-correta-em-python) · estrutura e ambiente Python → [seção 13](#13-estrutura-de-repositório-e-organização-de-arquivos) · ferramentas → [13.1](#131-ferramentas-do-projeto) · decisões já tomadas e próximos passos → [seção 20](#20-roadmap-técnico--próximos-passos).

---

## Sumário

1. [Contexto institucional](#1-contexto-institucional)
2. [Problema e motivação](#2-problema-e-motivação)
3. [Estrutura do projeto: dois planos de trabalho](#3-estrutura-do-projeto-dois-planos-de-trabalho)
4. [Objetivos](#4-objetivos)
5. [Fundamentação teórica](#5-fundamentação-teórica)
6. [Fontes de dados](#6-fontes-de-dados)
7. [Dicionário de dados — SINASC (DNSP)](#7-dicionário-de-dados--sinasc-dnsp)
8. [Dicionário de dados — SINAN Sífilis Congênita (SIFCBR)](#8-dicionário-de-dados--sinan-sífilis-congênita-sifcbr)
9. [Metodologia detalhada](#9-metodologia-detalhada)
10. [Arquitetura do sistema (proposta)](#10-arquitetura-do-sistema-proposta)
11. [Algoritmos de classificação previstos](#11-algoritmos-de-classificação-previstos)
12. [Métricas de avaliação](#12-métricas-de-avaliação)
13. [Estrutura de repositório e organização de arquivos](#13-estrutura-de-repositório-e-organização-de-arquivos)
14. [Controle de versão e fluxo de trabalho Git](#14-controle-de-versão-e-fluxo-de-trabalho-git)
15. [Considerações éticas, legais e de privacidade](#15-considerações-éticas-legais-e-de-privacidade)
16. [Cronograma detalhado](#16-cronograma-detalhado)
17. [Produção científica esperada](#17-produção-científica-esperada)
18. [Glossário](#18-glossário)
19. [Referências bibliográficas](#19-referências-bibliográficas)
20. [Roadmap técnico / próximos passos](#20-roadmap-técnico--próximos-passos)
21. [Histórico de revisões](#21-histórico-de-revisões)

---

## 1. Contexto institucional

| Item | Detalhe |
|---|---|
| Instituição | Universidade São Francisco (USF) |
| Programa | Edital de Iniciação Científica Tecnológica e/ou Extensão — 2026/2027 |
| Projeto de pesquisa (guarda-chuva) | "Modelo Preditivo de Sífilis Congênita com Arquitetura Adaptável por Configuração Externa" |
| Coordenadora | Profª Dra. Grace Miriam de Almeida Pfaffenbach |
| Colaboradora | Profª Msc. Débora Meyhofer Ferreira |
| Data de assinatura dos planos de trabalho | 23 de abril de 2026 |
| Área estratégica USF | Ensino e aprendizagem, avaliação e tecnologias educacionais; Tecnologia, inovação e empreendedorismo |

O projeto é conduzido por **dois alunos de IC**, cada um com um plano de trabalho formalmente distinto, submetido e assinado separadamente, mas que compõem uma única pesquisa integrada:

| Aluno(a) | Curso | Campus | Semestre | Foco do plano de trabalho |
|---|---|---|---|---|
| Lucas Marques Custodio | Engenharia da Computação | Itatiba | 4º | Modelo preditivo (Machine Learning) |
| Eduarda Rabelo Oliveira | Engenharia da Computação | Sagrado | 5º | Engenharia de dados / pipeline / banco de dados |

> Dados pessoais dos planos de trabalho (RA, CPF, RG, endereço, telefone) foram **deliberadamente omitidos** deste documento e não devem ser incluídos em nenhum arquivo versionado no Git — ver [seção 15](#15-considerações-éticas-legais-e-de-privacidade).

## 2. Problema e motivação

A sífilis congênita é uma infecção de transmissão vertical (mãe → feto) causada pelo *Treponema pallidum*, decorrente de sífilis materna não tratada ou tratada de forma inadequada durante a gestação. É considerada um agravo **amplamente evitável**, desde que haja diagnóstico precoce e tratamento correto no pré-natal — e por isso mesmo é utilizada como indicador de qualidade da atenção pré-natal em um país ou região.

Apesar disso, o Brasil mantém taxas de incidência persistentemente altas, o que indica falhas sistêmicas em pelo menos um destes pontos:

- Cobertura e qualidade do acompanhamento pré-natal;
- Testagem oportuna da gestante e do parceiro;
- Tratamento adequado (esquema, dose, oportunidade) da gestante diagnosticada;
- Notificação e seguimento do recém-nascido exposto.

**Desfechos possíveis quando a transmissão vertical ocorre:** abortamento, natimortalidade, prematuridade, baixo peso ao nascer e sequelas neonatais (ósseas, neurológicas, hepáticas, entre outras).

**Hipótese de trabalho do projeto:** cruzando variáveis sociodemográficas e assistenciais disponíveis publicamente (idade materna, escolaridade, número de consultas de pré-natal, tipo de parto, raça/cor, região de residência etc.) com os registros de notificação de sífilis congênita, é possível treinar um modelo de classificação capaz de estimar o **risco/propensão** de um caso associado a determinado perfil, servindo como ferramenta de apoio à vigilância epidemiológica — não como ferramenta de diagnóstico clínico individual.

## 3. Estrutura do projeto: dois planos de trabalho

### 3.1 Plano de trabalho 1 — "Desenvolvimento de Modelo Preditivo com Arquitetura Adaptável para Sífilis Congênita" (Lucas Marques Custodio)

Foco: a camada de **ciência de dados e machine learning** propriamente dita — modelagem, comparação de algoritmos, avaliação de desempenho, interpretabilidade e a arquitetura configurável que permite trocar algoritmo/variáveis/hiperparâmetros sem mexer no código-fonte.

### 3.2 Plano de trabalho 2 — "Desenvolvimento de Banco de Dados com Arquitetura Adaptável para Sífilis Congênita" (Eduarda Rabelo Oliveira)

Foco: a camada de **engenharia de dados** — pipeline ETL/ELT que extrai as bases brutas do DATASUS/SINAN, trata inconsistências e valores ausentes, padroniza variáveis e carrega o resultado em um banco de dados estruturado (relacional ou analítico), que serve de insumo para o plano de trabalho do Lucas.

### 3.3 Relação de dependência entre os dois planos

```
 SINASC (DNSP)  ──┐
                  ├──▶  [ Pipeline ETL/ELT ]  ──▶  [ Banco de dados tratado ]  ──▶  [ Modelagem ML ]  ──▶  Modelo + avaliação + interpretabilidade
 SINAN  (SIFCBR)──┘        (Eduarda)                  (saída da Eduarda)            (Lucas)
```

Ou seja: **o trabalho da Eduarda é pré-requisito de dados para o trabalho do Lucas.** A "arquitetura adaptável por configuração externa" é um conceito compartilhado pelos dois planos, mas aplicado em camadas diferentes: ela na composição do pipeline de tratamento de dados, ele na seleção de algoritmo/variáveis/hiperparâmetros de modelagem.

## 4. Objetivos

### 4.1 Objetivo geral (projeto integrado)

Desenvolver e avaliar um modelo preditivo baseado em técnicas de aprendizado de máquina, com arquitetura modular adaptável por configuração externa, capaz de estimar o risco de ocorrência de sífilis congênita a partir de dados epidemiológicos públicos, apoiado por um pipeline de engenharia de dados que garanta a qualidade e a integridade das informações utilizadas.

### 4.2 Objetivos específicos — consolidados dos dois planos

**Bibliográficos / conceituais**
- Levantamento bibliográfico sobre sífilis congênita, fatores de risco associados, e aplicações de ciência de dados / engenharia de dados / aprendizado de máquina em saúde (bases: Scopus, Web of Science, IEEE Xplore, Google Scholar).
- Identificação e compreensão das variáveis epidemiológicas relevantes disponíveis nas bases públicas.

**Engenharia de dados (Eduarda)**
- Projetar e implementar um pipeline de dados com etapas de ingestão, tratamento, transformação e carregamento (ETL/ELT).
- Tratar inconsistências: valores ausentes, duplicidades, padronização de formatos, normalização de variáveis.
- Modelar e estruturar um banco de dados (relacional ou analítico) para os dados tratados, com integridade, consistência e eficiência de acesso.
- Aplicar validação e controle de qualidade dos dados (consistência, duplicidade, integridade).
- Disponibilizar a base tratada para consumo por ferramentas analíticas e pelos modelos de ML.
- Documentar o pipeline e a modelagem do banco de dados.

**Modelagem preditiva (Lucas)**
- Pré-processar os dados: valores ausentes, normalização, codificação categórica, balanceamento de classes.
- Implementar e comparar múltiplos algoritmos de classificação.
- Desenvolver a arquitetura adaptável por configuração externa (seleção de algoritmo/variáveis/hiperparâmetros via arquivo de configuração, sem alteração do código-fonte).
- Avaliar desempenho com métricas apropriadas de classificação (ver [seção 12](#12-métricas-de-avaliação)).
- Aplicar técnicas de interpretabilidade (importância de variáveis).
- Analisar resultados à luz do contexto epidemiológico.
- Documentar o sistema e os resultados, produzindo relatórios técnicos e, se possível, publicação científica.

### 4.3 Escopo

**Dentro do escopo**

| Item | Detalhe |
|---|---|
| Bases de dados | SINASC (nascidos vivos) e SINAN — Sífilis Congênita, microdados públicos do DATASUS ([seção 6](#6-fontes-de-dados)) |
| Período | 2015–2024 (anos completos nas duas bases); 2025 como dado parcial/preliminar |
| Recorte geográfico atual | SINASC: estado de São Paulo · SINAN: Brasil (para cruzar com o SINASC, só residentes em SP) — ver decisão pendente abaixo |
| Produto de dados | Pipeline ETL/ELT reprodutível + base tratada e documentada |
| Produto de modelagem | Modelos de classificação comparados (RL, RF, SVM, RNA), configuráveis por arquivo externo, com avaliação e interpretabilidade |
| Produto de análise | Painel exploratório no Power BI ([ROTEIRO_POWER_BI.md](ROTEIRO_POWER_BI.md)) |
| Uso pretendido | **Apoio à vigilância epidemiológica** e à pesquisa — estimar risco/propensão por perfil ou território |

**Fora do escopo**

- Diagnóstico ou decisão clínica individual — o modelo **não** substitui avaliação profissional.
- Uso de dados identificados (nome, CPF, endereço) ou de bases não públicas.
- Colocar o modelo em produção (sistema em uso real por serviços de saúde) — o projeto entrega protótipo e avaliação.
- Outros agravos (sífilis adquirida, sífilis em gestante) e outras bases (SIM, SIH, CNES), salvo decisão futura registrada na [seção 20](#20-roadmap-técnico--próximos-passos).

**Em aberto (afetam o escopo):** recorte geográfico final (só SP ou Brasil), estratégia de integração SINASC × SINAN (individual ou agregada) e uso de 2025 — ver [seção 20](#20-roadmap-técnico--próximos-passos).

## 5. Fundamentação teórica

Resumo dos principais pontos levantados na introdução dos dois planos de trabalho, que devem orientar a revisão de literatura:

- **Sistemas de informação em saúde no Brasil** (DATASUS, SINAN) disponibilizam grandes volumes de dados epidemiológicos sobre sífilis, incluindo variáveis sociodemográficas, clínicas e de pré-natal — base relevante para ferramentas analíticas de predição de risco (BRASIL, 2022).
- **Machine learning em saúde pública**: técnicas de ciência de dados identificam padrões complexos e não lineares que métodos estatísticos tradicionais frequentemente não capturam (KOURENTZES; BARROW; CRONE, 2014), e modelos preditivos já são amplamente usados para apoio à decisão clínica/epidemiológica e estratificação de risco (OBERMEYER; EMANUEL, 2016).
- **Desafio de flexibilidade estrutural**: sistemas preditivos tradicionais costumam ter baixa flexibilidade para se adaptar a novas bases, novos algoritmos ou novos hiperparâmetros — daí a proposta de uma arquitetura modular e configurável, alinhada a princípios de engenharia de software (SOMMERVILLE, 2019).
- **Engenharia de dados como fundação**: a qualidade de qualquer modelo preditivo depende diretamente da qualidade do dado que o alimenta; pipelines ETL/ELT bem estruturados garantem confiabilidade, escalabilidade e reprodutibilidade (ALURA, 2023; ACCURATE, 2024).

> Esta seção deve ser expandida durante a fase de revisão bibliográfica (Ago–Out/2026) com achados específicos sobre: (a) fatores de risco já descritos na literatura para sífilis congênita, (b) trabalhos anteriores que aplicaram ML a dados do SINASC/SINAN, e (c) técnicas de record linkage entre bases de saúde pública brasileiras sem identificador único compartilhado.

## 6. Fontes de dados

Ambas as bases são públicas, mantidas pelo Ministério da Saúde via **DATASUS** (Departamento de Informática do SUS) e disponibilizadas pelo TabNet/FTP público do DATASUS.

| Sigla | Sistema completo | Órgão gestor | Unidade de registro | Abrangência geográfica | Anos disponíveis na pasta |
|---|---|---|---|---|---|
| **SINASC** (arquivos `DNSP*`) | Sistema de Informações sobre Nascidos Vivos | Ministério da Saúde / DATASUS | 1 linha = 1 nascido vivo (Declaração de Nascido Vivo — DN) | **Somente estado de São Paulo** (mães residentes em SP) | 2015–2024 |
| **SINAN** (arquivos `SIFCBR*`) | Sistema de Informação de Agravos de Notificação — agravo "Sífilis Congênita" | Ministério da Saúde / DATASUS | 1 linha = 1 notificação de caso | **Brasil inteiro** (27 UFs) | 2015–2025 (2025 parcial) |

> **Convenção de nomes do DATASUS:** `DN` + `SP` + ano = Declarações de Nascido vivo da UF **SP**; `SIFC` + `BR` + ano = Sífilis Congênita, **BR**asil. O sufixo de UF no nome do arquivo indica o recorte geográfico.

**Formato:** CSV, delimitador `,`, cabeçalho na primeira linha, valores numéricos de domínio (códigos) em vez de texto livre na maioria das variáveis. Ver [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos) para as particularidades de formato encontradas em cada arquivo.

**Tamanho:** arquivos `DNSP*` entre ~105 MB e ~140 MB cada (~470 a ~634 mil nascimentos/ano, só SP); arquivos `SIFCBR*` entre ~2,7 MB e ~5,8 MB cada (~20 a ~27 mil notificações/ano, Brasil todo — notificação de agravo é evento raro comparado a nascimento).

**Abrangências diferentes entre as bases (ponto crítico):** como o SINASC disponível cobre **apenas SP** e o SINAN cobre **o Brasil inteiro**, qualquer cruzamento entre as duas bases precisa primeiro **filtrar o SINAN para residentes em SP** (`SG_UF = 35` / `ID_MN_RESI` iniciando em `35`). Sem esse filtro, ~83% dos casos do SINAN (ex.: 2024 — 20.397 de 24.631) não têm nenhum nascimento correspondente na base de nascidos vivos, o que inviabiliza o linkage e distorce qualquer taxa calculada (numerador nacional sobre denominador estadual). Se o projeto quiser escala nacional, será necessário baixar os arquivos `DN<UF>` das demais UFs (ou `DNBR`).

**Desafio metodológico central:** SINASC e SINAN **não compartilham um identificador único de paciente**. Para unir nascimento (SINASC) e notificação de sífilis congênita (SINAN) referentes ao mesmo indivíduo, normalmente é necessário aplicar técnicas de **relacionamento probabilístico de registros (record linkage)** — por exemplo, cruzando município de residência, data de nascimento, nome da mãe (quando disponível) e faixas de data — ou, alternativamente, tratar as duas bases como **agregados por período/município** (abordagem ecológica) em vez de linkage individual. Essa decisão de desenho é crítica e deve ser definida explicitamente antes da fase de modelagem, pois muda completamente a granularidade do problema (predição a nível de indivíduo vs. predição a nível de município/período).

### 6.1 Perfil real dos dados (verificado nos arquivos)

> Levantamento feito diretamente sobre os CSVs da pasta do projeto em 2026-10-14 (leitura linha a linha, sem amostragem, exceto onde indicado). Deve ser refeito sempre que os arquivos forem substituídos por novas extrações do DATASUS.

**Volume de registros por ano**

| Ano | SINASC — nascidos vivos (SP) | SINAN — notificações SC (Brasil) | SINAN — residentes em SP (`SG_UF = 35`) |
|---|---:|---:|---:|
| 2015 | 634.026 | 19.800 | 3.439 |
| 2016 | 601.437 | 21.421 | 3.721 |
| 2017 | 611.803 | 25.374 | 4.127 |
| 2018 | 606.146 | 26.874 | 4.063 |
| 2019 | 583.191 | 25.586 | 3.982 |
| 2020 | 552.310 | 23.064 ¹ | 3.602 |
| 2021 | 525.239 | 27.186 | 4.072 |
| 2022 | 512.520 | 26.515 | 4.538 |
| 2023 | 503.910 | 25.291 | 4.351 |
| 2024 | 470.887 | 24.631 | 4.234 |
| 2025 | — (não disponível) | 12.630 (**ano parcial**) | 2.133 |
| **Total** | **5.601.469** | **258.372** | **42.262** |

¹ `SIFCBR20.csv` tem 23.065 linhas físicas, mas um registro (linha 16.624) tem uma quebra de linha dentro de um campo de texto entre aspas — são 23.064 registros. Um leitor de CSV que respeita aspas (pandas, Power Query) conta corretamente; contar linhas com `wc -l`/`ReadLine` dá um a mais. Conferido no Power BI em 2026-10-14.

- **Desbalanceamento esperado:** a razão bruta entre notificações de SC em residentes de SP e nascidos vivos em SP fica entre ~0,5% e ~0,9% ao ano. Na modelagem a nível individual, a classe positiva tende a ficar abaixo de 1% — reforça a necessidade de balanceamento e de métricas apropriadas ([seção 12](#12-métricas-de-avaliação)). *Atenção: essa razão é só ordem de grandeza — o numerador é por ano de notificação, não por ano de nascimento.*
- **2025 é parcial** (cerca de metade do volume dos anos anteriores) e não tem SINASC correspondente; deve ser excluído do treino ou tratado à parte (ex.: só como conjunto de validação temporal futura).
- **Todos os registros do SINAN são casos confirmados** (`EVO_DIAG_N` 1–4 em 100% das linhas; não há descartados). Distribuição 2015–2025: sífilis congênita recente 240.165 · tardia 423 · **aborto por sífilis 10.170** · **natimorto por sífilis 7.614**.
- **17.784 casos (6,9%) são aborto ou natimorto** e **nunca aparecem no SINASC**, que só registra nascidos vivos. Qualquer linkage individual SINAN × SINASC deixa esses casos de fora por definição — o que precisa ser tratado explicitamente (excluir do rótulo, ou modelar à parte) e reportado como limitação. Conferido no Power BI em 2026-10-20.

**Diferenças de schema entre arquivos (armadilhas para a ingestão)**

| Arquivo(s) | Particularidade | Impacto |
|---|---|---|
| `DNSP2015.csv`, `DNSP2017.csv` | Coluna `contador` em **minúsculas** e na **1ª posição** | Nos demais anos é `CONTADOR`, na **última** posição. Ler por **nome** (normalizando maiúsculas), nunca por posição. |
| `SIFCBR23.csv` | **65 colunas**: tem uma coluna extra `DT_NASC` na **posição 8** (entre `ID_REGIONA` e `DT_DIAG`) | Todas as colunas seguintes ficam deslocadas em relação aos outros anos. Ler por nome. `DT_NASC` (data de nascimento da criança) só existe neste ano, mas seria muito útil para linkage com o SINASC. |
| Demais `SIFCBR*` | 64 colunas, cabeçalho idêntico | — |
| Demais `DNSP*` | 61 colunas, cabeçalho idêntico | — |

**Formatos de valores**

| Aspecto | SINASC (`DNSP`) | SINAN (`SIFCBR`) |
|---|---|---|
| Datas | Texto `DDMMAAAA` sem separador (ex.: `06062024`) | ISO `AAAA-MM-DD` (ex.: `2024-11-06`) |
| Códigos com zero à esquerda | Presentes (ex.: `QTDFILVIVO`, `QTDFILMORT` = `00`) — ler como texto para não perder o zero | Presentes (ex.: `ESCOLMAE` = `03`) |
| Números | Inteiros | Alguns campos numéricos vêm como float (`ANT_IDADE` = `23.0`, `LABC_TIT_1` = `64.0`) |
| Idade codificada | — | `NU_IDADE_N`: 1º dígito = unidade (1 = hora, 2 = dia, 3 = mês, 4 = ano), demais = valor. Ex.: `3001` = 1 mês; `2000` = 0 dias |
| Código do agravo | — | `ID_AGRAVO` = `A509` (CID-10 A50.9, sífilis congênita não especificada) |

**Ano de notificação ≠ ano do evento:** `NU_ANO` e o nome do arquivo `SIFCBR<AA>` referem-se ao **ano da notificação**. Há casos notificados anos depois do diagnóstico (ex.: notificação em 2024 com `DT_DIAG` em 2019). Para cruzar com o SINASC, usar a data de diagnóstico/nascimento, não o ano do arquivo — e checar duplicidade de um mesmo caso entre arquivos de anos diferentes.

### 6.2 Como obter os dados

Os microdados ficam no **FTP público do DATASUS** (`ftp.datasus.gov.br`), no formato **`.dbc`** (DBF compactado, formato próprio do DATASUS). Caminhos conferidos em 2026-10-20:

| Base | Caminho no FTP | Arquivos | Situação |
|---|---|---|---|
| SINASC — SP (definitivo) | `/dissemin/publicos/SINASC/1996_/Dados/DNRES/` | `DNSP1996.DBC` … `DNSP2024.dbc` | **Final** |
| SINASC — SP (preliminar) | `/dissemin/publicos/SINASC/PRELIM/DNRES/` | `DNSP2025.dbc`, `DNSP2026.dbc` | Preliminar — pode mudar |
| SINAN — Sífilis Congênita, Brasil | `/dissemin/publicos/SINAN/DADOS/PRELIM/` | `SIFCBR07.dbc` … `SIFCBR25.dbc` | **Todos preliminares** — não há `SIFCBR` na pasta `FINAIS` |
| Dicionário oficial SINASC | `/dissemin/publicos/SINASC/1996_/Doc/` | `Estrutura_SINASC_para_CD.pdf` | — |
| Documentação SINAN (TabWin) | `/dissemin/publicos/SINAN/DOCS/` | `Docs_TAB_SINAN.zip`, `POP_I_Acesso_a_Microdados_5.pdf`, `POP_II_Descompactacao_expansao_conversao_3.pdf` | — |

> ⚠️ **SINAN é preliminar em todos os anos.** Os números podem mudar entre um download e outro. **Sempre registre a data do download** e não misture arquivos de downloads diferentes sem documentar.
>
> ⚠️ **Origem dos CSVs atuais:** os `DNSP*.csv` e `SIFCBR*.csv` desta pasta foram convertidos a partir desses `.dbc`, mas a **data do download e a ferramenta de conversão não estão registradas**. Preencher quando confirmado (pendência na [seção 20](#20-roadmap-técnico--próximos-passos)).

**Passo a passo para baixar e converter**

1. Baixe os `.dbc` pelo navegador ou por um cliente FTP (ex.: FileZilla — servidor `ftp.datasus.gov.br`, acesso anônimo). O FTP do DATASUS pode bloquear acessos de fora do Brasil.
2. Converta `.dbc` → tabela com a biblioteca Python [`pyreaddbc`](https://pypi.org/project/pyreaddbc/) (alternativas: TabWin do próprio DATASUS, ou o pacote `read.dbc` no R):

   ```python
   import pyreaddbc

   df = pyreaddbc.read_dbc("SIFCBR24.dbc", encoding="iso-8859-1")
   df.to_csv("SIFCBR24.csv", index=False)   # ou df.to_parquet(...) para arquivos menores e mais rápidos
   ```

3. Coloque os arquivos na pasta de dados brutos (hoje, a raiz do projeto; na estrutura prevista, `data/raw/` — [seção 13](#13-estrutura-de-repositório-e-organização-de-arquivos)). **Nunca** versione esses arquivos no Git.

### 6.3 Como usar os dados (leitura correta em Python)

Regras que evitam os erros já encontrados na [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos):

- **Ler tudo como texto** (`dtype=str`) — preserva zeros à esquerda dos códigos (`"03"`, `"00"`); converter números e datas depois, coluna a coluna.
- **Selecionar colunas pelo nome**, nunca pela posição (`SIFCBR23` tem coluna extra; `contador` muda de posição no SINASC).
- **Usar um leitor que respeite aspas** (o `pandas` já faz isso) — há registro com quebra de linha dentro de campo de texto.
- **Datas:** SINASC em `DDMMAAAA` (`format="%d%m%Y"`), SINAN em ISO (`format="%Y-%m-%d"`).
- **Filtrar SP no SINAN** (`SG_UF == "35"`) antes de cruzar com o SINASC.

```python
from pathlib import Path
import pandas as pd

PASTA = Path(".")  # pasta onde estão os CSVs

COLS_SINAN = ["NU_ANO", "SG_UF", "ID_MN_RESI", "DT_NOTIFIC", "DT_DIAG", "ANT_IDADE",
              "ESCOLMAE", "ANT_PRE_NA", "ANTSIFIL_N", "TRA_ESQUEM", "ANT_TRATAD", "EVO_DIAG_N"]

sinan = pd.concat(
    (pd.read_csv(arq, dtype=str, usecols=lambda c: c in COLS_SINAN).assign(arquivo=arq.name)
     for arq in sorted(PASTA.glob("SIFCBR*.csv"))),
    ignore_index=True,
)
sinan["DT_DIAG"] = pd.to_datetime(sinan["DT_DIAG"], format="%Y-%m-%d", errors="coerce")
sinan_sp = sinan[sinan["SG_UF"] == "35"]          # residentes em SP — 42.262 registros (2015–2025)

COLS_SINASC = ["CODMUNRES", "DTNASC", "IDADEMAE", "ESCMAE2010", "CONSULTAS", "MESPRENAT", "KOTELCHUCK"]
sinasc_2024 = pd.read_csv(PASTA / "DNSP2024.csv", dtype=str, usecols=COLS_SINASC)
sinasc_2024["DTNASC"] = pd.to_datetime(sinasc_2024["DTNASC"], format="%d%m%Y", errors="coerce")
```

> Os `DNSP*.csv` somam ~1,2 GB. Para ler todos os anos, use só as colunas necessárias (`usecols`) ou converta uma vez para Parquet. Contagens de referência para conferir a leitura estão na [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos).

## 7. Dicionário de dados — SINASC (DNSP)

61 colunas por registro (nascimento). Cabeçalho identificado nos arquivos `DNSP*.csv` (validado em todos os anos de 2015 a 2024; ver diferença de posição da coluna `CONTADOR` na [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos)). Abrangência: **somente mães residentes no estado de SP**.

> Os significados abaixo seguem o dicionário de dados público do SINASC/Ministério da Saúde. **Antes de usar em produção, confirme os domínios de código (ex.: valores possíveis de `ESTCIVMAE`) contra o dicionário oficial vigente para o ano de referência**, pois alguns domínios mudaram de codificação ao longo dos anos (ex.: `ESCMAE`, em faixas de anos de estudo, vs. `ESCMAE2010`, que segue a classificação por nível/série de escolaridade adotada no novo formulário da DN a partir de 2010).

| Campo | Descrição | Observação |
|---|---|---|
| `ORIGEM` | Origem do registro no sistema | Administrativo |
| `CODESTAB` | Código do estabelecimento de saúde onde ocorreu o nascimento | Chave para cruzar com CNES |
| `CODMUNNASC` | Código do município de ocorrência do nascimento (IBGE) | Geográfico |
| `LOCNASC` | Local do nascimento (hospital, domicílio, outros) | Categórica |
| `IDADEMAE` | Idade da mãe em anos completos | **Variável candidata a feature** |
| `ESTCIVMAE` | Estado civil da mãe | Categórica |
| `ESCMAE` | Escolaridade da mãe (classificação clássica, anos de estudo) | **Variável candidata a feature** |
| `CODOCUPMAE` | Código da ocupação da mãe (CBO) | Alta cardinalidade |
| `QTDFILVIVO` | Número de filhos vivos | Numérica |
| `QTDFILMORT` | Número de filhos mortos | Numérica |
| `CODMUNRES` | Código do município de residência da mãe (IBGE) | **Chave geográfica de integração** |
| `GESTACAO` | Duração da gestação (faixas em semanas) | **Variável candidata a feature** |
| `GRAVIDEZ` | Tipo de gravidez (única, dupla, tripla ou mais) | Categórica |
| `PARTO` | Tipo de parto (vaginal, cesáreo) | Categórica |
| `CONSULTAS` | Número de consultas de pré-natal (faixa) | **Variável-chave — proxy de qualidade do pré-natal** |
| `DTNASC` | Data de nascimento | Temporal |
| `HORANASC` | Hora de nascimento | Temporal |
| `SEXO` | Sexo do recém-nascido | Categórica |
| `APGAR1` | Índice de Apgar no 1º minuto | Numérica (0–10) |
| `APGAR5` | Índice de Apgar no 5º minuto | Numérica (0–10) |
| `RACACOR` | Raça/cor do recém-nascido | Categórica |
| `PESO` | Peso ao nascer em gramas | **Variável candidata a feature / possível desfecho auxiliar** |
| `IDANOMAL` | Indicador de anomalia identificada | Binária/categórica |
| `DTCADASTRO` | Data de cadastro do registro no sistema | Administrativo |
| `CODANOMAL` | Código CID-10 da anomalia (quando houver) | Alta cardinalidade |
| `NUMEROLOTE` | Número do lote de processamento | Administrativo |
| `VERSAOSIST` | Versão do sistema de captura | Administrativo |
| `DTRECEBIM` | Data de recebimento do registro | Administrativo |
| `DIFDATA` | Diferença entre datas (controle de qualidade) | Administrativo |
| `DTRECORIGA` | Data de recebimento original | Administrativo |
| `NATURALMAE` | Naturalidade da mãe (país/UF) | Categórica |
| `CODMUNNATU` | Código do município de naturalidade da mãe | Geográfico |
| `CODUFNATU` | Código da UF de naturalidade da mãe | Geográfico |
| `ESCMAE2010` | Escolaridade da mãe (classificação pós-2010) | **Preferir esta sobre `ESCMAE` em dados recentes** |
| `SERIESCMAE` | Série/ano escolar da mãe | Categórica |
| `DTNASCMAE` | Data de nascimento da mãe | Permite calcular idade com mais precisão que `IDADEMAE` |
| `RACACORMAE` | Raça/cor da mãe | **Variável candidata a feature** |
| `QTDGESTANT` | Número de gestações anteriores | Numérica |
| `QTDPARTNOR` | Número de partos normais anteriores | Numérica |
| `QTDPARTCES` | Número de partos cesáreos anteriores | Numérica |
| `IDADEPAI` | Idade do pai | Alta taxa de ausência esperada |
| `DTULTMENST` | Data da última menstruação | Temporal |
| `SEMAGESTAC` | Semanas de gestação (numérico) | **Mais granular que `GESTACAO`** |
| `TPMETESTIM` | Método de estimativa da idade gestacional | Categórica |
| `CONSPRENAT` | Número de consultas de pré-natal (numérico) | **Mais granular que `CONSULTAS`** |
| `MESPRENAT` | Mês de início do pré-natal | **Variável-chave — proxy de início precoce do pré-natal** |
| `TPAPRESENT` | Tipo de apresentação fetal no parto | Categórica |
| `STTRABPART` | Indicador de trabalho de parto induzido | Binária |
| `STCESPARTO` | Indicador de cesárea antes do trabalho de parto | Binária |
| `TPNASCASSI` | Tipo de profissional que assistiu ao parto | Categórica |
| `TPFUNCRESP` | Tipo de função do responsável pela declaração | Administrativo |
| `TPDOCRESP` | Tipo de documento do responsável | Administrativo |
| `DTDECLARAC` | Data de emissão da declaração de nascido vivo | Administrativo |
| `ESCMAEAGR1` | Escolaridade da mãe agregada (faixa simplificada) | Categórica |
| `STDNEPIDEM` | Indicador epidemiológico da DN | Administrativo |
| `STDNNOVA` | Indicador de nova DN (retificação) | Administrativo |
| `CODPAISRES` | Código do país de residência da mãe | Geográfico |
| `TPROBSON` | Classificação de Robson do parto (grupo 1–10) | **Relevante para análise obstétrica** |
| `PARIDADE` | Paridade da mãe (primípara/multípara) | Categórica |
| `KOTELCHUCK` | Índice de Kotelchuck (adequação do pré-natal) | **Variável-chave — índice validado internacionalmente para adequação do pré-natal** |
| `CONTADOR` | Identificador sequencial do registro no arquivo | Não é identificador de paciente |

### 7.1 Variáveis mais promissoras para o modelo (SINASC)

Com base no objetivo do projeto (fatores de risco assistenciais/sociodemográficos), as variáveis com maior valor preditivo esperado, segundo a literatura epidemiológica de sífilis congênita, são: `CONSULTAS`/`CONSPRENAT`, `MESPRENAT`, `KOTELCHUCK`, `ESCMAE2010`, `IDADEMAE`, `RACACORMAE`, `ESTCIVMAE`, `CODMUNRES` (como proxy de contexto socioeconômico regional) e `GESTACAO`/`SEMAGESTAC`.

## 8. Dicionário de dados — SINAN Sífilis Congênita (SIFCBR)

64 colunas por registro (notificação). Cabeçalho idêntico em todos os arquivos `SIFCBR*.csv` de 2015 a 2025, **exceto `SIFCBR23.csv`**, que tem 65 colunas por conta da coluna extra `DT_NASC` (ver [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos)). Abrangência: **Brasil inteiro**. Este layout é o padrão de ficha de notificação/investigação de sífilis congênita do SINAN NET/SINAN Online.

| Campo | Descrição | Observação |
|---|---|---|
| `TP_NOT` | Tipo de notificação (individual/agregada) | Administrativo |
| `SEM_NOT` | Semana epidemiológica da notificação | Temporal |
| `ID_AGRAVO` | Código CID-10 do agravo (valor encontrado nos arquivos: `A509` — A50.9, sífilis congênita não especificada) | Filtro de sanidade dos dados |
| `DT_NOTIFIC` | Data da notificação | Temporal |
| `NU_ANO` | Ano da notificação | Temporal |
| `SG_UF_NOT` | UF de notificação | Geográfico |
| `ID_MUNICIP` | Município de notificação (IBGE) | Geográfico |
| `ID_REGIONA` | Regional de saúde de notificação | Geográfico |
| `DT_DIAG` | Data do diagnóstico | Temporal — **relevante para calcular atraso notificação-diagnóstico** |
| `SEM_DIAG` | Semana epidemiológica do diagnóstico | Temporal |
| `NU_IDADE_N` | Idade do caso notificado (recém-nascido), codificada: 1º dígito = unidade (1 hora, 2 dia, 3 mês, 4 ano), demais = valor | **Desfecho relacionado à criança** |
| `CS_SEXO` | Sexo do caso | Categórica |
| `CS_GESTANT` | Idade gestacional da mãe à época (quando aplicável) | Categórica |
| `CS_RACA` | Raça/cor do caso | Categórica |
| `CS_ESCOL_N` | Escolaridade | Categórica |
| `SG_UF` | UF de residência | Geográfico |
| `ID_MN_RESI` | Município de residência (IBGE) | **Chave geográfica de integração com SINASC** |
| `ID_RG_RESI` | Regional de saúde de residência | Geográfico |
| `ID_PAIS` | País de residência | Geográfico |
| `ANT_IDADE` | Idade materna (antecedentes) | **Variável candidata a feature** |
| `ANT_RACA` | Raça/cor da mãe (antecedentes) | Categórica |
| `ID_OCUPA_N` | Ocupação | Alta cardinalidade |
| `ESCOLMAE` | Escolaridade da mãe | **Variável candidata a feature** |
| `ANT_PRE_NA` | Realizou pré-natal? | **Variável-chave** |
| `UF_PRE_NAT` | UF onde realizou o pré-natal | Geográfico |
| `MUN_PRE_NA` | Município onde realizou o pré-natal | Geográfico |
| `ANTSIFIL_N` | Momento do diagnóstico da sífilis materna (1 = durante o pré-natal, 2 = no parto/curetagem, 3 = após o parto, 4 = não realizado, 9 = ignorado) | Categórica — **relevante para avaliar oportunidade do diagnóstico** |
| `LAB_PARTO` | Resultado de teste laboratorial no momento do parto | Clínico |
| `LAB_TITU_2` | Titulação do teste não treponêmico | Clínico |
| `LAB_DT3` | Data de exame laboratorial | Temporal |
| `LAB_CONF` | Confirmação laboratorial do caso | **Variável de definição de caso** |
| `TRA_ESQUEM` | Esquema de tratamento realizado na mãe | **Variável-chave — adequação do tratamento** |
| `TRA_DT` | Data de início do tratamento | Temporal |
| `ANT_TRATAD` | Parceiro foi tratado? | Categórica |
| `ANT_UF_CRI` | UF de residência da criança | Geográfico |
| `ANT_MUNI_C` | Município de residência da criança | Geográfico |
| `LABC_SANGU` | Exame de sangue da criança realizado? | Clínico |
| `LABC_TIT_1` | Titulação do exame da criança (1) | Clínico |
| `LABC_DT_1` | Data do exame (1) | Temporal |
| `LABC_IGG` | Resultado IgG | Clínico |
| `LABC_DT` | Data do exame IgG | Temporal |
| `LABC_LIQUO` | Exame de líquor realizado? | Clínico |
| `LABC_TIT_2` | Titulação do exame (2) | Clínico |
| `LABC_DT_2` | Data do exame (2) | Temporal |
| `LABC_TITUL` | Titulação consolidada | Clínico |
| `LABC_EVIDE` | Evidência radiológica/clínica | Clínico |
| `LABC_LIQ_1` | Resultado da análise do líquor | Clínico |
| `TRA_DIAG_T` | Tipo de tratamento diagnóstico da criança | Clínico |
| `TRA_ESQU_1` | Esquema de tratamento da criança | Clínico |
| `DS_ESQUEMA` | Descrição textual do esquema (campo livre) | **Texto livre — exige NLP ou descarte** |
| `EVOLUCAO` | Evolução do caso (cura, óbito, etc.) | **Possível variável-alvo secundária (desfecho)** |
| `DT_OBITO` | Data do óbito (se aplicável) | Temporal |
| `EVO_DIAG_N` | Classificação final do diagnóstico | **Variável de definição de caso confirmado** |
| `TRA_DIAG_C` | Diagnóstico de tratamento da criança | Clínico |
| `CLI_ICTERI` | Icterícia (sinal clínico) | Binária |
| `CLI_RINITE` | Rinite sifilítica (sinal clínico) | Binária |
| `CLI_ANEMIA` | Anemia (sinal clínico) | Binária |
| `CLI_ESPLEN` | Esplenomegalia (sinal clínico) | Binária |
| `HEPATO` | Hepatomegalia (sinal clínico) | Binária |
| `CLI_OSTEO` | Alterações ósseas (sinal clínico) | Binária |
| `LESOES` | Lesões cutâneas (sinal clínico) | Binária |
| `CLI_OUTRO` | Outros sinais clínicos | Binária/texto |
| `SIN_OUTR_E` | Especificação de outros sinais (texto livre) | Texto livre |
| `CLI_PSEUDO` | Pseudoparalisia de membros (sinal clínico) | Binária |

### 8.1 Observações importantes sobre o SIFCBR

- Os campos `CLI_*` / `LESOES` / `HEPATO` / `CLI_PSEUDO` formam o **quadro clínico do recém-nascido** e são potenciais variáveis de caracterização de gravidade, mas **não devem ser usados como features de entrada** se o objetivo é prever risco *antes* do diagnóstico — usá-los geraria vazamento de dado (data leakage), pois só existem quando o caso já foi confirmado.
- `EVO_DIAG_N` e `LAB_CONF` são os campos mais prováveis para **definir o rótulo/target** de "caso confirmado de sífilis congênita" ao construir o dataset supervisionado.
- **Viés de seleção pela definição de caso:** pelos critérios do Ministério da Saúde, uma criança é notificada como sífilis congênita quando a mãe com sífilis **não foi tratada ou foi tratada de forma inadequada**. Por isso, entre os casos notificados, a proporção de mães com tratamento adequado (`TRA_ESQUEM = 1`) é baixa **por construção** (~3–6% na base) — esse número **não** mede a cobertura de tratamento da população de gestantes com sífilis e não deve ser apresentado como achado. Para medir falha de tratamento é preciso o denominador de **sífilis em gestante** (SINAN, agravo próprio, fora do escopo atual). Já o tratamento do parceiro (`ANT_TRATAD`) deixou de fazer parte do critério de adequação em 2017 e pode ser analisado como característica dos casos.
- Muitos campos são de preenchimento condicional (dependem de resposta a uma pergunta anterior na ficha) — espera-se **alta taxa de valores ausentes estruturais** (não aleatórios), o que deve ser tratado de forma distinta de ausência aleatória no pré-processamento.

## 9. Metodologia detalhada

### Etapa 0 — Revisão bibliográfica e definição de escopo (ambos)
Levantamento em Scopus, Web of Science, IEEE Xplore, Google Scholar. Saída esperada: síntese de fatores de risco já descritos na literatura + decisão formal sobre a estratégia de linkage entre SINASC e SINAN (individual vs. agregada).

### Etapa 1 — Ingestão (Eduarda)
Leitura dos arquivos CSV brutos ano a ano, validação de schema **lendo as colunas por nome, não por posição** (há diferenças reais de layout entre anos: `contador`/`CONTADOR` em posições distintas no SINASC 2015/2017 e a coluna extra `DT_NASC` no SINAN 2023 — ver [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos)), padronização dos formatos de data (`DDMMAAAA` no SINASC vs. ISO no SINAN), preservação de zeros à esquerda nos códigos, e consolidação em um dataset único por sistema (SINASC-SP consolidado 2015–2024; SINAN-BR consolidado 2015–2025, com 2025 marcado como ano parcial).

### Etapa 2 — Limpeza e padronização (Eduarda)
- Tratamento de valores ausentes (distinguindo ausência estrutural de ausência por falha de preenchimento).
- Padronização de tipos (datas, códigos numéricos vs. categóricos).
- Remoção/flag de duplicidades.
- Padronização de domínios de código entre anos (ex.: mudanças de codificação de escolaridade).

### Etapa 3 — Integração SINASC + SINAN (Eduarda + Lucas, decisão conjunta)
Definição e implementação da estratégia de linkage (ver [seção 6](#6-fontes-de-dados)). **Pré-requisito obrigatório:** restringir o SINAN a residentes em SP (`SG_UF = 35`), já que o SINASC disponível cobre apenas SP. **Atenção:** os casos de aborto e natimorto por sífilis (`EVO_DIAG_N` 3 e 4, ~6,9% do SINAN) não têm Declaração de Nascido Vivo e, portanto, nunca serão encontrados no SINASC — decidir se saem do rótulo ou são analisados à parte (ver [6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos)). Se for optado por record linkage individual: aplicar chave composta (município de residência + data de nascimento/data de referência + faixas de idade) com técnica probabilística; se optado por abordagem ecológica: agregar ambas as bases por município × período (ex. município × ano) para construir taxas.

### Etapa 4 — Armazenamento estruturado (Eduarda)
Modelagem de um banco de dados (relacional ou analítico) com separação entre camada de dados brutos e camada de dados tratados/integrados, versionamento do schema, e disponibilização de uma interface (ex.: views, exports parametrizados) para consumo pelo pipeline de ML.

### Etapa 5 — Pré-processamento para ML (Lucas)
- Seleção de variáveis (feature selection) a partir do dicionário de dados (seções 7 e 8), excluindo campos administrativos, de alta cardinalidade sem tratamento (ex. `CODOCUPMAE`), texto livre (`DS_ESQUEMA`, `SIN_OUTR_E`) e campos que causariam vazamento de dado (ver 8.1).
- Codificação de variáveis categóricas (one-hot / ordinal, conforme o algoritmo).
- Normalização/padronização de variáveis numéricas.
- Balanceamento de classes (ex.: SMOTE, undersampling, ou class-weighting), já que casos confirmados de sífilis congênita são evento raro frente ao total de nascimentos.

### Etapa 6 — Modelagem (Lucas)
Treinamento dos algoritmos listados na [seção 11](#11-algoritmos-de-classificação-previstos), com validação cruzada (k-fold, estratificada por classe dado o desbalanceamento).

### Etapa 7 — Arquitetura adaptável por configuração externa (Lucas)
Implementação de um arquivo de configuração externo (formato sugerido: YAML ou JSON) que permita definir, sem alterar código:
- Algoritmo(s) a treinar;
- Lista de variáveis de entrada (features);
- Hiperparâmetros de cada algoritmo;
- Estratégia de balanceamento de classes;
- Estratégia de validação (ex.: número de folds).

Ver proposta de estrutura em [seção 10](#10-arquitetura-do-sistema-proposta).

### Etapa 8 — Avaliação (Lucas)
Cálculo das métricas da [seção 12](#12-métricas-de-avaliação) para cada algoritmo/configuração testada, com registro estruturado dos experimentos (idealmente um log/tabela de execução — cada linha = uma configuração testada + métricas obtidas).

### Etapa 9 — Interpretabilidade (Lucas)
Importância de variáveis (ex.: feature importance nativa de Random Forest, coeficientes padronizados da Regressão Logística, ou técnicas agnósticas como permutation importance / SHAP).

### Etapa 10 — Documentação e publicação (ambos)
Relatórios parciais e final, atualização deste documento e do README, preparação de artigo científico.

## 10. Arquitetura do sistema (proposta)

> Ainda não implementada — este é o desenho de referência para guiar a implementação, alinhado ao que os planos de trabalho descrevem como "arquitetura modular adaptável por configuração externa".

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Arquivo de configuração                     │
│               (config.yaml — algoritmo, features, hiperparâmetros)  │
└───────────────────────────────┬───────────────────────────────────--┘
                                 │ lido por
                                 ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐   ┌────────────────────┐
│  Camada de Dados   │──▶│ Pré-processamento │──▶│    Modelagem       │──▶│    Avaliação        │
│ (extração/leitura  │   │ (limpeza, encode, │   │ (treino do(s)      │   │ (métricas, relatório│
│  do banco tratado) │   │  balanceamento)    │   │  algoritmo(s)      │   │  interpretabilidade)│
└───────────────────┘   └───────────────────┘   │  definidos na cfg) │   └────────────────────┘
                                                  └───────────────────┘
```

**Princípios de design:**
- Cada camada é um módulo independente, testável isoladamente.
- Nenhuma camada deve conter valores "hardcoded" que pertençam à configuração (algoritmo, hiperparâmetro, lista de features) — tudo deve vir do arquivo de configuração externo.
- A saída de cada etapa deve ser versionável/rastreável (ex.: salvar o dataset pré-processado, o modelo treinado serializado, e o relatório de métricas de cada execução), para reprodutibilidade.

**Exemplo ilustrativo de arquivo de configuração** (formato a validar com o restante da equipe):

```yaml
experimento: "baseline_random_forest_v1"
dados:
  fonte: "banco_tratado.parquet"
  features:
    - CONSULTAS
    - MESPRENAT
    - KOTELCHUCK
    - ESCMAE2010
    - IDADEMAE
    - RACACORMAE
    - GESTACAO
  target: "caso_confirmado"
pre_processamento:
  balanceamento: "smote"
  normalizacao: "standard_scaler"
modelo:
  algoritmo: "random_forest"
  hiperparametros:
    n_estimators: 300
    max_depth: 12
    min_samples_leaf: 5
validacao:
  metodo: "stratified_kfold"
  n_folds: 5
metricas:
  - acuracia
  - precisao
  - recall
  - f1
  - roc_auc
```

## 11. Algoritmos de classificação previstos

| Algoritmo | Por que está no escopo | Ponto de atenção |
|---|---|---|
| Regressão Logística | Baseline interpretável, coeficientes diretamente relacionáveis a fatores de risco | Sensível a colinearidade entre variáveis |
| Random Forest | Bom desempenho em dados tabulares heterogêneos, robusto a outliers, fornece importância de variáveis nativa | Cuidado com overfitting em alta profundidade |
| Support Vector Machine (SVM) | Bom em espaços de alta dimensão após codificação categórica | Custo computacional em bases grandes (SINASC é grande) |
| Redes Neurais Artificiais (RNA) | Capacidade de capturar relações não lineares complexas | Exige mais dado e tuning; menor interpretabilidade nativa |

## 12. Métricas de avaliação

Dado que o problema é uma **classificação binária desbalanceada** (caso confirmado vs. não caso), a acurácia isolada é enganosa. As métricas previstas nos planos de trabalho são:

| Métrica | O que mede | Por que importa aqui |
|---|---|---|
| Acurácia | Proporção geral de acertos | Contextual — pode ser alta mesmo com modelo inútil, dado o desbalanceamento |
| Precisão (precision) | Dos casos previstos como positivos, quantos eram de fato positivos | Relevante para evitar excesso de falsos alertas |
| Recall (sensibilidade) | Dos casos positivos reais, quantos o modelo identificou | **Crítica em saúde pública** — deixar de identificar um caso de risco é mais grave que um falso alarme |
| F1-score | Média harmônica entre precisão e recall | Métrica-resumo para comparar modelos sob desbalanceamento |
| AUC-ROC | Capacidade de discriminação do modelo entre classes, em todos os limiares | Permite comparar modelos independente do ponto de corte escolhido |

## 13. Estrutura de repositório e organização de arquivos

**Estado atual:**

```
Sifilis congenita/
├── README.md
├── DOCUMENTACAO_TECNICA.md      # este arquivo (fonte oficial da documentação)
├── Documentacao_Tecnica_Sifilis_Congenita.docx / .pdf   # versões exportadas deste .md (regenerar a cada revisão)
├── Artigo_Cientifico_Modelo_Preditivo_Sifilis_Congenita.pdf  # artigo metodológico (não versionado — *.pdf no .gitignore)
├── requirements.txt             # dependências Python (ver seção 13.2)
├── ROTEIRO_POWER_BI.md          # modelo do painel no Power BI e roteiro das páginas
├── Projeto_Sifilis_BI.pbip      # abre o BI no Power BI Desktop (Projeto do Power BI)
├── Projeto_Sifilis_BI.SemanticModel/  # modelo do BI em texto (TMDL) — versionável
├── Projeto_Sifilis_BI.Report/         # páginas/visuais do BI — versionável
├── .gitignore
├── DNSP2015.csv ... DNSP2024.csv        # SINASC-SP bruto, 10 arquivos (não versionado)
├── SIFCBR15.csv ... SIFCBR25.csv        # SINAN-BR bruto, 11 arquivos, 2025 parcial (não versionado)
├── Lucas_-_Plano_de_Trabalho_...pdf     # não versionado (dado pessoal)
├── Plano_de_trabalho_Eduarda_Oliveira.pdf  # não versionado (dado pessoal)
└── Microsoft.Services.Store.winmd       # ⚠ arquivo do Windows sem relação com o projeto — remover (não está no .gitignore)
```

> Nenhum código (`.py`/notebook) foi implementado até esta revisão.

**Estrutura prevista quando a implementação começar** (sugestão, a validar com a Eduarda):

```
Sifilis congenita/
├── README.md
├── DOCUMENTACAO_TECNICA.md
├── .gitignore
├── config/
│   └── experimentos/*.yaml        # arquivos de configuração externa (Lucas)
├── data/
│   ├── raw/                       # CSVs originais (ignorado no git)
│   ├── interim/                   # dados parcialmente tratados
│   └── processed/                 # dataset final pronto para modelagem
├── src/
│   ├── pipeline/                  # ETL/ELT (Eduarda)
│   │   ├── extract.py
│   │   ├── transform.py
│   │   └── load.py
│   ├── modeling/                  # treino/avaliação (Lucas)
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── interpret.py
│   └── shared/                    # utilitários comuns (schemas, logging)
├── notebooks/                     # análises exploratórias
├── reports/                       # relatórios parciais/final, figuras
├── tests/                         # testes automatizados do pipeline e da modelagem
└── requirements.txt / environment.yml
```

### 13.1 Ferramentas do projeto

| Ferramenta | Uso no projeto | Situação |
|---|---|---|
| **Python 3.12** | Linguagem do pipeline e da modelagem | Definido |
| `pandas`, `numpy` | Leitura e tratamento dos dados | Definido (`requirements.txt`) |
| `scikit-learn` | Algoritmos de classificação, validação cruzada, métricas | Definido |
| `imbalanced-learn` | Balanceamento de classes (SMOTE, undersampling) | Definido |
| `matplotlib`, `seaborn` | Gráficos da análise exploratória e dos relatórios | Definido |
| `pyyaml` | Leitura do arquivo de configuração externo (`config/*.yaml`) | Definido |
| `jupyter` | Notebooks de análise exploratória | Definido |
| `pyreaddbc` | Conversão dos `.dbc` do DATASUS ([seção 6.2](#62-como-obter-os-dados)) | Definido |
| `pyarrow` | Gravar/ler Parquet (dados intermediários menores e mais rápidos) | Definido |
| **PyCharm** | IDE do projeto (configuração em `.idea/`, fora do Git) | Em uso |
| **Power BI Desktop** | Painel exploratório dos dados ([ROTEIRO_POWER_BI.md](ROTEIRO_POWER_BI.md)) | Em uso |
| **Git + GitHub** | Versionamento ([seção 14](#14-controle-de-versão-e-fluxo-de-trabalho-git)) | Em uso |
| Banco de dados tratado | Armazenamento da base integrada (frente da Eduarda) | **A definir** |

### 13.2 Configurando o ambiente Python

Passo a passo para quem vai rodar o projeto pela primeira vez (Windows):

1. **Instalar o Python 3.12** pelo [python.org](https://www.python.org/downloads/) — marcar **"Add python.exe to PATH"** na instalação. Conferir no terminal:

   ```bash
   python --version
   ```

   > No Windows, se `python` abrir a Microsoft Store ou der erro, o Python não está instalado de verdade — é só o atalho da Store. Desative em *Configurações → Aplicativos → Aliases de execução de aplicativo*.

2. **Criar o ambiente virtual** na pasta do projeto (a pasta `.venv/` já está no `.gitignore`):

   ```bash
   python -m venv .venv
   ```

3. **Ativar o ambiente** (PowerShell):

   ```bash
   .venv\Scripts\Activate.ps1
   ```

   > Se o PowerShell bloquear o script, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

4. **Instalar as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

5. **No PyCharm:** *Settings → Project → Python Interpreter → Add Interpreter → Existing* → selecionar `.venv\Scripts\python.exe`. Os notebooks Jupyter rodam direto no PyCharm com esse interpretador.

6. **Testar a leitura dos dados** com o exemplo da [seção 6.3](#63-como-usar-os-dados-leitura-correta-em-python) e conferir as contagens com a [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos).

> **Reprodutibilidade:** o `requirements.txt` ainda **não fixa versões**. Assim que o ambiente estiver funcionando, rodar `pip freeze > requirements.txt` e versionar o resultado, para todos usarem as mesmas versões (pendência na [seção 20](#20-roadmap-técnico--próximos-passos)).

## 14. Controle de versão e fluxo de trabalho Git

- **Repositório remoto:** `https://github.com/EduardaRab/S-filis-Cong-nita-ML` (branch principal: `main`).
- **`.gitignore` atual exclui:** todos os `*.csv` (dados brutos, grandes demais e não devem ser versionados) e todos os `*.pdf` (planos de trabalho, contêm CPF/RG/endereço/telefone).
- **Recomendação de fluxo:** usar branches por funcionalidade (ex.: `feature/pipeline-etl`, `feature/modelo-baseline`) e abrir Pull Request para `main`, já que o repositório é compartilhado entre os dois alunos — evita sobrescrever trabalho um do outro, o que já ocorreu uma vez no histórico inicial (commit automático do GitHub precisou ser mesclado manualmente).
- **Dados grandes:** se em algum momento for necessário versionar uma amostra de dados ou o dataset processado, considerar Git LFS (Large File Storage) em vez de commitar diretamente, ou hospedar em um storage externo (ex.: Google Drive institucional) referenciado no README.

## 15. Considerações éticas, legais e de privacidade

- Os dados do SINASC e do SINAN utilizados são **públicos e agregados/anonimizados** pelo DATASUS — não contêm nome, CPF ou outro identificador direto de paciente.
- Ainda assim, por se tratar de **dados de saúde** (categoria sensível segundo a LGPD, Lei nº 13.709/2018), o tratamento deve seguir boas práticas de minimização (usar apenas as variáveis necessárias ao objetivo do estudo) e de segurança (não republicar os microdados brutos fora dos canais oficiais do DATASUS).
- **Os planos de trabalho em PDF contêm dados pessoais diretos dos dois alunos** (CPF, RG, endereço residencial, telefone) — por isso foram excluídos do controle de versão via `.gitignore` e não devem ser anexados a nenhum relatório público, artigo ou repositório aberto.
- Qualquer publicação científica decorrente do projeto deve reportar resultados de forma agregada (nunca a nível de caso individual identificável).

## 16. Cronograma detalhado

Os cronogramas dos dois planos de trabalho são **idênticos em periodização**, refletindo que as duas frentes avançam em paralelo e se retroalimentam:

| Período | Frente de Engenharia de Dados (Eduarda) | Frente de Modelagem (Lucas) |
|---|---|---|
| **Ago–Out/2026** | Levantamento bibliográfico; estudo de ETL/ELT, modelagem de dados e qualidade da informação; compreensão das bases DATASUS/SINAN; planejamento da arquitetura do pipeline. | Levantamento bibliográfico; estudo de modelagem preditiva e análise de dados; compreensão das bases públicas; planejamento da arquitetura do sistema. |
| **Nov/2026–Jan/2027** | Ingestão e tratamento dos dados (limpeza, valores ausentes, padronização); implementação inicial do pipeline ETL; análises exploratórias de qualidade dos dados. | Pré-processamento dos dados; análise exploratória para identificação de padrões; implementação inicial do pipeline e dos primeiros modelos; testes iniciais de treinamento/validação. |
| **Fev–Abr/2027** | Automação e melhoria do pipeline; modelagem e implementação do banco de dados estruturado; validações e regras de qualidade; disponibilização da base para consumo analítico; **apresentação de resultados parciais em evento de IC**. | Ajuste de parâmetros e comparação entre algoritmos; implementação da arquitetura adaptável por configuração externa; testes robustos de desempenho; **apresentação de resultados parciais em evento de IC**. |
| **Mai–Jul/2027** | Finalização do pipeline e da estrutura do banco de dados; testes finais de consistência/desempenho/reprodutibilidade; relatório final; preparação de artigo científico. | Finalização do modelo preditivo; validação do sistema; ajustes finais na arquitetura; relatório final; preparação de artigo científico. |

## 17. Produção científica esperada

- Relatórios parciais e relatório final de IC (um conjunto por aluno, conforme exigência do edital).
- Apresentação de resultados parciais em evento de iniciação científica da USF (Fev–Abr/2027).
- **Artigo metodológico já redigido:** *"Modelo preditivo de sífilis congênita com arquitetura adaptável por configuração externa: uma proposta metodológica integrando engenharia de dados, aprendizado de máquina e vigilância epidemiológica"* (`Artigo_Cientifico_Modelo_Preditivo_Sifilis_Congenita.pdf`, 10 p.). Descreve o delineamento, sem resultados empíricos. Antes de submeter, alinhar com os achados da [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos) (abrangência SP × Brasil) e corrigir a referência KOURENTZES.
- Preparação de artigo científico com resultados empíricos para submissão em periódico ou congresso da área (ao final do projeto, Mai–Jul/2027).
- Potencial de continuidade: novas aplicações de engenharia de dados/ML em saúde pública a partir da base construída.

## 18. Glossário

| Termo/Sigla | Significado |
|---|---|
| **DATASUS** | Departamento de Informática do SUS — órgão do Ministério da Saúde responsável por sistemas de informação em saúde no Brasil |
| **SINASC** | Sistema de Informações sobre Nascidos Vivos |
| **SINAN** | Sistema de Informação de Agravos de Notificação |
| **DN** | Declaração de Nascido Vivo (documento/registro do SINASC) |
| **CID-10** | Classificação Internacional de Doenças, 10ª revisão (ex.: A50 = sífilis congênita) |
| **ETL** | Extract, Transform, Load — extração, transformação e carregamento de dados |
| **ELT** | Extract, Load, Transform — variante do ETL em que a transformação ocorre após o carregamento |
| **Record linkage** | Técnica de relacionar registros de bases distintas que se referem à mesma entidade, sem identificador único comum |
| **Data leakage (vazamento de dado)** | Quando uma variável usada como entrada do modelo carrega informação que só existiria após o desfecho ser conhecido, inflando artificialmente o desempenho |
| **SMOTE** | Synthetic Minority Oversampling Technique — técnica de balanceamento de classes por geração sintética de exemplos da classe minoritária |
| **F1-score** | Média harmônica entre precisão e recall |
| **AUC-ROC** | Área sob a curva ROC (Receiver Operating Characteristic) — mede a capacidade de discriminação de um classificador |
| **Índice de Kotelchuck** | Índice validado que mede a adequação do início e da quantidade de consultas de pré-natal |
| **Classificação de Robson** | Sistema que classifica partos em 10 grupos, usado para análise de indicações de cesárea |
| **LGPD** | Lei Geral de Proteção de Dados (Lei nº 13.709/2018) |
| **IC** | Iniciação Científica |

## 19. Referências bibliográficas

- BRASIL. Ministério da Saúde. *Protocolo Clínico e Diretrizes Terapêuticas para Atenção Integral às Pessoas com Infecções Sexualmente Transmissíveis (IST)*. Brasília: Ministério da Saúde, 2022. Disponível em: https://www.gov.br/aids/pt-br/centrais-de-conteudo/pcdts/2022/ist
- WORLD HEALTH ORGANIZATION (WHO). *Global progress report on HIV, viral hepatitis and sexually transmitted infections*. Geneva: WHO, 2021. Disponível em: https://www.who.int/publications/i/item/9789240027077
- KOURENTZES, N.; BARROW, D. K.; CRONE, S. F. Neural network ensemble operators for time series forecasting. *Expert Systems with Applications*, v. 41, n. 9, p. 4235–4244, 2014. https://doi.org/10.1016/j.eswa.2013.12.011
  > Corrigido na v1.1: a versão anterior citava ano 2019 e um DOI de outro artigo. O mesmo erro (ano 2019) está no artigo científico — corrigir lá também.
- OBERMEYER, Z.; EMANUEL, E. J. Predicting the future — big data, machine learning, and clinical medicine. *The New England Journal of Medicine*, v. 375, n. 13, p. 1216–1219, 2016. https://doi.org/10.1056/NEJMp1606181
- SOMMERVILLE, I. *Engenharia de Software*. 10. ed. São Paulo: Pearson, 2019.
- ALURA. *O que é engenharia de dados*. 2023. Disponível em: https://www.alura.com.br/artigos/engenharia-dados
- ACCURATE. *Engenharia de dados e sua importância para BI e BA*. 2024. Disponível em: https://blog.accurate.com.br/engenharia-de-dados/

## 20. Roadmap técnico / próximos passos

### 20.1 Decisões já tomadas

| # | Decisão | Origem / data | Onde está detalhada |
|---|---|---|---|
| D1 | Modelo **apoia a vigilância**, não faz diagnóstico individual | Planos de trabalho (abr/2026) | [2](#2-problema-e-motivação), [4.3](#43-escopo) |
| D2 | Fontes: SINASC + SINAN Sífilis Congênita (DATASUS), 2015–2025 | Planos de trabalho; arquivos baixados (set/2026) | [6](#6-fontes-de-dados) |
| D3 | Linguagem **Python** com pandas, scikit-learn, imbalanced-learn, pyyaml etc. | `requirements.txt` (out/2026) | [13.1](#131-ferramentas-do-projeto) |
| D4 | Configuração externa em **YAML** (algoritmo, features, hiperparâmetros, balanceamento, validação) | Planos de trabalho; artigo | [9 — Etapa 7](#etapa-7--arquitetura-adaptável-por-configuração-externa-lucas), [10](#10-arquitetura-do-sistema-proposta) |
| D5 | Algoritmos a comparar: Regressão Logística (baseline), Random Forest, SVM, Redes Neurais | Planos de trabalho | [11](#11-algoritmos-de-classificação-previstos) |
| D6 | Validação cruzada **k-fold estratificada**; métricas acurácia, precisão, **recall (prioritária)**, F1, AUC-ROC | Planos de trabalho; artigo | [12](#12-métricas-de-avaliação) |
| D7 | Campos clínicos do recém-nascido (`CLI_*` etc.) **não** entram como features — evitam vazamento de dado | v1.0 da doc | [8.1](#81-observações-importantes-sobre-o-sifcbr) |
| D8 | Dados brutos (`*.csv`) e PDFs com dados pessoais **fora do Git** | `.gitignore` (set/2026) | [14](#14-controle-de-versão-e-fluxo-de-trabalho-git), [15](#15-considerações-éticas-legais-e-de-privacidade) |
| D9 | Ler os CSVs **por nome de coluna e como texto**; datas convertidas por base | v1.1 da doc (out/2026) | [6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos), [6.3](#63-como-usar-os-dados-leitura-correta-em-python) |
| D10 | Para cruzar com o SINASC, usar só casos do SINAN **residentes em SP** | v1.1 da doc (out/2026) | [6](#6-fontes-de-dados) |
| D11 | **Power BI Desktop** como ferramenta de análise exploratória/painel | 2026-10-14 | [ROTEIRO_POWER_BI.md](ROTEIRO_POWER_BI.md) |
| D12 | Esta documentação (`DOCUMENTACAO_TECNICA.md`) é a **fonte oficial**; README resume; `.docx`/`.pdf` são exportações | v1.1 da doc | [13](#13-estrutura-de-repositório-e-organização-de-arquivos) |
| D13 | Branches por funcionalidade + Pull Request para `main` | v1.0 da doc | [14](#14-controle-de-versão-e-fluxo-de-trabalho-git) |

> Nova decisão? Acrescente uma linha aqui (com data) e, se ela fechar um item abaixo, marque o item como feito.

### 20.2 Próximos passos

- [x] ~~Confirmar/obter o arquivo `SIFCBR22.csv` (2022)~~ — o arquivo está na pasta (26.515 registros); a "lacuna" da v1.0 era um erro de levantamento.
- [x] Levantar volume, abrangência e diferenças de schema reais dos arquivos — feito na v1.1 ([seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos)).
- [ ] **Decidir o recorte geográfico do estudo:** trabalhar só com SP (filtrando o SINAN para `SG_UF = 35`) ou baixar o SINASC das demais UFs para escala nacional.
- [ ] Decidir e documentar a estratégia de integração SINASC × SINAN (linkage individual vs. agregação ecológica).
- [ ] Decidir o tratamento de 2025 (ano parcial). O SINASC-SP 2025 já existe como preliminar no FTP (`DNSP2025.dbc` — [seção 6.2](#62-como-obter-os-dados)).
- [ ] Registrar a data de download e a ferramenta usada para converter os `.dbc` atuais em CSV (o SINAN é preliminar e muda entre downloads).
- [x] Documentar como obter os dados, como lê-los e como configurar o ambiente Python — feito na v1.2 ([6.2](#62-como-obter-os-dados), [6.3](#63-como-usar-os-dados-leitura-correta-em-python), [13.2](#132-configurando-o-ambiente-python)).
- [ ] Verificar duplicidade de casos entre arquivos SINAN de anos diferentes (notificação tardia).
- [ ] Decidir o tratamento dos 17.784 casos de aborto/natimorto por sífilis (sem registro no SINASC) na definição do rótulo do modelo.
- [ ] Validar os domínios de código de cada campo contra o dicionário oficial vigente do DATASUS/SINAN para os anos 2015–2025.
- [x] Stack técnica inicial: Python com `pandas`, `numpy`, `scikit-learn`, `imbalanced-learn`, `matplotlib`, `seaborn`, `pyyaml`, `jupyter` (ver `requirements.txt`).
- [ ] Fixar versões no `requirements.txt` (hoje sem versão — compromete a reprodutibilidade) e definir o formato do banco de dados tratado.
- [ ] Remover `Microsoft.Services.Store.winmd` da pasta do projeto.
- [ ] Corrigir a referência KOURENTZES (ano 2014) no artigo científico.
- [ ] Implementar o pipeline ETL/ELT inicial (frente da Eduarda).
- [ ] Implementar o primeiro modelo baseline (Regressão Logística) para validar o pipeline de ponta a ponta antes de partir para modelos mais complexos.
- [ ] Especificar o schema definitivo do arquivo de configuração externo (formato YAML/JSON, campos obrigatórios).
- [ ] Definir política de armazenamento de dados grandes fora do Git (Drive institucional, Git LFS, ou storage próprio da USF).

## 21. Histórico de revisões

| Versão | Data | Alterações |
|---|---|---|
| 1.0 | 2026-09-15 | Versão inicial. |
| 1.1 | 2026-10-14 | Revisão contra os arquivos reais: abrangência corrigida (SINASC = só SP; SINAN = Brasil); removida a falsa "lacuna de 2022" (`SIFCBR22.csv` existe); contagem de colunas corrigida (61 SINASC / 64 SINAN, 65 no SINAN 2023); nova [seção 6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos) com volume por ano, diferenças de schema e formatos; `ID_AGRAVO`, `NU_IDADE_N` e `ESCMAE2010` corrigidos; referência KOURENTZES corrigida (2014); estrutura de repositório, produção científica e roadmap atualizados. |
| 1.2 | 2026-10-20 | Nova [4.3 Escopo](#43-escopo) (dentro/fora/em aberto); nova [6.2](#62-como-obter-os-dados) com caminhos do FTP do DATASUS conferidos (SINAN Sífilis Congênita é **todo preliminar**; SINASC-SP 2025 disponível como preliminar) e conversão `.dbc`; nova [6.3](#63-como-usar-os-dados-leitura-correta-em-python) com regras e exemplo de leitura em Python; total do SINAN corrigido para 258.372 (registro com quebra de linha em `SIFCBR20`); novas [13.1 Ferramentas](#131-ferramentas-do-projeto) e [13.2 Ambiente Python](#132-configurando-o-ambiente-python); `pyreaddbc` e `pyarrow` adicionados ao `requirements.txt`; nova 20.1 com as decisões já tomadas; roadmap reorganizado. |
| 1.3 | 2026-10-20 | Revisão de gestão: descrição de `ANTSIFIL_N` corrigida (é o **momento do diagnóstico da sífilis materna**, não "gestação anterior"); [6.1](#61-perfil-real-dos-dados-verificado-nos-arquivos) ganhou a distribuição do diagnóstico final e o alerta de que **17.784 casos de aborto/natimorto não existem no SINASC**; [8.1](#81-observações-importantes-sobre-o-sifcbr) ganhou o alerta de **viés pela definição de caso** (tratamento materno adequado é baixo entre casos por construção); Etapa 3 e roadmap atualizados; `.docx`/`.pdf` regenerados a partir desta versão; coluna RA removida da seção 1 (o documento passou a ser versionado em repositório público). |
