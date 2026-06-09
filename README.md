# 🚦 Dashboard BI — Infrações de Trânsito Recife 2025

Dashboard interativo de Business Intelligence para análise de **171.109 infrações reais de trânsito** registradas pela **CTTU / Prefeitura do Recife** entre janeiro e maio de 2025.

## 📊 Visão Geral

| Indicador | Valor |
|---|---|
| Registros processados | 171.109 |
| Período analisado | Jan–Mai 2025 |
| Perguntas respondidas | 5 |
| Gráficos gerados | 5 |
| Tabelas analíticas | 11 |

## 📋 Perguntas Analisadas

| # | Artigo | Tema | Registros |
|---|---|---|---|
| 1 | Art. 164 | Permitir condução a pessoa sem CNH/PPD/ACC | 172 |
| 2 | Art. 208 | Avanço de sinal vermelho | 3.479 |
| 3 | Art. 162, I | Conduzir sem CNH/PPD/ACC | 304 |
| 4 | Art. 165 / 165-A | Álcool vs recusa ao bafômetro | 22 |
| 5 | Art. 165-A | Recusa ao bafômetro × sinistros | 1.654 |

## 🗂️ Estrutura

```
silvio-bi/
├── output/
│   ├── dashboard_bi.html          # Dashboard completo (abrir no navegador)
│   ├── grafico_q1_art164.png      # Gráficos por pergunta
│   ├── grafico_q2_art208.png
│   ├── grafico_q3_art162.png
│   ├── grafico_q4_art165_165a.png
│   ├── grafico_q5_recusa_sinistro.png
│   ├── relatorio_completo.txt     # Relatório textual completo
│   └── tabelas_analiticas/        # 11 CSVs com dados consolidados
├── script_analise_bi.py           # Script principal (apresentável)
├── analise_completa_bi.py         # Script completo com todas as análises
├── analise_bi_pergunta5.py        # Análise focada na pergunta 5
└── Perguntas.pdf                  # Enunciado das perguntas
```

## 🚀 Como Usar

1. Abra `output/dashboard_bi.html` em qualquer navegador moderno
2. Para reprocessar as análises:

```bash
pip install pandas numpy matplotlib seaborn
python script_analise_bi.py
```

## 🛠️ Tecnologias

- **Python** — Pandas, NumPy, Matplotlib, Seaborn
- **HTML/CSS** — Dashboard responsivo (mobile 480px → 1080p)
- **CTTU** — Dados oficiais da autarquia de trânsito do Recife

## 👥 Grupo

Taísa Santiago · Victor Erbs · Caio Vrasack · Hiram Aguiar · Bruno da Silva · Bárbara Nolé

---

<p align="center">Dashboard gerado em junho de 2026 — Trabalho de Business Intelligence</p>
