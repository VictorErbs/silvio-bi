"""
=============================================================================
  SCRIPT DE ANALISE DE DADOS - BUSINESS INTELLIGENCE
  Infracoes de Transito - Recife 2025
  Disciplina: Business Intelligence
=============================================================================
  Este script realiza a carga, filtragem, analise e visualizacao dos
  dados de infracoes de transito da cidade do Recife/PE, fornecidos
  pela CTTU, respondendo as 5 perguntas do trabalho de BI.

   Autor: Grupo - Taísa Santiago, Victor Erbs, Caio Vrasack,
          Hiram Aguiar, Bruno da Silva, Bárbara Nolé
  Fonte: CTTU / Prefeitura do Recife
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
from datetime import datetime

# ============================================================================
# CONFIGURACOES INICIAIS
# ============================================================================

sns.set_style("whitegrid")
plt.rcParams.update({
    'figure.max_open_warning': 0,
    'font.size': 12,
    'axes.titleweight': 'bold',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
})

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "output")
TAB = os.path.join(OUT, "tabelas_analiticas")
os.makedirs(TAB, exist_ok=True)

MESES = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
DIA_SEMANA = {0:'Segunda',1:'Terca',2:'Quarta',3:'Quinta',4:'Sexta',5:'Sabado',6:'Domingo'}

print("=" * 70)
print("  INICIANDO ANALISE DE DADOS - BI")
print("=" * 70)

# ============================================================================
# 1. CARGA DOS DADOS
# ============================================================================

print("\n[1] Carregando dados...")

# Base real de infracoes (CTTU)
ARQUIVO_REAL = os.path.join(BASE,
    "resources_571dfcc2-9ab2-4cab-a69c-f1558d0f9898_registro-das-infracoes-de-transito-2025.csv")

df = pd.read_csv(ARQUIVO_REAL, sep=';', encoding='utf-8', low_memory=False)

# Converte colunas de data/hora
df['datainfracao'] = pd.to_datetime(df['datainfracao'])
df['horainfracao_dt'] = pd.to_datetime(df['horainfracao'], format='%H:%M:%S', errors='coerce')
df['hora'] = df['horainfracao_dt'].dt.hour
df['mes'] = df['datainfracao'].dt.month
df['dia_semana_num'] = df['datainfracao'].dt.dayofweek
df['dia_semana'] = df['dia_semana_num'].map(DIA_SEMANA)

# Dados complementares para Pergunta 5
df_condutor = pd.read_csv(os.path.join(BASE, 'dim_condutor.csv'))
df_infracoes = pd.read_csv(os.path.join(BASE, 'fact_infracoes.csv'))
df_sinistros = pd.read_csv(os.path.join(BASE, 'fact_sinistros.csv'))
df_q5_base = pd.read_csv(os.path.join(BASE, 'base_questao5_recusa_bafometro_sinistros.csv'))
df_grav_rec = pd.read_csv(os.path.join(BASE, 'analise_gravidade_recusa.csv'))

print(f"  >> Base real de infracoes: {len(df):,} registros")
print(f"  >> Periodo: {df['datainfracao'].min()} a {df['datainfracao'].max()}")
print(f"  >> Bases complementares carregadas: {len(df_q5_base):,} registros")


# ============================================================================
# 2. FILTRAGEM DOS DADOS POR PERGUNTA
# ============================================================================

print("\n[2] Filtrando dados por artigo do CTB...\n")

# --------------------------------------------------------------------------
# PERGUNTA 1 - Art. 164: Permitir conducao a pessoa sem CNH
# --------------------------------------------------------------------------
df_q1 = df[df['amparolegal'].str.contains('164', na=False, case=False)].copy()
print(f"  Q1 - Art. 164: {len(df_q1)} registros")
print(f"         Subtipos:")
for tipo, qtd in df_q1['descricaoinfracao'].value_counts().items():
    print(f"           - {tipo[:80]}: {qtd}")

# --------------------------------------------------------------------------
# PERGUNTA 2 - Art. 208: Avanco de sinal vermelho
# --------------------------------------------------------------------------
df_q2 = df[df['amparolegal'] == 'Art. 208'].copy()
print(f"\n  Q2 - Art. 208: {len(df_q2)} registros")
print(f"         Fiscalizacao por agente: {len(df_q2[df_q2['agenteequipamento'].str.contains('8', na=False)])}")
print(f"         Fiscalizacao por radar:  {len(df_q2[df_q2['agenteequipamento'].str.contains('5', na=False)])}")

# --------------------------------------------------------------------------
# PERGUNTA 3 - Art. 162, I: Conduzir sem CNH/PPD/ACC
# --------------------------------------------------------------------------
df_q3 = df[df['amparolegal'] == 'Art. 162, Inc. I'].copy()
print(f"\n  Q3 - Art. 162, I: {len(df_q3)} registros")
print(f"         Observacao: Base nao contem campo de tipo de veiculo")
print(f"         Analise realizada: evolucao mensal geral")

# --------------------------------------------------------------------------
# PERGUNTA 4 - Art. 165 vs Art. 165-A: Alcool e recusa ao bafometro
# --------------------------------------------------------------------------
df_q4 = df[df['amparolegal'].str.contains('165', na=False, case=False)].copy()
print(f"\n  Q4 - Art. 165 e 165-A: {len(df_q4)} registros")
print(f"         Art. 165 (Dirigir sob influencia): {len(df_q4[df_q4['amparolegal']=='Art. 165'])}")
print(f"         Art. 165-A (Recusa ao bafometro): {len(df_q4[df_q4['amparolegal']=='Art. 165-A'])}")

# --------------------------------------------------------------------------
# PERGUNTA 5 - Recusa ao bafometro vs sinistros
# --------------------------------------------------------------------------
df_q5_recusas = df_q5_base[df_q5_base['tipo_evento'] == 'MULTA_165A_RECUSA_BAFOMETRO']
df_q5_sinistros = df_q5_base[df_q5_base['tipo_evento'] == 'SINISTRO_TRANSITO']
print(f"\n  Q5 - Recusa vs Sinistros:")
print(f"         Registros de recusa: {len(df_q5_recusas)}")
print(f"         Registros de sinistros: {len(df_q5_sinistros)}")


# ============================================================================
# 3. ANALISE DESCRITIVA E AGREGACOES
# ============================================================================

print("\n[3] Executando analises...\n")

# ----------------------------------------------------------
# Q1: Volume mensal e dia da semana - Art. 164
# ----------------------------------------------------------
q1_mensal = df_q1.groupby('mes').size()
q1_dia = df_q1.groupby('dia_semana').size().reindex(
    ['Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo'], fill_value=0)

print("  Q1 - Volume Mensal (Art. 164):")
for mes in sorted(q1_mensal.index):
    print(f"    {MESES[mes]:>5}: {q1_mensal[mes]:>3} infracoes ({q1_mensal[mes]/len(df_q1)*100:5.1f}%)")

print("\n  Q1 - Por Dia da Semana:")
for dia in q1_dia.index:
    print(f"    {dia:>8}: {q1_dia[dia]:>3} infracoes ({q1_dia[dia]/len(df_q1)*100:5.1f}%)")

# ----------------------------------------------------------
# Q2: Distribuicao horaria, local e tipo de fiscalizacao - Art. 208
# ----------------------------------------------------------
q2_hora = df_q2.groupby('hora').size()
q2_equip = df_q2['agenteequipamento'].value_counts()
q2_top10_local = df_q2['localcometimento'].value_counts().head(10)

pico_hora = q2_hora.idxmax()
print(f"\n  Q2 - Pico horario: {pico_hora:02d}h ({q2_hora[pico_hora]} registros)")
print(f"  Q2 - Principal local: {q2_top10_local.index[0][:70]} ({q2_top10_local.iloc[0]} registros)")

# ----------------------------------------------------------
# Q3: Evolucao mensal - Art. 162, I
# ----------------------------------------------------------
q3_mensal = df_q3.groupby('mes').size()
coef_tendencia = np.polyfit(sorted(q3_mensal.index), [q3_mensal[m] for m in sorted(q3_mensal.index)], 1)[0]
print(f"\n  Q3 - Tendencia linear: {coef_tendencia:+.2f} registros/mes")

# ----------------------------------------------------------
# Q4: Comparacao Art. 165 vs Art. 165-A por faixa horaria
# ----------------------------------------------------------
def bucket(h):
    if h < 6: return 'Madrugada (0h-6h)'
    elif h < 12: return 'Manha (6h-12h)'
    elif h < 18: return 'Tarde (12h-18h)'
    else: return 'Noite (18h-24h)'

df_q4_165 = df_q4[df_q4['amparolegal'] == 'Art. 165'].copy()
df_q4_165a = df_q4[df_q4['amparolegal'] == 'Art. 165-A'].copy()
df_q4_165['faixa'] = df_q4_165['hora'].apply(bucket)
df_q4_165a['faixa'] = df_q4_165a['hora'].apply(bucket)

print(f"\n  Q4 - Art. 165-A concentracao noturna: "
      f"{(df_q4_165a['faixa']=='Noite (18h-24h)').sum()}/{len(df_q4_165a)} registros")

# ----------------------------------------------------------
# Q5: Correlacao recusa vs sinistros
# ----------------------------------------------------------
cond_recusa = df_q5_recusas['cpf_condutor'].unique()
cond_sinistro = df_q5_sinistros['cpf_condutor'].unique()
cond_ambos = set(cond_recusa) & set(cond_sinistro)

print(f"\n  Q5 - Condutores com recusa: {len(cond_recusa)}")
print(f"  Q5 - Condutores com sinistro: {len(cond_sinistro)}")
print(f"  Q5 - Condutores com ambos: {len(cond_ambos)} ({len(cond_ambos)/len(cond_recusa)*100:.1f}%)")

# Cruzamento com dados de reincidencia (CTTU)
recusas_ids = df_infracoes[df_infracoes['codigo_ctb'] == '165-A']['id_condutor'].unique()
nao_recusas_ids = df_condutor[~df_condutor['id_condutor'].isin(recusas_ids)]['id_condutor'].unique()
sin_com_recusa = df_sinistros[df_sinistros['id_condutor'].isin(recusas_ids)]['id_condutor'].nunique()
sin_sem_recusa = df_sinistros[~df_sinistros['id_condutor'].isin(recusas_ids)]['id_condutor'].nunique()

taxa_rec = sin_com_recusa / len(recusas_ids) * 100
taxa_nao = sin_sem_recusa / len(nao_recusas_ids) * 100
risco = taxa_rec / taxa_nao if taxa_nao > 0 else 0

print(f"\n  Q5 - Risco Relativo: {risco:.2f}x")
print(f"         Condutores que recusaram: {taxa_rec:.1f}% com sinistros")
print(f"         Condutores sem recusa: {taxa_nao:.1f}% com sinistros")


# ============================================================================
# 4. GERACAO DE GRAFICOS
# ============================================================================

print("\n[4] Gerando graficos...")

# --------------------------------------------------------------------------
# GRAFICO Q1 - Art. 164
# --------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
fig.suptitle('Q1 - Art. 164: Permitir Conducao a Pessoa sem CNH/PPD/ACC', fontsize=14, fontweight='bold', y=1.02)

# Grafico 1: Volume Mensal
ax1 = axes[0]
cores_mes = sns.color_palette("rocket", len(q1_mensal))
ax1.bar([MESES[m] for m in q1_mensal.index], q1_mensal.values,
        color=cores_mes, edgecolor='#2c3e50', linewidth=1.2, width=0.65)
ylim_max1 = max(q1_mensal.values) * 1.25
ax1.set_ylim(0, ylim_max1)
for i, (mes, v) in enumerate(sorted(q1_mensal.items())):
    ax1.text(i, v + ylim_max1 * 0.03, str(v),
            ha='center', va='bottom', fontweight='bold', fontsize=11, color='#2c3e50')
ax1.set_title('Volume Mensal de Infracoes', fontsize=12, fontweight='bold')
ax1.set_xlabel('Mes')
ax1.set_ylabel('Quantidade de Infracoes')
ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax1.text(0.5, -0.1, 'Fonte: CTTU / Registro de Infracoes 2025', transform=ax1.transAxes, ha='center', fontsize=8, style='italic', color='#888')

# Grafico 2: Dia da Semana
ax2 = axes[1]
cores_dia = ['#3498db' if v == max(q1_dia.values) else '#95a5a6' for v in q1_dia.values]
ax2.bar(q1_dia.index, q1_dia.values, color=cores_dia, edgecolor='#2c3e50', linewidth=1.2, width=0.65)
ylim_max2 = max(q1_dia.values) * 1.25
ax2.set_ylim(0, ylim_max2)
for i, (dia, v) in enumerate(q1_dia.items()):
    ax2.text(i, v + ylim_max2 * 0.03, str(v),
            ha='center', va='bottom', fontweight='bold', fontsize=11, color='#2c3e50')
ax2.set_title('Distribuicao por Dia da Semana', fontsize=12, fontweight='bold')
ax2.set_xlabel('Dia da Semana')
ax2.set_ylabel('Quantidade de Infracoes')
ax2.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax2.text(0.5, -0.1, 'Fonte: CTTU / Registro de Infracoes 2025', transform=ax2.transAxes, ha='center', fontsize=8, style='italic', color='#888')

plt.subplots_adjust(bottom=0.15, wspace=0.25)
plt.savefig(os.path.join(OUT, 'grafico_q1_art164.png'), dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print("  >> grafico_q1_art164.png")

# --------------------------------------------------------------------------
# GRAFICO Q2 - Art. 208
# --------------------------------------------------------------------------
fig = plt.figure(figsize=(16, 10), facecolor='white')
fig.suptitle('Q2 - Art. 208: Avanco de Sinal Vermelho - Analise Completa', fontsize=15, fontweight='bold', y=1.01)

# Grafico 1: Distribuicao Horaria
ax1 = fig.add_subplot(2, 2, 1)
horas = range(24)
vals_hora = [q2_hora.get(h, 0) for h in horas]
cores_h = ['#e74c3c' if 7 <= h <= 9 or 17 <= h <= 18 else '#3498db' for h in horas]
ax1.bar(horas, vals_hora, color=cores_h, edgecolor='white', linewidth=0.8, width=0.8)
for h in [8, 7, 11, 9, 12]:
    v = q2_hora.get(h, 0)
    ax1.text(h, v + 8, str(v), ha='center', fontweight='bold', fontsize=8, color='#2c3e50')
ax1.set_title('Distribuicao Horaria (pico em vermelho)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Hora do Dia')
ax1.set_ylabel('Quantidade')
ax1.set_xticks(range(0, 24, 2))
ax1.text(0.5, -0.12, 'Fonte: CTTU / Registro de Infracoes 2025', transform=ax1.transAxes, ha='center', fontsize=8, style='italic', color='#888')

# Grafico 2: Pizza Agente vs Radar
ax2 = fig.add_subplot(2, 2, 2)
cores_pizza = ['#e67e22', '#2ecc71', '#95a5a6']
labels_pizza = ['AGENTE\n(Talao Eletronico)', 'RADAR\n(Foto Sensor)', 'Nao Identificado']
vals_pizza = [
    q2_equip.get('C\u00f3digo 8 - AUTOS NO TAL\u00c3O ELETR\u00d4NICO', 0),
    q2_equip.get('C\u00f3digo 5 - FOTO SENSOR', 0),
    len(df_q2) - q2_equip.sum()
]
vals_pizza = [v for v in vals_pizza if v > 0]
labels_pizza = [labels_pizza[i] for i, v in enumerate(vals_pizza) if v > 0]
wedges, texts, autotexts = ax2.pie(
    vals_pizza, labels=labels_pizza, autopct='%1.1f%%',
    colors=cores_pizza[:len(vals_pizza)], startangle=90,
    textprops={'fontsize': 10}, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
for t in autotexts:
    t.set_fontweight('bold')
    t.set_color('white')
ax2.set_title('Distribuicao: Agente vs Radar', fontsize=12, fontweight='bold')

# Grafico 3: Top 10 Locais
ax3 = fig.add_subplot(2, 2, (3, 4))
locais_short = [l[:65] + '...' if len(l) > 65 else l for l in q2_top10_local.index[::-1]]
cores_barh = sns.color_palette("YlOrRd", len(q2_top10_local))[::-1]
ax3.barh(locais_short, q2_top10_local.values[::-1], color=cores_barh, edgecolor='white', linewidth=0.8, height=0.7)
ax3.set_title('Top 10 Locais com Maior Incidencia', fontsize=12, fontweight='bold')
ax3.set_xlabel('Quantidade de Infracoes')
for i, v in enumerate(q2_top10_local.values[::-1]):
    ax3.text(v + 5, i, str(v), va='center', fontsize=9, fontweight='bold', color='#2c3e50')
ax3.text(0.5, -0.12, 'Fonte: CTTU / Registro de Infracoes 2025', transform=ax3.transAxes, ha='center', fontsize=8, style='italic', color='#888')

plt.tight_layout()
plt.savefig(os.path.join(OUT, 'grafico_q2_art208.png'), dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("  >> grafico_q2_art208.png")

# --------------------------------------------------------------------------
# GRAFICO Q3 - Art. 162, I
# --------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5), facecolor='white')
fig.suptitle('Q3 - Art. 162, I: Conduzir sem CNH/PPD/ACC - Evolucao Mensal', fontsize=14, fontweight='bold', y=1.02)

meses_nomes = [MESES[m] for m in sorted(q3_mensal.index)]
vals_q3 = [q3_mensal[m] for m in sorted(q3_mensal.index)]

ax.plot(meses_nomes, vals_q3, marker='o', linewidth=3, color='#8e44ad',
        markersize=10, markerfacecolor='white', markeredgewidth=2.5, zorder=5)
ax.fill_between(range(len(vals_q3)), vals_q3, alpha=0.12, color='#8e44ad')

for i, v in enumerate(vals_q3):
    ax.annotate(str(v), (i, v), textcoords="offset points", xytext=(0, 14),
               ha='center', fontweight='bold', fontsize=11, color='#8e44ad')

ax.set_xlabel('Mes (2025)')
ax.set_ylabel('Quantidade de Infracoes')
ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.set_ylim(0, max(vals_q3) * 1.25)
ax.set_xticks(range(len(meses_nomes)))
ax.set_xticklabels(meses_nomes)
ax.text(0.5, -0.15, 'Nota: Dados nao permitem segmentacao por tipo de veiculo (eletrico vs combustao)',
        transform=ax.transAxes, ha='center', fontsize=9, style='italic', color='#888')
ax.text(0.5, -0.22, 'Fonte: CTTU / Registro de Infracoes 2025',
        transform=ax.transAxes, ha='center', fontsize=8, style='italic', color='#aaa')

plt.tight_layout()
plt.savefig(os.path.join(OUT, 'grafico_q3_art162.png'), dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("  >> grafico_q3_art162.png")

# --------------------------------------------------------------------------
# GRAFICO Q4 - Art. 165 vs 165-A
# --------------------------------------------------------------------------
faixas_ord = ['Madrugada (0h-6h)', 'Manha (6h-12h)', 'Tarde (12h-18h)', 'Noite (18h-24h)']
q4_165_f = df_q4_165.groupby('faixa').size().reindex(faixas_ord, fill_value=0)
q4_165a_f = df_q4_165a.groupby('faixa').size().reindex(faixas_ord, fill_value=0)

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor='white')
fig.suptitle('Q4 - Art. 165 (Alcool) vs Art. 165-A (Recusa Bafometro)', fontsize=14, fontweight='bold', y=1.02)

ax1 = axes[0]
x = np.arange(len(faixas_ord))
w = 0.32
bars_a = ax1.bar(x - w/2, q4_165_f.values, w, label='Art. 165 (Alcool)',
                 color='#e74c3c', edgecolor='white', linewidth=1.2)
bars_b = ax1.bar(x + w/2, q4_165a_f.values, w, label='Art. 165-A (Recusa)',
                 color='#f39c12', edgecolor='white', linewidth=1.2)
for bar in bars_a:
    if bar.get_height() > 0:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                str(int(bar.get_height())), ha='center', fontweight='bold', fontsize=10)
for bar in bars_b:
    if bar.get_height() > 0:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                str(int(bar.get_height())), ha='center', fontweight='bold', fontsize=10)
ax1.set_xticks(x)
ax1.set_xticklabels(faixas_ord, rotation=12)
ax1.set_ylabel('Quantidade')
ax1.set_title('Distribuicao por Faixa Horaria', fontsize=12, fontweight='bold')
ax1.legend(frameon=True, fancybox=True)
ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax1.text(0.5, -0.15, 'Fonte: CTTU / Registro de Infracoes 2025',
        transform=ax1.transAxes, ha='center', fontsize=8, style='italic', color='#888')

# Grafico de dispersao por hora
ax2 = axes[1]
q4_hora_165 = df_q4_165.groupby('hora').size()
q4_hora_165a = df_q4_165a.groupby('hora').size()
horas_all = sorted(set(list(q4_hora_165.index) + list(q4_hora_165a.index)))
vals165_h = [q4_hora_165.get(h, 0) for h in horas_all]
vals165a_h = [q4_hora_165a.get(h, 0) for h in horas_all]

ax2.scatter(horas_all, vals165_h, color='#e74c3c', s=140, label='Art. 165',
           zorder=5, edgecolor='white', linewidth=1.5)
ax2.scatter(horas_all, vals165a_h, color='#f39c12', s=140, label='Art. 165-A',
           zorder=5, edgecolor='white', linewidth=1.5, marker='s')
for h, v in zip(horas_all, vals165_h):
    if v > 0:
        ax2.annotate(str(v), (h, v), textcoords="offset points", xytext=(0,10),
                    ha='center', fontsize=9, fontweight='bold')
for h, v in zip(horas_all, vals165a_h):
    if v > 0:
        ax2.annotate(str(v), (h, v), textcoords="offset points", xytext=(0,10),
                    ha='center', fontsize=9, fontweight='bold')
ax2.set_xlabel('Hora do Dia')
ax2.set_ylabel('Quantidade')
ax2.set_title('Distribuicao por Hora Especifica', fontsize=12, fontweight='bold')
ax2.set_xticks(range(0, 24, 2))
ax2.legend(frameon=True, fancybox=True)
ax2.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

plt.tight_layout()
plt.savefig(os.path.join(OUT, 'grafico_q4_art165_165a.png'), dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("  >> grafico_q4_art165_165a.png")

# --------------------------------------------------------------------------
# GRAFICO Q5 - Recusa vs Sinistros
# --------------------------------------------------------------------------
sinistros_rec = df_sinistros[df_sinistros['id_condutor'].isin(recusas_ids)]
sinistros_nao_rec = df_sinistros[~df_sinistros['id_condutor'].isin(recusas_ids)]
q5_com_dias = df_q5_base.dropna(subset=['dias_apos_recusa'])

fig = plt.figure(figsize=(16, 10), facecolor='white')
fig.suptitle('Q5 - Relacao entre Recusa ao Bafometro e Sinistros de Transito', fontsize=15, fontweight='bold', y=1.01)

# Grafico 1: Taxa de sinistros
ax1 = fig.add_subplot(2, 2, 1)
dados_bar = pd.DataFrame({
    'Grupo': ['Recusaram Bafometro', 'Nao Recusaram'],
    'Taxa de Sinistros (%)': [taxa_rec, taxa_nao]
})
bars = ax1.bar(dados_bar['Grupo'], dados_bar['Taxa de Sinistros (%)'],
               color=['#e74c3c', '#3498db'], edgecolor='white', linewidth=1.5, width=0.5)
for bar, v in zip(bars, dados_bar['Taxa de Sinistros (%)']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{v:.1f}%', ha='center', fontweight='bold', fontsize=13, color='#2c3e50')
ax1.set_title('Taxa de Condutores com Sinistros', fontsize=12, fontweight='bold')
ax1.set_ylabel('Percentual (%)')
ax1.set_ylim(0, max(taxa_rec, taxa_nao) * 1.25)
ax1.text(0.5, -0.15, 'Fonte: CTTU / Base de Infracoes e Sinistros',
        transform=ax1.transAxes, ha='center', fontsize=8, style='italic', color='#888')

# Grafico 2: Histograma de dias entre recusa e sinistro
ax2 = fig.add_subplot(2, 2, 2)
if len(q5_com_dias) > 0:
    ax2.hist(q5_com_dias['dias_apos_recusa'], bins=20, color='#e67e22',
             edgecolor='white', linewidth=0.8, alpha=0.85)
    ax2.axvline(q5_com_dias['dias_apos_recusa'].mean(), color='#c0392b',
                linestyle='--', linewidth=2.5, label=f"Media: {q5_com_dias['dias_apos_recusa'].mean():.0f} dias")
    ax2.axvline(q5_com_dias['dias_apos_recusa'].median(), color='#27ae60',
                linestyle=':', linewidth=2.5, label=f"Mediana: {q5_com_dias['dias_apos_recusa'].median():.0f} dias")
    ax2.set_title('Distribuicao: Dias entre Recusa e Sinistro', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Dias apos Recusa')
    ax2.set_ylabel('Frequencia')
    ax2.legend(frameon=True, fancybox=True)

# Grafico 3: Gravidade dos sinistros
ax3 = fig.add_subplot(2, 2, 3)
todas_grav = ['Leve', 'Grave', 'Fatal']
sin_rec_grav = sinistros_rec['gravidade'].value_counts()
sin_nao_grav = sinistros_nao_rec['gravidade'].value_counts()
grav_comparison = pd.DataFrame({
    'Gravidade': todas_grav,
    'Com Recusa': [sin_rec_grav.get(g, 0) for g in todas_grav],
    'Sem Recusa': [sin_nao_grav.get(g, 0) for g in todas_grav]
})
x = np.arange(len(todas_grav))
w = 0.32
bars_c = ax3.bar(x - w/2, grav_comparison['Com Recusa'], w, label='Recusaram Bafometro',
                color='#e74c3c', edgecolor='white', linewidth=1.2)
bars_s = ax3.bar(x + w/2, grav_comparison['Sem Recusa'], w, label='Nao Recusaram',
                color='#3498db', edgecolor='white', linewidth=1.2)
for bar in bars_c:
    if bar.get_height() > 0:
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                str(int(bar.get_height())), ha='center', fontweight='bold', fontsize=9, color='#e74c3c')
for bar in bars_s:
    if bar.get_height() > 0:
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                str(int(bar.get_height())), ha='center', fontweight='bold', fontsize=9, color='#3498db')
ax3.set_xticks(x)
ax3.set_xticklabels(todas_grav)
ax3.set_title('Gravidade dos Sinistros por Grupo', fontsize=12, fontweight='bold')
ax3.set_ylabel('Quantidade')
ax3.legend(frameon=True, fancybox=True)
ax3.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# Grafico 4: Causas de sinistros
ax4 = fig.add_subplot(2, 2, 4)
causas = sinistros_rec['causa_provavel'].value_counts()
cores_causa = sns.color_palette("Set2", len(causas))
wedges, texts, autotexts = ax4.pie(
    causas.values,
    labels=[f"{c.split(' ')[0] if len(c.split()) > 1 else c}\n({v})" for c, v in zip(causas.index, causas.values)],
    autopct='%1.1f%%', colors=cores_causa, startangle=90,
    textprops={'fontsize': 9}, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
for t in autotexts:
    t.set_fontweight('bold')
ax4.set_title('Causas de Sinistros (Condutores com Recusa)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(OUT, 'grafico_q5_recusa_sinistro.png'), dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("  >> grafico_q5_recusa_sinistro.png")


# ============================================================================
# 5. EXPORTACAO DE TABELAS ANALITICAS
# ============================================================================

print("\n[5] Exportando tabelas analiticas...")

q1_mensal.to_csv(os.path.join(TAB, 'q1_art164_mensal.csv'), header=['quantidade'])
q1_dia.to_csv(os.path.join(TAB, 'q1_art164_dia_semana.csv'), header=['quantidade'])
q2_hora.to_csv(os.path.join(TAB, 'q2_art208_hora.csv'), header=['quantidade'])
q2_equip.to_csv(os.path.join(TAB, 'q2_art208_agente_radar.csv'), header=['quantidade'])
q2_top10_local.to_csv(os.path.join(TAB, 'q2_art208_top10_locais.csv'), header=['quantidade'])
q3_mensal.to_csv(os.path.join(TAB, 'q3_art162_mensal.csv'), header=['quantidade'])
q4_165_f.to_csv(os.path.join(TAB, 'q4_art165_faixas.csv'), header=['quantidade'])
q4_165a_f.to_csv(os.path.join(TAB, 'q4_art165a_faixas.csv'), header=['quantidade'])

pd.DataFrame({
    'Grupo': ['Recusaram Bafometro', 'Nao Recusaram'],
    'Total Condutores': [len(recusas_ids), len(nao_recusas_ids)],
    'Com Sinistro': [sin_com_recusa, sin_sem_recusa],
    'Taxa (%)': [round(taxa_rec, 2), round(taxa_nao, 2)]
}).to_csv(os.path.join(TAB, 'q5_taxa_sinistros.csv'), index=False)

grav_comparison.to_csv(os.path.join(TAB, 'q5_gravidade_comparacao.csv'), index=False)

if len(q5_com_dias) > 0:
    q5_com_dias['dias_apos_recusa'].describe().to_csv(os.path.join(TAB, 'q5_dias_estatisticas.csv'))

print("  >> 11 tabelas exportadas para output/tabelas_analiticas/")


# ============================================================================
# RESUMO FINAL
# ============================================================================

print("\n" + "=" * 70)
print("  ANALISE CONCLUIDA COM SUCESSO!")
print("=" * 70)
print(f"\n  Resumo:")
print(f"    Q1 - Art. 164: {len(df_q1)} registros analisados")
print(f"    Q2 - Art. 208: {len(df_q2)} registros analisados")
print(f"    Q3 - Art. 162, I: {len(df_q3)} registros analisados")
print(f"    Q4 - Art. 165 vs 165-A: {len(df_q4)} registros analisados")
print(f"    Q5 - Recusa vs Sinistros: {len(df_q5_base):,} registros analisados")
print(f"\n  Graficos gerados: 5")
print(f"  Tabelas exportadas: 11")
print(f"\n  Outputs salvos em: {OUT}/")
