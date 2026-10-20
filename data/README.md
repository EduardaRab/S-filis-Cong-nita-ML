# data/

Dados do projeto, separados por estágio. **Nenhum arquivo de dados é versionado no Git** (ver `.gitignore`); só esta explicação e os `.gitkeep` que mantêm as pastas.

| Pasta | Conteúdo | Quem grava |
|---|---|---|
| `raw/` | Dados originais do DATASUS, sem nenhuma alteração: `DNSP2015.csv` … `DNSP2024.csv` (SINASC, só SP) e `SIFCBR15.csv` … `SIFCBR25.csv` (SINAN sífilis congênita, Brasil). Também os `.dbc` baixados do FTP, se houver. | Download manual (seção 6.2 da documentação técnica) |
| `processed/` | Dados tratados pelo pipeline: limpos, padronizados, integrados e prontos para modelagem (preferência por Parquet). | Pipeline em `src/` (frente da Eduarda) |
| `outputs/` | Resultados gerados: métricas dos experimentos, modelos treinados, tabelas e figuras de avaliação, relatórios de completude. | Modelagem e análises (frentes do Lucas e da Ester) |

Regras:

- **`raw/` é somente leitura.** Nunca edite nem sobrescreva os arquivos originais; qualquer correção vai para `processed/`.
- Registre a **data do download** dos arquivos de `raw/` (o SINAN é preliminar e muda entre downloads).
- Contagens de referência para conferir a leitura estão na seção 6.1 da [documentação técnica](../DOCUMENTACAO_TECNICA.md#61-perfil-real-dos-dados-verificado-nos-arquivos).
