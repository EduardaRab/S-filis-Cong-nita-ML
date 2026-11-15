"""
Junta os relatórios de nulos e de duplicados do SINASC num único Excel formatado.
Rodar depois de verificacao_nulos_sinasc.py e verificacao_duplicados_sinasc.py.

Uso:
    python gerar_excel_consolidado_sinasc.py [arquivo_saida.xlsx]
"""

import os
import sys
from datetime import date

import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from sinasc_comum import ANOS_ALVO, CODIGOS_IGNORADO, FONTE_CODIGO, PASTA_SAIDA_PADRAO

periodo = f"{ANOS_ALVO[0]}_{ANOS_ALVO[-1]}"
rel_nulos = os.path.join(PASTA_SAIDA_PADRAO, f"Relatorio_Analise_Nulos_SINASC_{periodo}.xlsx")
rel_dup = os.path.join(PASTA_SAIDA_PADRAO, f"Relatorio_Duplicados_SINASC_{periodo}.xlsx")
saida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    PASTA_SAIDA_PADRAO, f"Analises_Qualidade_SINASC_{periodo}.xlsx")

nulos = pd.read_excel(rel_nulos, sheet_name=None, dtype={"Codigo_Ignorado": str})
dup = pd.read_excel(rel_dup, sheet_name=None, dtype=str)

FONTE = "Arial"
AZUL = "1F4E78"
F_TITULO = Font(name=FONTE, size=14, bold=True, color=AZUL)
F_SUB = Font(name=FONTE, size=11, bold=True, color=AZUL)
F_CAB = Font(name=FONTE, size=10, bold=True, color="FFFFFF")
F_TXT = Font(name=FONTE, size=10)
F_NOTA = Font(name=FONTE, size=9, italic=True, color="595959")
P_CAB = PatternFill("solid", start_color=AZUL)
BORDA = Border(bottom=Side(style="thin", color="D9D9D9"))
P_CRIT = PatternFill("solid", start_color="F8CBAD")
P_ATEN = PatternFill("solid", start_color="FFE699")
P_OK = PatternFill("solid", start_color="E2EFDA")

wb = Workbook()
wb.remove(wb.active)


def cabecalho(ws, linha, colunas):
    for j, nome in enumerate(colunas, start=1):
        c = ws.cell(row=linha, column=j, value=nome)
        c.font, c.fill = F_CAB, P_CAB
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[linha].height = 32


def larguras(ws, mapa):
    for col, w in mapa.items():
        ws.column_dimensions[col].width = w


def titulo(ws, texto, sub=None):
    ws["A1"] = texto
    ws["A1"].font = F_TITULO
    if sub:
        ws["A2"] = sub
        ws["A2"].font = F_NOTA


def num(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return v


def escreve_df(ws, df, linha_ini, formatos=None, manter_texto=False):
    """Escreve um DataFrame (cabeçalho + linhas) e devolve a última linha usada."""
    cabecalho(ws, linha_ini, list(df.columns))
    formatos = formatos or {}
    for i, row in enumerate(df.itertuples(index=False), start=linha_ini + 1):
        for j, v in enumerate(row, start=1):
            c = ws.cell(row=i, column=j, value=None if pd.isna(v) else (v if manter_texto else num(v)))
            c.font, c.border = F_TXT, BORDA
            nome = df.columns[j - 1]
            if nome in formatos:
                c.number_format = formatos[nome]
    return linha_ini + len(df)


def status_formula(cel_pct):
    return (f'=IF({cel_pct}>=0.5,"Crítico (>= 50%)",IF({cel_pct}>=0.2,"Atenção (20% a 49,9%)",'
            f'IF({cel_pct}>0,"Aceitável (< 20%)","Completo (0%)")))')


def aba_completude(nome_aba, df, titulo_txt):
    """Tabela de completude com % e status calculados por fórmula a partir das quantidades."""
    ws = wb.create_sheet(nome_aba)
    titulo(ws, titulo_txt, "Perda total = nulo técnico (campo vazio) + código de 'Ignorado' da variável. "
                           "% e status são fórmulas sobre as quantidades.")
    cols = ["Variável", "Código ignorado", "Total de registros", "Nulos (vazio)", "% Nulos",
            "Ignorados", "% Ignorados", "Perda total", "% Perda total", "Status de qualidade"]
    L0 = 4
    cabecalho(ws, L0, cols)
    for i, r in enumerate(df.itertuples(index=False), start=L0 + 1):
        ws.cell(row=i, column=1, value=r.Variavel_DBF)
        ws.cell(row=i, column=2, value=r.Codigo_Ignorado)
        ws.cell(row=i, column=3, value=int(r.Total_Registros))
        ws.cell(row=i, column=4, value=int(r.Qtd_Nulos_NaN))
        ws.cell(row=i, column=5, value=f"=IF(C{i}=0,0,D{i}/C{i})")
        ws.cell(row=i, column=6, value=int(r.Qtd_Ignorado))
        ws.cell(row=i, column=7, value=f"=IF(C{i}=0,0,F{i}/C{i})")
        ws.cell(row=i, column=8, value=f"=D{i}+F{i}")
        ws.cell(row=i, column=9, value=f"=IF(C{i}=0,0,H{i}/C{i})")
        ws.cell(row=i, column=10, value=status_formula(f"I{i}"))
        for j in range(1, 11):
            c = ws.cell(row=i, column=j)
            c.font, c.border = F_TXT, BORDA
        for j in (3, 4, 6, 8):
            ws.cell(row=i, column=j).number_format = "#,##0"
        for j in (5, 7, 9):
            ws.cell(row=i, column=j).number_format = "0.00%"
    fim = L0 + len(df)
    faixa = f"I{L0 + 1}:I{fim}"
    ws.conditional_formatting.add(faixa, CellIsRule(operator="greaterThanOrEqual", formula=["0.5"], fill=P_CRIT))
    ws.conditional_formatting.add(faixa, CellIsRule(operator="between", formula=["0.2", "0.4999999"], fill=P_ATEN))
    ws.conditional_formatting.add(faixa, CellIsRule(operator="lessThan", formula=["0.2"], fill=P_OK))
    larguras(ws, {"A": 16, "B": 11, "C": 13, "D": 13, "E": 10, "F": 11, "G": 11, "H": 13, "I": 12, "J": 24})
    ws.freeze_panes = ws.cell(row=L0 + 1, column=2)
    ws.auto_filter.ref = f"A{L0}:J{fim}"
    return ws


# ---------------------------------------------------------------- Leia-me
ws = wb.create_sheet("Leia-me")
titulo(ws, f"Análise de qualidade do SINASC (DNSP), {ANOS_ALVO[0]} a {ANOS_ALVO[-1]}")
cons = nulos[f"Consolidado_{periodo}"]
total = int(cons["Total_Registros"].iloc[0])
dres = dup["1_Resumo_Consolidado"]
linhas = [
    ("O que é", "Réplica, para o SINASC, das análises de completude (nulos/ignorados) e de duplicidade "
                "feitas para o SINAN (verificacao_nulos.py e verificacao_duplicados.py)."),
    ("Base", "SINASC, Declarações de Nascido Vivo, mães residentes no estado de SP "
             "(arquivos DNSP2020.csv a DNSP2024.csv, DATASUS)."),
    ("Período", f"{ANOS_ALVO[0]} a {ANOS_ALVO[-1]} (mesmo recorte do SINAN; o SINASC de 2025 ainda não foi publicado)."),
    ("Registros analisados", f"{total:,}".replace(",", ".") + " nascidos vivos."),
    ("Gerado em", date.today().strftime("%d/%m/%Y") + " pelos scripts verificacao_nulos_sinasc.py, "
                  "verificacao_duplicados_sinasc.py e gerar_excel_consolidado_sinasc.py."),
    ("", ""),
    ("ABAS", ""),
    ("Nulos_Consolidado", "Completude de cada variável somando todos os anos."),
    ("Nulos_Evolucao_Anual", "% de perda total de cada variável, ano a ano (escala de cor)."),
    ("Nulos_AAAA", "Completude de cada variável em cada ano."),
    ("Dup_Resumo", "Quantidade de registros duplicados por critério, todos os anos juntos."),
    ("Dup_Comparativo_Anual", "% de registros excedentes por critério e ano."),
    ("Dup_Detalhado_Ano", "Métricas completas de duplicidade por ano e critério."),
    ("Dup_Amostra_Pares", "Até 500 registros do critério 3, ordenados para os pares ficarem lado a lado."),
    ("Codigos_Ignorado", "Código considerado 'Ignorado' em cada variável."),
    ("", ""),
    ("DIFERENÇAS EM RELAÇÃO AO SINAN", ""),
    ("Código ignorado", "No SINAN, a regra única era '9' ou '99'. No SINASC o código muda por variável "
                        "(ex.: em CONSPRENAT '9' = 9 consultas e o ignorado é '99'; em ESCMAEAGR1 é '09'; "
                        "em TPROBSON é '11'). Por isso foi usado um mapa por variável (aba Codigos_Ignorado)."),
    ("Chaves de duplicidade", "O SINASC público não tem número da DN nem nome da mãe. Os critérios usam data/hora "
                              "do nascimento, estabelecimento, sexo, peso e data de nascimento da mãe. "
                              "A coluna CONTADOR (sequencial) foi excluída da comparação de linha idêntica."),
    ("Gêmeos", "Gêmeos compartilham mãe, data e local. A coluna 'Envolvidos_Gravidez_Multipla' mostra quantos "
               "registros envolvidos são de gravidez dupla/tripla. No critério 4 (amplo) a maioria é gêmeo, "
               "não erro de registro."),
    ("", ""),
    ("COMO LER OS 'CRÍTICOS'", ""),
    ("DTRECORIGA", "Vazio em 100% dos registros. Pelo dicionário, deveria ser preenchido (cópia de DTRECORIG, "
                   "ou DTRECEBIM, ou DTCADASTRO); na base disseminada não vem. Não usar."),
    ("CODANOMAL", "Só é preenchido quando há anomalia (IDANOMAL = 1, menos de 2% dos nascidos). Vazio é esperado."),
    ("DTULTMENST", "Data da última menstruação: opcional quando a idade gestacional é estimada por outro método."),
    ("IDADEPAI", "Ausência alta e real (~52%): dado do pai pouco preenchido na DN. Pouco útil para o modelo."),
    ("SERIESCMAE", "Só se aplica a alguns níveis de escolaridade (ESCMAE2010). Vazio é parcialmente esperado."),
    ("", ""),
    ("DICIONÁRIO DE DADOS", ""),
    ("Referência", "SINASC: Estrutura de 1996 a 2019 – Dicionário de Dados (MS/SVS/CGIAE). "
                   "https://diaad.s3.sa-east-1.amazonaws.com/sinasc/SINASC+-+Estrutura.pdf"),
    ("Fonte do código", "A aba Codigos_Ignorado diz, para cada variável, se o código de ignorado está no dicionário, "
                        "se é convenção do DATASUS (o dicionário não lista os valores do campo, ex.: IDADEMAE, "
                        "CONSPRENAT, APGAR) ou se é um valor fora do domínio do dicionário (LOCNASC = 9)."),
    ("Cobertura", "O dicionário vai até 2019; a análise é de 2020 a 2024. Os valores encontrados nos dados "
                  "seguem os mesmos domínios."),
    ("TPMETESTIM = 8", "O dicionário só prevê 1 (exame físico), 2 (outro método) e 9 (ignorado), mas ~40% dos "
                       "registros têm 8. Não foi contado como ignorado; tratar como categoria sem documentação."),
    ("Raça/cor (RN e mãe)", "O dicionário não tem código de ignorado (1 a 5); só os campos vazios contam como perda."),
    ("", ""),
    ("LEGENDA DE STATUS", ""),
    ("Crítico", ">= 50% de perda total"),
    ("Atenção", "20% a 49,9%"),
    ("Aceitável", "> 0% e < 20%"),
    ("Completo", "0%"),
]
for i, (a, b) in enumerate(linhas, start=3):
    ca, cb = ws.cell(row=i, column=1, value=a or None), ws.cell(row=i, column=2, value=b or None)
    ca.font = F_SUB if a and a.isupper() else Font(name=FONTE, size=10, bold=True)
    cb.font = F_TXT
    cb.alignment = Alignment(wrap_text=True, vertical="top")
    ca.alignment = Alignment(vertical="top")
    if a in ("Crítico", "Atenção", "Aceitável", "Completo"):
        ca.fill = {"Crítico": P_CRIT, "Atenção": P_ATEN, "Aceitável": P_OK, "Completo": P_OK}[a]
larguras(ws, {"A": 26, "B": 110})

# ---------------------------------------------------------------- Nulos
aba_completude("Nulos_Consolidado", cons, f"Completude das variáveis, consolidado {ANOS_ALVO[0]}–{ANOS_ALVO[-1]}")

ws = wb.create_sheet("Nulos_Evolucao_Anual")
titulo(ws, "% de perda total (nulo + ignorado) por variável e ano",
       "Valores em % (0 a 100). Verde = baixa perda, vermelho = alta perda.")
matriz = nulos["Matriz_Evolucao_Anual"].copy()
matriz.columns = ["Variável"] + [c.replace(" (%)", "").replace("Perda_", "").replace("Consolidado_", "Consolidado ")
                                 .replace("_", "–") for c in matriz.columns[1:]]
fim = escreve_df(ws, matriz, 4, {c: "0.00" for c in matriz.columns[1:]})
ultima = get_column_letter(len(matriz.columns))
ws.conditional_formatting.add(f"B5:{ultima}{fim}", ColorScaleRule(
    start_type="num", start_value=0, start_color="E2EFDA",
    mid_type="num", mid_value=20, mid_color="FFE699",
    end_type="num", end_value=100, end_color="F8CBAD"))
larguras(ws, {"A": 16, **{get_column_letter(j): 14 for j in range(2, len(matriz.columns) + 1)}})
ws.freeze_panes = "B5"

for ano in ANOS_ALVO:
    if f"Ano_{ano}" in nulos:
        aba_completude(f"Nulos_{ano}", nulos[f"Ano_{ano}"], f"Completude das variáveis, {ano}")

# ---------------------------------------------------------------- Duplicados
ws = wb.create_sheet("Dup_Resumo")
titulo(ws, f"Registros duplicados por critério, consolidado {ANOS_ALVO[0]}–{ANOS_ALVO[-1]}",
       "Envolvidos = linhas em algum grupo duplicado. Excedentes = linhas que sobrariam mantendo 1 por grupo. "
       "% calculados por fórmula.")
cols = ["Critério", "Colunas utilizadas", "Total de registros", "Registros envolvidos", "% Envolvidos",
        "Registros excedentes", "% Excedentes", "Envolvidos de gravidez múltipla", "% Envolvidos que são gêmeos"]
cabecalho(ws, 4, cols)
for i, r in enumerate(dres.itertuples(index=False), start=5):
    vals = [r.Criterio_Analise, r.Colunas_Utilizadas, int(r.Total_Registros), int(r.Registros_Envolvidos),
            f"=IF(C{i}=0,0,D{i}/C{i})", int(r.Registros_Excedentes), f"=IF(C{i}=0,0,F{i}/C{i})",
            int(r.Envolvidos_Gravidez_Multipla), f"=IF(D{i}=0,0,H{i}/D{i})"]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.font, c.border = F_TXT, BORDA
        c.alignment = Alignment(wrap_text=(j == 2), vertical="top")
    for j in (3, 4, 6, 8):
        ws.cell(row=i, column=j).number_format = "#,##0"
    for j in (5, 7):
        ws.cell(row=i, column=j).number_format = "0.0000%"
    ws.cell(row=i, column=9).number_format = "0.0%"
larguras(ws, {"A": 24, "B": 60, "C": 13, "D": 13, "E": 12, "F": 13, "G": 12, "H": 16, "I": 14})

ws = wb.create_sheet("Dup_Comparativo_Anual")
titulo(ws, "% de registros excedentes por critério e ano", "Valores em % (0 a 100), duplicidade dentro de cada ano.")
piv = dup["2_Comparativo_Anual_Pct"].rename(columns={"Criterio_Analise": "Critério"})
escreve_df(ws, piv, 4, {c: "0.0000" for c in piv.columns[1:]})
larguras(ws, {"A": 24, **{get_column_letter(j): 12 for j in range(2, len(piv.columns) + 1)}})

ws = wb.create_sheet("Dup_Detalhado_Ano")
titulo(ws, "Métricas de duplicidade por ano e critério", "Percentuais em % (0 a 100).")
det = dup["3_Detalhado_Por_Ano"]
fmt = {c: "#,##0" for c in det.columns if c.startswith(("Total", "Registros", "Envolvidos"))}
fmt.update({c: "0.0000" for c in det.columns if c.startswith("Pct")})
escreve_df(ws, det, 4, fmt)
larguras(ws, {"A": 8, "B": 24, **{get_column_letter(j): 14 for j in range(3, len(det.columns) + 1)}})
ws.freeze_panes = "C5"

if "4_Amostra_Pares_Duplicados" in dup:
    ws = wb.create_sheet("Dup_Amostra_Pares")
    titulo(ws, "Amostra de registros duplicados (critério 3: mesmo RN, chave forte)",
           "Até 500 linhas, ordenadas pela chave para os pares ficarem um abaixo do outro.")
    amostra = dup["4_Amostra_Pares_Duplicados"]
    escreve_df(ws, amostra, 4, manter_texto=True)
    for j in range(1, len(amostra.columns) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 12
    ws.freeze_panes = "A5"

# ---------------------------------------------------------------- Dicionário de códigos
ws = wb.create_sheet("Codigos_Ignorado")
titulo(ws, "Código de 'Ignorado' usado em cada variável",
       "Variáveis fora desta lista (datas, códigos de município, CBO, contadores) só contam nulo técnico (vazio).")
dic = pd.DataFrame([{"Variável": k, "Código(s) ignorado": ", ".join(v), "Fonte": FONTE_CODIGO[k]}
                    for k, v in CODIGOS_IGNORADO.items()])
escreve_df(ws, dic, 4, manter_texto=True)
larguras(ws, {"A": 16, "B": 20, "C": 44})

for s in wb.worksheets:
    s.sheet_view.showGridLines = False
wb.calculation.fullCalcOnLoad = True
wb.save(saida)
print(f"Excel consolidado salvo em: {saida}")
