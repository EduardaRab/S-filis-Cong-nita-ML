# Roteiro do BI: Sífilis Congênita (Power BI)

> **Onde está o BI:** os arquivos do painel (`Projeto_Sifilis_BI.pbip` e as pastas `Projeto_Sifilis_BI.SemanticModel/` e `Projeto_Sifilis_BI.Report/`) ficam, por enquanto, na **pasta de trabalho local** do projeto, junto com os CSVs, e **ainda não estão neste repositório** (ver seção 13 da [documentação técnica](DOCUMENTACAO_TECNICA.md#13-estrutura-de-repositório-e-organização-de-arquivos)). Este roteiro descreve o modelo e as páginas para quem for abrir ou recriar o painel.

> Modelo recriado em 2026-10-20 via Power BI Modeling MCP e **salvo em disco como Projeto do Power BI (`.pbip`)**. (A primeira versão, de 2026-10-14, foi perdida porque o arquivo nunca foi salvo.)
> O MCP cria **tabelas, relações e medidas**, mas **não cria visuais**. Por isso, em 2026-10-20 **as 5 páginas da seção 2 foram geradas direto nos arquivos PBIR** (`Projeto_Sifilis_BI.Report\definition\pages\`: `visao_geral`, `sinasc_sp`, `sinan_brasil`, `qualidade`, `projeto`, com 52 visuais, incluindo a tabela da equipe na página Projeto). Elas saem com a formatação padrão do Power BI; cores, tamanhos e títulos podem ser ajustados à mão e salvos com Ctrl+S. A seção 2 continua valendo como descrição do que cada página mostra.
> Todas as contagens foram conferidas contra a seção 6.1 da [DOCUMENTACAO_TECNICA.md](DOCUMENTACAO_TECNICA.md) depois de abrir o `.pbip` no Power BI Desktop.

## 0. Como abrir o BI

1. Dê dois cliques em **`Projeto_Sifilis_BI.pbip`** (nesta pasta) ou, no Power BI Desktop, *Arquivo → Abrir* e escolha o `.pbip`.
2. Se as tabelas aparecerem vazias, clique em **Página Inicial → Atualizar** (lê os CSVs e a doc; leva alguns minutos por causa do SINASC).
3. Depois de montar visuais, **salve com Ctrl+S**: o Power BI grava tudo nos arquivos de texto do projeto e o cache de dados em `.pbi\cache.abf`.

**Arquivos do projeto:**

| Caminho | O que é | Vai para o Git? |
|---|---|---|
| `Projeto_Sifilis_BI.pbip` | Atalho que abre o projeto | Sim |
| `Projeto_Sifilis_BI.SemanticModel\definition\*.tmdl` | **O modelo** (tabelas, Power Query, relações, medidas) em texto | Sim |
| `Projeto_Sifilis_BI.Report\` | As páginas e visuais do relatório | Sim |
| `**\.pbi\cache.abf`, `**\.pbi\localSettings.json` | Cache dos dados e preferências locais | Não (está no `.gitignore`) |

- Como o modelo é texto (TMDL), mudanças em medidas e consultas aparecem no `git diff` e dá para revisar em Pull Request.
- Se mover a pasta do projeto, altere só o parâmetro **PastaProjeto** (*Transformar dados → Gerenciar parâmetros*) e clique em **Atualizar**.
- O `.pbip` exige que os CSVs estejam na pasta indicada por `PastaProjeto`. Eles não vão para o Git, então cada pessoa precisa ter os dados localmente ([seção 6.2 da doc](DOCUMENTACAO_TECNICA.md#62-como-obter-os-dados)).

## 1. O que existe no modelo

| Tabela | Conteúdo | Linhas |
|---|---|---:|
| `SINASC` | Nascidos vivos, **só mães residentes em SP**, 2015–2024, 16 colunas úteis + rótulos | 5.601.469 |
| `SINAN` | Notificações de sífilis congênita, **Brasil**, 2015–2025 (2025 parcial), 25 colunas + rótulos e campos derivados | 258.372 |
| `SINAN_Completude` | Preenchimento de **todos** os campos do SINAN por ano × UF de residência | 18.738 |
| `dAno` | 2015–2025 (filtra as 3 tabelas acima) | 11 |
| `dUF` | 27 UFs + "não informado", com sigla e região (filtra SINAN e Completude) | 28 |
| `Projeto_Equipe` | Lido da seção 1 da doc: coordenadora, colaboradora e os alunos de IC (Lucas, Eduarda, Ester e Naylla), sem dados pessoais | 6 |
| `Projeto_Cronograma` | Lido da seção 16 da doc, com as três frentes (Eduarda, Lucas e Ester) e status automático pela data de hoje | 4 |
| `Projeto_Roadmap` | Lido da seção 20.2 da doc (só os checkboxes; `[x]` = Feito) | 19 (doc v1.4, 2026-10-20) |
| `Projeto_Dicionario` | Lido das seções 7 e 8 da doc, com categoria (definição do rótulo / clínico com risco de vazamento / chave de integração / variável-chave / candidata / administrativo / outros) | 125 |
| `_Medidas` | Todas as medidas, em 5 pastas | Não se aplica |

**Relações:** `dAno[Ano]` → `SINASC[AnoNascimento]`, `SINAN[AnoNotificacao]`, `SINAN_Completude[AnoNotificacao]`; `dUF[CodUF]` → `SINAN[CodUFRes]`, `SINAN_Completude[CodUFRes]`.
➡️ **Em eixos e segmentadores use sempre `dAno[Ano]` e `dUF[...]`** (as colunas de ano/UF das tabelas de fatos estão ocultas de propósito).

> As tabelas `Projeto_*` leem a `DOCUMENTACAO_TECNICA.md`: quando a doc mudar, basta **Atualizar** no Power BI.

### Medidas (tabela `_Medidas`, 34 no total)

| Pasta | Medidas |
|---|---|
| 1. Volume | Nascidos Vivos SP · Casos Notificados · Casos Residentes SP · Casos por 1.000 NV (SP) · % Casos do Brasil · Casos Δ% Ano Anterior · Nascidos Vivos Δ% Ano Anterior |
| 2. Pré-natal (SINASC-SP) | % Pré-natal 7+ Consultas · % Início Pré-natal 1º Trimestre · % Pré-natal Adequado (Kotelchuck) · Média de Consultas Pré-natal · % Baixo Peso ao Nascer · % Prematuros · % Partos Cesáreos · % Mães Adolescentes (<20) |
| 3. Perfil dos casos (SINAN) | % Mães que Fizeram Pré-natal (casos) · % Diagnóstico Materno no Pré-natal · % Tratamento Materno Adequado · % Parceiro Tratado · % Parceiro Tratado Ignorado/Branco · Óbitos por Sífilis Congênita · Abortos e Natimortos por Sífilis · Mediana Dias Diagnóstico → Notificação · % Notificados >1 Ano Após Diagnóstico |
| 4. Qualidade dos dados | Completude % · % Ignorado · % Válido · Classificação Completude (MS) · Cor Completude |
| 5. Projeto | Itens Roadmap Feitos · Itens Roadmap Pendentes · % Roadmap Concluído · Fase Atual · Dias até o Fim do Projeto |

## 2. Páginas sugeridas

Em todas as páginas: segmentador de **`dAno[Ano]`** (estilo "Entre" ou lista) no topo. Paleta sugerida: um tom principal (azul-petróleo) + vermelho só para alertas.

### Página 1: Visão geral

| Visual | Campos |
|---|---|
| 4 Cartões | `Nascidos Vivos SP` · `Casos Notificados` · `Casos Residentes SP` · `Casos por 1.000 NV (SP)` |
| Gráfico de linhas | Eixo `dAno[Ano]` · Valores `Casos Notificados` e `Casos Residentes SP` |
| Gráfico de colunas + linha | Eixo `dAno[Ano]` · Colunas `Nascidos Vivos SP` · Linha `Casos por 1.000 NV (SP)` |
| Caixa de texto | Aviso: *"SINASC cobre só SP; SINAN cobre o Brasil. 2025 é parcial. A razão por 1.000 NV usa ano de notificação no numerador; é ordem de grandeza, não taxa oficial."* |

### Página 2: SINASC-SP (pré-natal e nascimentos)

| Visual | Campos |
|---|---|
| Cartões | `% Pré-natal 7+ Consultas` · `% Início Pré-natal 1º Trimestre` · `% Pré-natal Adequado (Kotelchuck)` · `% Baixo Peso ao Nascer` · `% Prematuros` |
| Linhas | Eixo `dAno[Ano]` · `% Pré-natal 7+ Consultas`, `% Início Pré-natal 1º Trimestre`, `% Pré-natal Adequado (Kotelchuck)` |
| Colunas 100% empilhadas | Eixo `dAno[Ano]` · Legenda `SINASC[AdequacaoKotelchuck]` · Valor `Nascidos Vivos SP` |
| Barras | Eixo `SINASC[EscolaridadeMae]` · Valor `% Pré-natal 7+ Consultas` (mostra desigualdade por escolaridade) |
| Barras | Eixo `SINASC[FaixaIdadeMae]` · Valor `Nascidos Vivos SP` |
| Segmentadores | `SINASC[RacaMae]` · `SINASC[EstadoCivilMae]` |

### Página 3: SINAN-Brasil (casos de sífilis congênita)

| Visual | Campos |
|---|---|
| Mapa coroplético (ou Mapa de formas) | Local `dUF[UF]` (categoria = Estado) · Saturação `Casos Notificados` |
| Barras horizontais | Eixo `dUF[Sigla]` · Valor `Casos Notificados` · Dica de ferramenta `% Casos do Brasil` |
| Segmentador | `dUF[Regiao]` |
| Cartões | `% Mães que Fizeram Pré-natal (casos)` · `% Diagnóstico Materno no Pré-natal` · `% Tratamento Materno Adequado` · `% Parceiro Tratado` |
| Rosca | Legenda `SINAN[MomentoDiagMae]` · Valor `Casos Notificados` |
| Barras empilhadas | Eixo `SINAN[TratamentoMae]` · Legenda `SINAN[ParceiroTratado]` · Valor `Casos Notificados` |
| Colunas | Eixo `SINAN[DiagnosticoFinal]` · Valor `Casos Notificados` |
| Cartões | `Óbitos por Sífilis Congênita` · `Abortos e Natimortos por Sífilis` · `Mediana Dias Diagnóstico → Notificação` · `% Notificados >1 Ano Após Diagnóstico` |

> **Achado para destacar:** em todos os anos, ~78–83% das mães dos casos **fizeram pré-natal** e ~51–60% tiveram a sífilis **diagnosticada durante o pré-natal**, e só ~14–23% dos **parceiros foram tratados** (com ~28% de "ignorado" nesse campo). Ou seja: a maioria dos casos passou pelo pré-natal e teve a sífilis materna identificada, então houve oportunidade perdida de interromper a transmissão.
>
> ⚠️ **Não use o "% Tratamento Materno Adequado" (~3–6%) como achado.** Pela definição de caso do Ministério da Saúde, a criança só é notificada como sífilis congênita quando a mãe **não** foi tratada ou foi tratada de forma inadequada. Por isso, esse percentual é baixo **por construção**. Ele serve só para checar consistência da base. Para medir falha de tratamento seria preciso o SINAN de **sífilis em gestante** (fora do escopo atual). Detalhes na [seção 8.1 da doc](DOCUMENTACAO_TECNICA.md#81-observações-importantes-sobre-o-sifcbr).
>
> ⚠️ **~6,9% dos casos são aborto ou natimorto** (`Abortos e Natimortos por Sífilis`) e não existem no SINASC (só nascidos vivos).

### Página 4: Qualidade dos dados (completude do SINAN)

| Visual | Campos |
|---|---|
| Matriz | Linhas `SINAN_Completude[Campo]` · Colunas `dAno[Ano]` · Valores `% Válido`; *Formatação condicional → Cor da tela de fundo → Valor do campo → `Cor Completude`* |
| Tabela | `SINAN_Completude[Campo]` · `Completude %` · `% Ignorado` · `% Válido` · `Classificação Completude (MS)` (filtro: `CampoPrioritario = Verdadeiro`) |
| Segmentadores | `dUF[UF]` · `SINAN_Completude[CampoPrioritario]` |
| Barras | Eixo `dUF[Sigla]` · Valor `% Válido` (filtro de visual: Campo = `ANT_TRATAD`), para o ranking de UFs no preenchimento do tratamento do parceiro |
| Caixa de texto | Critério MS (Brasil, 2019): excelente ≥95%, bom 90–95%, regular 70–90%, ruim 50–70%, muito ruim <50%. "Ignorado" = códigos 9/09/99, só faz sentido em campos categóricos. |

> **Achado:** os piores campos prioritários são **escolaridade da mãe (28,5% ignorado)** e **parceiro tratado (27,8% ignorado)**, ambos com classificação *Regular*, coerente com Monteiro Neta et al. (2025).

### Página 5: Projeto (equipe, cronograma, roadmap, dicionário)

| Visual | Campos |
|---|---|
| Cartões | `Fase Atual` · `% Roadmap Concluído` · `Itens Roadmap Pendentes` · `Dias até o Fim do Projeto` |
| Tabela (equipe) | `Projeto_Equipe[Nome]`, `[Papel]`, `[Curso]`, `[Campus]`, `[Semestre]`, `[Foco]`, ordenada por `Ordem` |
| Tabela (cronograma) | `Projeto_Cronograma[Periodo]`, `[Status]`, `[EngenhariaDados]`, `[Modelagem]`, `[Epidemiologia]`, com formatação condicional em `Status` |
| Tabela | `Projeto_Roadmap[Item]`, `[Tipo]`, `[Status]`, ordenada por `Ordem`; ícone/cor por Status |
| Tabela + segmentadores | `Projeto_Dicionario[Base]`, `[Campo]`, `[Descricao]`, `[Observacao]`, `[Categoria]` · segmentadores `Base` e `Categoria` |

## 3. Cuidados ao interpretar

- **SINASC = só SP; SINAN = Brasil.** O filtro de UF não afeta as medidas de SINASC; `Casos por 1.000 NV (SP)` fica em branco se a UF selecionada não for SP.
- **Ano do SINAN = ano da notificação**, não do diagnóstico nem do nascimento.
- **2025 é parcial** (só SINAN, ~meio ano); `Casos Δ% Ano Anterior` fica em branco em 2025 de propósito.
- **A base pública do SINAN só traz casos confirmados** (`EVO_DIAG_N` 1–4 em 100% dos registros; não há "descartados"), então não serve sozinha como rótulo negativo para o modelo de ML.
- **Rótulos de código** (ex.: "Adequado", "Ignorado") foram aplicados a partir do dicionário público e ainda precisam ser **validados contra o dicionário oficial** (item do roadmap). Os códigos brutos estão nas pastas *Códigos brutos* de cada tabela.
