"""
Junta os relatórios de nulos e duplicados do SINASC e do SINAN num único Excel formatado.
Rodar depois de qualidade_nulos.py e qualidade_duplicados.py para as duas bases.

Uso:
    python gerar_excel_qualidade.py [arquivo_saida.xlsx]
"""

import os
import sys
from datetime import date

import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import sinan_comum
import sinasc_comum
from qualidade_comum import PASTA_SAIDA_PADRAO, caminho_relatorio, periodo

saida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PASTA_SAIDA_PADRAO, "Analises_Qualidade_SINASC_SINAN.xlsx")

FONTE = "Arial"
AZUL = "1F4E78"
F_TITULO = Font(name=FONTE, size=14, bold=True, color=AZUL)
F_SUB = Font(name=FONTE, size=11, bold=True, color=AZUL)
F_NEG = Font(name=FONTE, size=10, bold=True)
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


# ---------------------------------------------------------------- utilitários
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
    ws["A1"], ws["A1"].font = texto, F_TITULO
    if sub:
        ws["A2"], ws["A2"].font = sub, F_NOTA


def num(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return v


def escreve_df(ws, df, linha_ini, formatos=None, manter_texto=False):
    cabecalho(ws, linha_ini, list(df.columns))
    formatos = formatos or {}
    for i, row in enumerate(df.itertuples(index=False), start=linha_ini + 1):
        for j, v in enumerate(row, start=1):
            c = ws.cell(row=i, column=j, value=None if pd.isna(v) else (v if manter_texto else num(v)))
            c.font, c.border = F_TXT, BORDA
            if df.columns[j - 1] in formatos:
                c.number_format = formatos[df.columns[j - 1]]
    return linha_ini + len(df)


def status_formula(cel):
    return (f'=IF({cel}>=0.5,"Crítico (>= 50%)",IF({cel}>=0.2,"Atenção (20% a 49,9%)",'
            f'IF({cel}>0,"Aceitável (< 20%)","Completo (0%)")))')


def aba_completude(nome_aba, df, titulo_txt):
    ws = wb.create_sheet(nome_aba)
    titulo(ws, titulo_txt, "Perda total = nulo técnico (campo vazio) + código de 'Ignorado' da variável. "
                           "% e status são fórmulas sobre as quantidades.")
    L0 = 4
    cabecalho(ws, L0, ["Variável", "Código ignorado", "Total de registros", "Nulos (vazio)", "% Nulos",
                       "Ignorados", "% Ignorados", "Perda total", "% Perda total", "Status de qualidade"])
    for i, r in enumerate(df.itertuples(index=False), start=L0 + 1):
        vals = [r.Variavel_DBF, r.Codigo_Ignorado, int(r.Total_Registros), int(r.Qtd_Nulos_NaN),
                f"=IF(C{i}=0,0,D{i}/C{i})", int(r.Qtd_Ignorado), f"=IF(C{i}=0,0,F{i}/C{i})",
                f"=D{i}+F{i}", f"=IF(C{i}=0,0,H{i}/C{i})", status_formula(f"I{i}")]
        for j, v in enumerate(vals, start=1):
            c = ws.cell(row=i, column=j, value=v)
            c.font, c.border = F_TXT, BORDA
            c.number_format = "#,##0" if j in (3, 4, 6, 8) else ("0.00%" if j in (5, 7, 9) else "General")
    fim = L0 + len(df)
    faixa = f"I{L0 + 1}:I{fim}"
    ws.conditional_formatting.add(faixa, CellIsRule(operator="greaterThanOrEqual", formula=["0.5"], fill=P_CRIT))
    ws.conditional_formatting.add(faixa, CellIsRule(operator="between", formula=["0.2", "0.4999999"], fill=P_ATEN))
    ws.conditional_formatting.add(faixa, CellIsRule(operator="lessThan", formula=["0.2"], fill=P_OK))
    larguras(ws, {"A": 16, "B": 11, "C": 13, "D": 13, "E": 10, "F": 11, "G": 11, "H": 13, "I": 12, "J": 24})
    ws.freeze_panes = ws.cell(row=L0 + 1, column=2)
    ws.auto_filter.ref = f"A{L0}:J{fim}"
    return fim


def secao_base(base):
    """Cria todas as abas de uma base. Retorna dados para a Visão Geral."""
    P, per = base.NOME, periodo(base)
    anos = f"{base.ANOS_ALVO[0]}–{base.ANOS_ALVO[-1]}"
    nulos = pd.read_excel(caminho_relatorio(base, "Nulos"), sheet_name=None, dtype={"Codigo_Ignorado": str})
    dup = pd.read_excel(caminho_relatorio(base, "Duplicados"), sheet_name=None, dtype=str)

    cons = nulos[f"Consolidado_{per}"]
    fim_cons = aba_completude(f"{P}_Nulos_Consolidado", cons, f"{P}: completude das variáveis, consolidado {anos}")

    ws = wb.create_sheet(f"{P}_Nulos_Evolucao")
    titulo(ws, f"{P}: % de perda total (nulo + ignorado) por variável e ano",
           "Valores em % (0 a 100). Verde = baixa perda, vermelho = alta perda. Vazio = coluna não existe no ano.")
    matriz = nulos["Matriz_Evolucao_Anual"].copy()
    matriz.columns = ["Variável"] + [c.replace(" (%)", "").replace("Perda_", "").replace("Consolidado_", "Consolidado ")
                                     .replace("_", "–") for c in matriz.columns[1:]]
    fim = escreve_df(ws, matriz, 4, {c: "0.00" for c in matriz.columns[1:]})
    ult = get_column_letter(len(matriz.columns))
    ws.conditional_formatting.add(f"B5:{ult}{fim}", ColorScaleRule(
        start_type="num", start_value=0, start_color="E2EFDA", mid_type="num", mid_value=20,
        mid_color="FFE699", end_type="num", end_value=100, end_color="F8CBAD"))
    larguras(ws, {"A": 16, **{get_column_letter(j): 14 for j in range(2, len(matriz.columns) + 1)}})
    ws.freeze_panes = "B5"

    for ano in base.ANOS_ALVO:
        if f"Ano_{ano}" in nulos:
            aba_completude(f"{P}_Nulos_{ano}", nulos[f"Ano_{ano}"], f"{P}: completude das variáveis, {ano}")

    # Duplicados: resumo com % por fórmula
    ws = wb.create_sheet(f"{P}_Dup_Resumo")
    titulo(ws, f"{P}: registros duplicados por critério, consolidado {anos}",
           "Envolvidos = linhas em algum grupo duplicado. Excedentes = linhas que sobrariam mantendo 1 por grupo.")
    dres = dup["1_Resumo_Consolidado"]
    tem_gemeos = "Envolvidos_Gravidez_Multipla" in dres.columns
    cols = ["Critério", "Colunas utilizadas", "Total de registros", "Registros envolvidos", "% Envolvidos",
            "Registros excedentes", "% Excedentes"]
    if tem_gemeos:
        cols += ["Envolvidos de gravidez múltipla", "% Envolvidos que são gêmeos"]
    cabecalho(ws, 4, cols)
    for i, r in enumerate(dres.itertuples(index=False), start=5):
        vals = [r.Criterio_Analise, r.Colunas_Utilizadas, int(r.Total_Registros), int(r.Registros_Envolvidos),
                f"=IF(C{i}=0,0,D{i}/C{i})", int(r.Registros_Excedentes), f"=IF(C{i}=0,0,F{i}/C{i})"]
        if tem_gemeos:
            vals += [int(r.Envolvidos_Gravidez_Multipla), f"=IF(D{i}=0,0,H{i}/D{i})"]
        for j, v in enumerate(vals, start=1):
            c = ws.cell(row=i, column=j, value=v)
            c.font, c.border = F_TXT, BORDA
            c.alignment = Alignment(wrap_text=(j == 2), vertical="top")
            c.number_format = {3: "#,##0", 4: "#,##0", 6: "#,##0", 8: "#,##0",
                               5: "0.0000%", 7: "0.0000%", 9: "0.0%"}.get(j, "General")
    larguras(ws, {"A": 24, "B": 60, "C": 13, "D": 13, "E": 12, "F": 13, "G": 12, "H": 16, "I": 14})

    ws = wb.create_sheet(f"{P}_Dup_Comparativo")
    titulo(ws, f"{P}: % de registros excedentes por critério e ano",
           "Valores em % (0 a 100), duplicidade dentro de cada ano.")
    piv = dup["2_Comparativo_Anual_Pct"].rename(columns={"Criterio_Analise": "Critério"})
    escreve_df(ws, piv, 4, {c: "0.0000" for c in piv.columns[1:]})
    larguras(ws, {"A": 24, **{get_column_letter(j): 12 for j in range(2, len(piv.columns) + 1)}})

    ws = wb.create_sheet(f"{P}_Dup_Detalhado")
    titulo(ws, f"{P}: métricas de duplicidade por ano e critério", "Percentuais em % (0 a 100).")
    det = dup["3_Detalhado_Por_Ano"]
    fmt = {c: "#,##0" for c in det.columns if c.startswith(("Total", "Registros", "Envolvidos"))}
    fmt.update({c: "0.0000" for c in det.columns if c.startswith("Pct")})
    escreve_df(ws, det, 4, fmt)
    larguras(ws, {"A": 8, "B": 24, **{get_column_letter(j): 14 for j in range(3, len(det.columns) + 1)}})
    ws.freeze_panes = "C5"

    if "4_Amostra_Pares_Duplicados" in dup:
        ws = wb.create_sheet(f"{P}_Dup_Amostra")
        titulo(ws, f"{P}: amostra de registros duplicados (critério {base.CRITERIO_AMOSTRA})",
               "Até 500 linhas, ordenadas pela chave para os pares ficarem um abaixo do outro.")
        amostra = dup["4_Amostra_Pares_Duplicados"]
        escreve_df(ws, amostra, 4, manter_texto=True)
        for j in range(1, len(amostra.columns) + 1):
            ws.column_dimensions[get_column_letter(j)].width = 12
        ws.freeze_panes = "A5"

    ws = wb.create_sheet(f"{P}_Codigos_Ignorado")
    titulo(ws, f"{P}: código de 'Ignorado' usado em cada variável",
           "Variáveis fora desta lista (datas, códigos de município, textos) só contam nulo técnico (vazio).")
    dic = pd.DataFrame([{"Variável": k, "Código(s) ignorado": ", ".join(v), "Fonte": base.FONTE_CODIGO[k]}
                        for k, v in base.CODIGOS_IGNORADO.items()])
    escreve_df(ws, dic, 4, manter_texto=True)
    larguras(ws, {"A": 16, "B": 20, "C": 44})

    return {"base": base, "anos": anos, "aba_cons": f"{P}_Nulos_Consolidado", "fim_cons": fim_cons,
            "aba_dup": f"{P}_Dup_Resumo", "n_crit": len(dres)}


# ---------------------------------------------------------------- Leia-me (criada primeiro)
leia = wb.create_sheet("Leia-me")
visao = wb.create_sheet("Visao_Geral")
info = [secao_base(sinasc_comum), secao_base(sinan_comum)]

titulo(leia, "Análise de qualidade dos dados: SINASC e SINAN (sífilis congênita)")
linhas = [
    ("O que é", "Análises de completude (campos vazios + códigos de 'Ignorado') e de duplicidade das duas bases do "
                "projeto, com a mesma lógica de verificacao_nulos.py e verificacao_duplicados.py (análise do SINAN)."),
    ("Gerado em", date.today().strftime("%d/%m/%Y") + " pelos scripts qualidade_nulos.py, qualidade_duplicados.py e "
                  "gerar_excel_qualidade.py."),
    ("", ""),
    ("BASES ANALISADAS", ""),
    ("SINASC", f"{sinasc_comum.DESCRICAO}. Período {info[0]['anos']} (o SINASC de 2025 ainda não foi publicado)."),
    ("SINAN", f"{sinan_comum.DESCRICAO}. Período {info[1]['anos']} (2025 é ano parcial)."),
    ("", ""),
    ("ABAS (prefixo SINASC_ ou SINAN_)", ""),
    ("Visao_Geral", "Resumo lado a lado das duas bases."),
    ("*_Nulos_Consolidado", "Completude de cada variável somando todos os anos."),
    ("*_Nulos_Evolucao", "% de perda total de cada variável, ano a ano (escala de cor)."),
    ("*_Nulos_AAAA", "Completude de cada variável em cada ano."),
    ("*_Dup_Resumo", "Registros duplicados por critério, todos os anos juntos."),
    ("*_Dup_Comparativo", "% de registros excedentes por critério e ano."),
    ("*_Dup_Detalhado", "Métricas completas de duplicidade por ano e critério."),
    ("*_Dup_Amostra", "Até 500 registros do critério 3, ordenados para os pares ficarem lado a lado."),
    ("*_Codigos_Ignorado", "Código considerado 'Ignorado' em cada variável e de onde ele vem."),
    ("", ""),
    ("SINAN: AJUSTES EM RELAÇÃO AOS SCRIPTS ORIGINAIS", ""),
    ("Leitura", "Os scripts originais leem .xlsx; aqui foram lidos os CSVs SIFCBR20 a SIFCBR25 da pasta do projeto."),
    ("ESCOLMAE / CS_ESCOL_N", "O 'Ignorado' vem com zero à esquerda ('09'). A regra original ('9' ou '99') não pegava "
                              "esses registros: ESCOLMAE passa de 0% para 29,2% de ignorado (40.732 registros)."),
    ("CS_SEXO", "O ignorado é 'I' (M/F/I). A regra original não pegava: 8.336 registros (6,0%)."),
    ("Chaves de duplicidade", "Os CSVs não têm NU_NOTIFIC nem ID_UNIDADE, e DT_NASC só existe em 2023. Com as chaves "
                              "originais, o critério 2 virava 'mesma data + mesmo município' e os critérios 3/4 só "
                              "olhavam 2023. Foram trocadas por DT_DIAG, NU_IDADE_N, ID_MN_RESI, ANT_IDADE etc. "
                              "(ver coluna 'Colunas utilizadas' em SINAN_Dup_Resumo)."),
    ("DT_NASC", "Só existe no arquivo de 2023; por isso aparece com ~82% de vazio no consolidado."),
    ("", ""),
    ("SINASC: PONTOS DE ATENÇÃO", ""),
    ("Código ignorado", "Muda por variável (ex.: em CONSPRENAT '9' = 9 consultas e o ignorado é '99'; em ESCMAEAGR1 "
                        "é '09'; em TPROBSON é '11'). Conferido com o dicionário SINASC: Estrutura de 1996 a 2019 "
                        "(https://diaad.s3.sa-east-1.amazonaws.com/sinasc/SINASC+-+Estrutura.pdf)."),
    ("Gêmeos", "Gêmeos compartilham mãe, data e local. No critério 4 (amplo) a maioria dos 'duplicados' é gêmeo."),
    ("CONTADOR", "Sequencial do arquivo; fica fora da comparação de linha 100% idêntica."),
    ("TPMETESTIM = 8", "O dicionário só prevê 1, 2 e 9, mas ~40% dos registros têm 8. Não foi contado como ignorado."),
    ("DTRECORIGA", "Vazio em 100% dos registros, embora o dicionário diga que deveria ser preenchido. Não usar."),
    ("", ""),
    ("COMO LER OS 'CRÍTICOS'", ""),
    ("Campos condicionais", "Vários campos só são preenchidos quando a resposta anterior pede (ex.: CODANOMAL só com "
                            "anomalia; DT_OBITO só com óbito; DS_ESQUEMA e SIN_OUTR_E são texto livre opcional). "
                            "Vazio alto nesses campos é esperado e não é falha de preenchimento."),
    ("Campos sempre vazios", "SINASC: DTRECORIGA. SINAN: SEM_DIAG e TRA_DIAG_C (100% vazios)."),
    ("Ausência real", "SINASC: IDADEPAI (~52%). SINAN: ANT_TRATAD (31% ignorado) e ESCOLMAE (29% ignorado)."),
    ("", ""),
    ("LEGENDA DE STATUS", ""),
    ("Crítico", ">= 50% de perda total"),
    ("Atenção", "20% a 49,9%"),
    ("Aceitável", "> 0% e < 20%"),
    ("Completo", "0%"),
]
for i, (a, b) in enumerate(linhas, start=3):
    ca, cb = leia.cell(row=i, column=1, value=a or None), leia.cell(row=i, column=2, value=b or None)
    ca.font = F_SUB if a and a == a.upper() and len(a) > 8 and " " in a else F_NEG
    cb.font = F_TXT
    cb.alignment = Alignment(wrap_text=True, vertical="top")
    ca.alignment = Alignment(vertical="top", wrap_text=True)
    if a in ("Crítico", "Atenção", "Aceitável", "Completo"):
        ca.fill = {"Crítico": P_CRIT, "Atenção": P_ATEN}.get(a, P_OK)
larguras(leia, {"A": 30, "B": 110})

# ---------------------------------------------------------------- Visão geral (fórmulas sobre as outras abas)
titulo(visao, "Visão geral: SINASC x SINAN", "Tudo nesta aba é fórmula sobre as abas de cada base.")
cabecalho(visao, 4, ["Indicador", "SINASC", "SINAN"])
indicadores = [
    ("Período", lambda d: d["anos"], "General"),
    ("Registros analisados", lambda d: f"='{d['aba_cons']}'!C5", "#,##0"),
    ("Variáveis analisadas", lambda d: f"=COUNTA('{d['aba_cons']}'!A5:A{d['fim_cons']})", "#,##0"),
    ("Variáveis críticas (>= 50%)", lambda d: f"=COUNTIF('{d['aba_cons']}'!I5:I{d['fim_cons']},\">=0.5\")", "#,##0"),
    ("Variáveis em atenção (20% a 49,9%)",
     lambda d: f"=COUNTIFS('{d['aba_cons']}'!I5:I{d['fim_cons']},\">=0.2\",'{d['aba_cons']}'!I5:I{d['fim_cons']},\"<0.5\")",
     "#,##0"),
    ("Variáveis completas (0%)", lambda d: f"=COUNTIF('{d['aba_cons']}'!I5:I{d['fim_cons']},0)", "#,##0"),
    ("Linhas 100% idênticas (excedentes)", lambda d: f"='{d['aba_dup']}'!F5", "#,##0"),
    ("% linhas 100% idênticas", lambda d: f"='{d['aba_dup']}'!G5", "0.0000%"),
    ("Excedentes no critério 3 (forte)", lambda d: f"='{d['aba_dup']}'!F7", "#,##0"),
    ("% excedentes no critério 3", lambda d: f"='{d['aba_dup']}'!G7", "0.0000%"),
    ("Excedentes no critério 4 (amplo)", lambda d: f"='{d['aba_dup']}'!F8", "#,##0"),
    ("% excedentes no critério 4", lambda d: f"='{d['aba_dup']}'!G8", "0.0000%"),
]
for i, (nome, f, fmt) in enumerate(indicadores, start=5):
    visao.cell(row=i, column=1, value=nome).font = F_NEG
    for j, d in enumerate(info, start=2):
        c = visao.cell(row=i, column=j, value=f(d))
        c.font, c.border, c.number_format = F_TXT, BORDA, fmt
        c.alignment = Alignment(horizontal="right")
nota = len(indicadores) + 6
visao.cell(row=nota, column=1, value="Critérios de duplicidade: no SINASC, 3 = mesmo RN (data/hora, sexo, peso, mãe); "
                                     "no SINAN, 3 = mesmo paciente (diagnóstico, sexo, raça, município, idade e "
                                     "escolaridade da mãe). No SINASC o critério 4 é dominado por gêmeos.").font = F_NOTA
larguras(visao, {"A": 38, "B": 16, "C": 16})

for s in wb.worksheets:
    s.sheet_view.showGridLines = False
wb.calculation.fullCalcOnLoad = True
wb.save(saida)
print(f"Excel salvo em: {saida}  ({len(wb.sheetnames)} abas)")
