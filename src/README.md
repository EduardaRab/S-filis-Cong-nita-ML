# src/

Código-fonte Python do projeto. Organização prevista (seção 13 da [documentação técnica](../DOCUMENTACAO_TECNICA.md#13-estrutura-de-repositório-e-organização-de-arquivos)):

| Subpasta | Conteúdo | Frente |
|---|---|---|
| `pipeline/` | Extração, transformação e carga (lê `data/raw/`, grava `data/processed/`) | Eduarda |
| `modeling/` | Treino, avaliação e interpretabilidade dos modelos (lê `data/processed/` e `config/`, grava `data/outputs/`) | Lucas |
| `shared/` | Utilitários comuns (leitura dos CSVs, schemas, logging) | Todos |

Nenhum código foi implementado ainda.
