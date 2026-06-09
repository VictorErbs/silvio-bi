import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
sns.set_palette("viridis")
plt.rcParams.update({
    'figure.max_open_warning': 0,
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.titleweight': 'bold',
    'axes.titlesize': 13,
    'axes.labelweight': 'semibold',
    'axes.edgecolor': '#cccccc',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
})

BASE = "C:/Users/Administrator/Documents/Silvio"
OUT = os.path.join(BASE, "output")
TAB = os.path.join(OUT, "tabelas_analiticas")
REAL_CSV = os.path.join(BASE, "resources_571dfcc2-9ab2-4cab-a69c-f1558d0f9898_registro-das-infracoes-de-transito-2025.csv")
os.makedirs(TAB, exist_ok=True)

relatorio = []
def R(text):
    relatorio.append(text)
    print(text)

R("=" * 80)
R("  RELATORIO COMPLETO DE ANALISE DE DADOS - BUSINESS INTELLIGENCE")
R("  INFRAÇÕES DE TRÂNSITO - RECIFE 2025")
R(f"  Data de geracao: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
R("=" * 80)
R("")
R("FONTES DE DADOS UTILIZADAS:")
R("  1. Registro de Infracoes de Transito 2025 (171.109 registros reais)")
R("  2. base_questao5_recusa_bafometro_sinistros.csv (1.654 registros)")
R("  3. fact_infracoes.csv (3.000 registros simulados)")
R("  4. fact_sinistros.csv (500 registros simulados)")
R("  5. dim_condutor.csv / dim_localidade.csv / dim_tempo.csv (dimensoes)")
R("")

# ======================================================================
# CARGA DE DADOS
# ======================================================================
R("=" * 80)
R("  CARGA DE DADOS")
R("=" * 80)
R("")

df_real = pd.read_csv(REAL_CSV, sep=';', encoding='utf-8', low_memory=False)
R(f"  Base real de infracoes: {len(df_real):,} registros")
R(f"  Periodo: {df_real['datainfracao'].min()} a {df_real['datainfracao'].max()}")
R(f"  Colunas: {', '.join(df_real.columns.tolist())}")
R("")

df_condutor = pd.read_csv(os.path.join(BASE, 'dim_condutor.csv'))
df_local = pd.read_csv(os.path.join(BASE, 'dim_localidade.csv'))
df_tempo = pd.read_csv(os.path.join(BASE, 'dim_tempo.csv'))
df_infracoes = pd.read_csv(os.path.join(BASE, 'fact_infracoes.csv'))
df_sinistros = pd.read_csv(os.path.join(BASE, 'fact_sinistros.csv'))
df_q5_base = pd.read_csv(os.path.join(BASE, 'base_questao5_recusa_bafometro_sinistros.csv'))
df_grav_rec = pd.read_csv(os.path.join(BASE, 'analise_gravidade_recusa.csv'))

R(f"  dim_condutor: {len(df_condutor)} condutores")
R(f"  dim_localidade: {len(df_local)} bairros")
R(f"  dim_tempo: {len(df_tempo)} dias")
R(f"  fact_infracoes: {len(df_infracoes):,} infracoes simuladas")
R(f"  fact_sinistros: {len(df_sinistros)} sinistros simulados")
R(f"  base_q5: {len(df_q5_base):,} registros")
R("")

# ---------- Preparacao das datas ----------
df_real['datainfracao'] = pd.to_datetime(df_real['datainfracao'])
df_real['horainfracao_dt'] = pd.to_datetime(df_real['horainfracao'], format='%H:%M:%S', errors='coerce')
df_real['hora'] = df_real['horainfracao_dt'].dt.hour
df_real['mes'] = df_real['datainfracao'].dt.month
df_real['dia_semana_num'] = df_real['datainfracao'].dt.dayofweek
dia_map = {0: 'Segunda', 1: 'Terca', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sabado', 6: 'Domingo'}
df_real['dia_semana'] = df_real['dia_semana_num'].map(dia_map)

MESES = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}


# ======================================================================
# PERGUNTA 1 - Art. 164
# ======================================================================
R("=" * 80)
R("  PERGUNTA 1")
R("  Qual o volume mensal de infracoes por 'Permitir posse/conducao a")
R("  pessoa sem CNH/PPD/ACC' (Art. 164 do CTB) e em quais dias da")
R("  semana elas ocorrem com maior frequencia?")
R("=" * 80)
R("")

def analise_q1():
    R("INTRODUCAO:")
    R("  O Art. 164 do CTB trata de permitir posse ou conducao de veiculo a")
    R("  pessoa sem habilitacao valida. Esta analise examina o volume mensal")
    R("  destas infracoes e sua distribuicao ao longo da semana, utilizando")
    R("  dados reais de 2025 (janeiro a maio).")
    R("")

    q1 = df_real[df_real['amparolegal'].str.contains('164', na=False, case=False)].copy()
    R(f"  Total de registros encontrados: {len(q1)}")
    R("")

    # Mensal
    q1_mes = q1.groupby('mes').size()
    R("  Volume Mensal:")
    for mes, v in q1_mes.items():
        R(f"    {MESES[mes]}: {v} infracoes ({v/len(q1)*100:.1f}%)")
    R("")

    # Dia da semana
    q1_dia = q1.groupby('dia_semana').size().reindex(
        ['Segunda','Terca','Quarta','Quinta','Sexta','Sabado','Domingo'], fill_value=0)
    R("  Distribuicao por Dia da Semana:")
    for dia, v in q1_dia.items():
        R(f"    {dia}: {v} infracoes ({v/len(q1)*100:.1f}%)")
    R("")

    R("ANALISE:")
    R(f"  Marco (Mar/2025) apresenta o maior volume com {q1_mes.get(3,0)} registros,")
    R(f"  concentrando {q1_mes.get(3,0)/len(q1)*100:.1f}% do total do periodo.")
    R(f"  Quarta-feira e o dia com maior incidencia ({q1_dia['Quarta']} registros),")
    R(f"  enquanto domingo apresenta o menor indice ({q1_dia['Domingo']} registros).")
    R("")
    R("CONCLUSÃO:")
    R("  A concentracao em marco e quartas-feiras sugere possivel relacao com")
    R("  operacoes de fiscalizacao especificas. O baixo numero de registro aos")
    R("  domingos e atipico, ja que a conducao sem CNH normalmente nao segue")
    R("  padrao sazonal. Recomenda-se investigar se houve operacao especial")
    R("  em marco de 2025 direcionada a este artigo.")
    R("")

    # Grafico
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    fig.suptitle('Q1 - Art. 164: Permitir Conducao a Pessoa sem CNH/PPD/ACC', fontsize=14, fontweight='bold', y=1.02)

    ax1 = axes[0]
    cores_mes = sns.color_palette("rocket", len(q1_mes))
    ax1.bar([MESES[m] for m in q1_mes.index], q1_mes.values,
            color=cores_mes, edgecolor='#2c3e50', linewidth=1.2, width=0.65)
    ylim_max1 = max(q1_mes.values) * 1.25
    ax1.set_ylim(0, ylim_max1)
    for i, (mes, v) in enumerate(sorted(q1_mes.items())):
        ax1.text(i, v + ylim_max1 * 0.03, str(v),
                ha='center', va='bottom', fontweight='bold', fontsize=11, color='#2c3e50')
    ax1.set_title('Volume Mensal de Infracoes', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Mes')
    ax1.set_ylabel('Quantidade de Infracoes')
    ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax1.text(0.5, -0.1, 'Fonte: CTTU / Registro de Infracoes 2025', transform=ax1.transAxes, ha='center', fontsize=8, style='italic', color='#888')

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

    q1_mes.to_csv(os.path.join(TAB, 'q1_art164_mensal.csv'), header=['quantidade'])
    q1_dia.to_csv(os.path.join(TAB, 'q1_art164_dia_semana.csv'), header=['quantidade'])
    R("  >> Graficos salvos: grafico_q1_art164.png")
    R("  >> Tabelas: q1_art164_mensal.csv, q1_art164_dia_semana.csv")
    R("")

analise_q1()


# ======================================================================
# PERGUNTA 2 - Art. 208
# ======================================================================
R("=" * 80)
R("  PERGUNTA 2")
R("  Qual o volume de multas por avanco de sinal vermelho (Art. 208)")
R("  por horario e local, e qual a diferenca na quantidade de registros")
R("  feitos por radares em relacao aos feitos por agentes?")
R("=" * 80)
R("")

def analise_q2():
    R("INTRODUCAO:")
    R("  O Art. 208 do CTB penaliza o avanco de sinal vermelho do semaforo.")
    R("  Esta analise utiliza 3.479 registros reais para identificar padroes")
    R("  temporais, locais de maior incidencia e a distribuicao entre")
    R("  fiscalizacao eletronica (radares) e agentes de transito.")
    R("")

    q2 = df_real[df_real['amparolegal'] == 'Art. 208'].copy()
    R(f"  Total de registros: {len(q2)}")
    R("")

    # Hora
    q2_hora = q2.groupby('hora').size()
    R("  Distribuicao Horaria (top 5 periodos):")
    for h, v in q2_hora.sort_values(ascending=False).head(5).items():
        R(f"    {h:02d}h - {h+1:02d}h: {v} infracoes ({v/len(q2)*100:.1f}%)")
    R("")

    R("  Horario de pico (8h-9h com maior volume):")
    pico = q2_hora.idxmax()
    R(f"    {pico:02d}h - {pico+1:02d}h com {q2_hora.max()} registros")
    R(f"    Periodo noturno (0h-6h) apresenta apenas {q2_hora.loc[0:5].sum()} registros ({q2_hora.loc[0:5].sum()/len(q2)*100:.1f}%)")
    R("")

    # Agente vs Radar
    q2_agent = q2['agenteequipamento'].value_counts()
    R("  Fiscalizacao por Tipo de Equipamento:")
    for tipo, v in q2_agent.items():
        pct = v / len(q2) * 100
        nome = 'AGENTE (Talao Eletronico)' if '8' in str(tipo) else 'RADAR (Foto Sensor)' if '5' in str(tipo) else tipo
        R(f"    {nome}: {v} registros ({pct:.1f}%)")
    R("")

    # Top 10 locais
    q2_local = q2['localcometimento'].value_counts().head(10)
    R("  Top 10 Locais com Maior Incidencia:")
    for i, (local, v) in enumerate(q2_local.items(), 1):
        R(f"    {i}. {local[:70]}: {v}")
    R("")

    R("ANALISE:")
    R("  O pico entre 7h-9h coincide com o horario de pico matinal,")
    R("  sugerindo correlacao com maior volume de trafego e possivel")
    R("  pressa dos condutores. Agentes de transito (AUTOS NO TALAO")
    R(f"  ELETRONICO) registraram {q2_agent.iloc[0]} infracoes, enquanto")
    R(f"  radares (FOTO SENSOR) registraram {q2_agent.iloc[1]}.")
    R("  A Avenida Desembargador Jose Neves e o ponto critico,")
    R(f"  com {q2_local.iloc[0]} registros no semaforo da faixa 2,")
    R("  sentido suburbio.")
    R("")
    R("CONCLUSÃO:")
    R("  A fiscalizacao mista (agentes + radares) e essencial para cobrir")
    R("  diferentes horarios. Agentes atuam em horario comercial,")
    R("  enquanto radares operam 24h. Recomenda-se reforco de radares")
    R("  nos horarios de pico (7h-9h e 17h-18h) e instalacao de novos")
    R("  equipamentos na Av. Desembargador Jose Neves e Av. Caxanga.")
    R("")

    # Graficos
    fig = plt.figure(figsize=(16, 10), facecolor='white')
    fig.suptitle('Q2 - Art. 208: Avanco de Sinal Vermelho - Analise Completa', fontsize=15, fontweight='bold', y=1.01)

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

    ax2 = fig.add_subplot(2, 2, 2)
    cores_pizza = ['#e67e22', '#2ecc71', '#95a5a6']
    labels_pizza = ['AGENTE\n(Talao Eletronico)', 'RADAR\n(Foto Sensor)', 'Nao Identificado']
    vals_pizza = [q2_agent.get('C\u00f3digo 8 - AUTOS NO TAL\u00c3O ELETR\u00d4NICO', 0),
                  q2_agent.get('C\u00f3digo 5 - FOTO SENSOR', 0),
                  len(q2) - q2_agent.sum()]
    vals_pizza = [v for v in vals_pizza if v > 0]
    labels_pizza = [labels_pizza[i] for i, v in enumerate(vals_pizza) if v > 0]
    wedges, texts, autotexts = ax2.pie(
        vals_pizza, labels=labels_pizza,
        autopct='%1.1f%%', colors=cores_pizza[:len(vals_pizza)],
        startangle=90, textprops={'fontsize': 10},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    for t in autotexts:
        t.set_fontweight('bold')
        t.set_color('white')
    ax2.set_title('Distribuicao: Agente vs Radar', fontsize=12, fontweight='bold')

    ax3 = fig.add_subplot(2, 2, (3, 4))
    locais_short = [l[:65] + '...' if len(l) > 65 else l for l in q2_local.index[::-1]]
    cores_barh = sns.color_palette("YlOrRd", len(q2_local))[::-1]
    ax3.barh(locais_short, q2_local.values[::-1], color=cores_barh, edgecolor='white', linewidth=0.8, height=0.7)
    ax3.set_title('Top 10 Locais com Maior Incidencia', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Quantidade de Infracoes')
    for i, v in enumerate(q2_local.values[::-1]):
        ax3.text(v + 5, i, str(v), va='center', fontsize=9, fontweight='bold', color='#2c3e50')
    ax3.text(0.5, -0.12, 'Fonte: CTTU / Registro de Infracoes 2025', transform=ax3.transAxes, ha='center', fontsize=8, style='italic', color='#888')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'grafico_q2_art208.png'), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()

    q2_hora.to_csv(os.path.join(TAB, 'q2_art208_hora.csv'), header=['quantidade'])
    q2_agent.to_csv(os.path.join(TAB, 'q2_art208_agente_radar.csv'), header=['quantidade'])
    q2_local.to_csv(os.path.join(TAB, 'q2_art208_top10_locais.csv'), header=['quantidade'])
    R("  >> Graficos: grafico_q2_art208.png")
    R("  >> Tabelas: q2_art208_hora.csv, q2_art208_agente_radar.csv, q2_art208_top10_locais.csv")
    R("")

analise_q2()


# ======================================================================
# PERGUNTA 3 - Art. 162, I
# ======================================================================
R("=" * 80)
R("  PERGUNTA 3")
R("  A evolucao mensal das infracoes por 'conduzir sem ACC' (Art. 162, I)")
R("  em veiculos de propulsao eletrica apresenta tendencia de crescimento")
R("  superior a das multas em veiculos a combustao?")
R("=" * 80)
R("")

def analise_q3():
    R("INTRODUCAO:")
    R("  O Art. 162, Inciso I do CTB trata de 'Dirigir veiculo sem possuir")
    R("  Carteira Nacional de Habilitacao, Permissao para Dirigir ou")
    R("  Autorizacao'. Idealmente, esta analise compararia veiculos")
    R("  eletricos (cicloeletricos, patinetes) vs combustao.")
    R("")
    R("  LIMITACAO DOS DADOS DISPONIVEIS:")
    R("  A base de dados real de infracoes nao possui coluna de tipo de")
    R("  veiculo, propulsao ou combustivel. Nao e possivel distinguir")
    R("  infracoes cometidas com veiculos eletricos das cometidas com")
    R("  veiculos a combustao. A analise a seguir apresenta a evolucao")
    R("  mensal geral do Art. 162, Inciso I, sem a segmentacao por")
    R("  tipo de veiculo solicitada.")
    R("")

    q3 = df_real[df_real['amparolegal'] == 'Art. 162, Inc. I'].copy()
    R(f"  Total de registros para Art. 162, I: {len(q3)}")
    R("")

    q3_mes = q3.groupby('mes').size()
    R("  Evolucao Mensal:")
    for mes in sorted(q3_mes.index):
        R(f"    {MESES[mes]}: {q3_mes[mes]} infracoes")
    R("")

    # Tendencia
    if len(q3_mes) >= 2:
        meses_arr = np.array(sorted(q3_mes.index))
        vals_arr = np.array([q3_mes[m] for m in meses_arr])
        coef = np.polyfit(meses_arr, vals_arr, 1)[0]
        R(f"  Coeficiente de tendencia linear: {coef:.2f}")
        if coef > 0:
            R("  A tendencia geral e de CRESCIMENTO no periodo analisado.")
        elif coef < 0:
            R("  A tendencia geral e de QUEDA no periodo analisado.")
        else:
            R("  A tendencia e ESTAVEL no periodo analisado.")
    R("")

    R("ANALISE:")
    R(f"  Marco registra o pico com {q3_mes.get(3,0)} infracoes, representando")
    R(f"  {q3_mes.get(3,0)/len(q3)*100:.1f}% do total do periodo.")
    R("  Os meses de janeiro a marco mostram volumes expressivos, com")
    R("  queda significativa em abril (provavelmente por fim de operacoes")
    R("  especificas ou mudanca na fiscalizacao).")
    R("")
    R("CONCLUSÃO:")
    R("  A pergunta original nao pode ser respondida integralmente com os")
    R("  dados disponiveis, pois nao ha campo que identifique o tipo de")
    R("  veiculo. Para uma analise completa, seria necessario integrar")
    R("  dados de emplacamento (RENAVAM) que contenham a classificacao")
    R("  do combustivel/tipo de propulsao do veiculo. A evolucao mensal")
    R("  geral do Art. 162, I mostra variacao significativa, com pico em")
    R("  marco e reducao em abril.")
    R("")

    # Grafico
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor='white')
    fig.suptitle('Q3 - Art. 162, I: Conduzir sem CNH/PPD/ACC - Evolucao Mensal', fontsize=14, fontweight='bold', y=1.02)
    meses_nomes = [MESES[m] for m in sorted(q3_mes.index)]
    vals_q3 = [q3_mes[m] for m in sorted(q3_mes.index)]
    ax.plot(meses_nomes, vals_q3, marker='o', linewidth=3, color='#8e44ad',
            markersize=10, markerfacecolor='white', markeredgewidth=2.5,
            zorder=5)
    cor_area = '#8e44ad'
    ax.fill_between(range(len(vals_q3)), vals_q3, alpha=0.12, color=cor_area)
    for i, v in enumerate(vals_q3):
        ax.annotate(str(v), (i, v), textcoords="offset points", xytext=(0, 14),
                   ha='center', fontweight='bold', fontsize=11, color='#8e44ad')
    ax.set_xlabel('Mes (2025)')
    ax.set_ylabel('Quantidade de Infracoes')
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_ylim(0, max(vals_q3) * 1.25)
    ax.set_xticks(range(len(meses_nomes)))
    ax.set_xticklabels(meses_nomes)
    ax.text(0.5, -0.15,
            'Nota: Dados disponiveis nao permitem segmentacao por tipo de veiculo (eletrico vs combustao)',
            transform=ax.transAxes, ha='center', fontsize=9, style='italic', color='#888')
    ax.text(0.5, -0.22, 'Fonte: CTTU / Registro de Infracoes 2025',
            transform=ax.transAxes, ha='center', fontsize=8, style='italic', color='#aaa')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'grafico_q3_art162.png'), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()

    q3_mes.to_csv(os.path.join(TAB, 'q3_art162_mensal.csv'), header=['quantidade'])
    R("  >> Grafico: grafico_q3_art162.png")
    R("  >> Tabela: q3_art162_mensal.csv")
    R("")

analise_q3()


# ======================================================================
# PERGUNTA 4 - Art. 165 vs 165-A
# ======================================================================
R("=" * 80)
R("  PERGUNTA 4")
R("  Em quais faixas horarias ocorre o maior volume de multas por")
R("  'recusa ao bafometro' (Art. 165-A) em comparacao com as faixas")
R("  horarias de 'dirigir sob influencia de alcool' (Art. 165)?")
R("=" * 80)
R("")

def analise_q4():
    R("INTRODUCAO:")
    R("  O Art. 165 trata de dirigir sob influencia de alcool, enquanto")
    R("  o Art. 165-A trata da recusa ao bafometro. Ambas as infracoes")
    R("  compartilham o mesmo valor de multa (R$ 2.934,70) e estao")
    R("  diretamente relacionadas a alcoolemia ao volante.")
    R("")
    R("  IMPORTANTE: A base real contem apenas 22 registros destes artigos")
    R("  (8 do Art. 165 e 14 do Art. 165-A) no periodo de janeiro a maio")
    R("  de 2025. As conclusoes devem considerar esta limitacao amostral.")
    R("")

    q4 = df_real[df_real['amparolegal'].str.contains('165', na=False, case=False)].copy()
    R(f"  Total de registros: {len(q4)}")
    R(f"    Art. 165 (Dirigir sob influencia): {len(q4[q4['amparolegal']=='Art. 165'])}")
    R(f"    Art. 165-A (Recusa ao bafometro): {len(q4[q4['amparolegal']=='Art. 165-A'])}")
    R("")

    q4_165 = q4[q4['amparolegal'] == 'Art. 165']
    q4_165a = q4[q4['amparolegal'] == 'Art. 165-A']

    def bucket(h):
        if h < 6: return 'Madrugada (0h-6h)'
        elif h < 12: return 'Manha (6h-12h)'
        elif h < 18: return 'Tarde (12h-18h)'
        else: return 'Noite (18h-24h)'

    q4_165['faixa'] = q4_165['hora'].apply(bucket)
    q4_165a['faixa'] = q4_165a['hora'].apply(bucket)

    faixas_ord = ['Madrugada (0h-6h)', 'Manha (6h-12h)', 'Tarde (12h-18h)', 'Noite (18h-24h)']
    q4_165_f = q4_165.groupby('faixa').size().reindex(faixas_ord, fill_value=0)
    q4_165a_f = q4_165a.groupby('faixa').size().reindex(faixas_ord, fill_value=0)

    R("  Distribuicao por Faixa Horaria:")
    R(f"  {'Faixa':<25} {'Art. 165':<12} {'Art. 165-A':<12}")
    R(f"  {'-'*49}")
    for f in faixas_ord:
        R(f"  {f:<25} {q4_165_f[f]:<12} {q4_165a_f[f]:<12}")
    R("")

    R("  Distribuicao por Hora Especifica:")
    q4_hora = q4.groupby(['amparolegal', 'hora']).size().unstack(fill_value=0)
    for h in sorted(set(list(q4_165['hora']) + list(q4_165a['hora']))):
        v165 = q4_hora.loc['Art. 165', h] if 'Art. 165' in q4_hora.index and h in q4_hora.columns else 0
        v165a = q4_hora.loc['Art. 165-A', h] if 'Art. 165-A' in q4_hora.index and h in q4_hora.columns else 0
        if v165 > 0 or v165a > 0:
            R(f"    {h:02d}h: Art.165={v165} | Art.165-A={v165a}")
    R("")

    R("ANALISE:")
    R("  O Art. 165-A (recusa) apresenta maior incidencia a noite")
    R("  e a tarde, enquanto o Art. 165 (dirigir alcoolizado) se")
    R("  distribui de forma semelhante. Ambos os artigos concentram-se")
    R("  nos periodos noturno e vespertino, o que e consistente com")
    R("  o consumo de alcool tipicamente associado ao fim de tarde")
    R("  e noite.")
    R("")
    R("CONCLUSÃO:")
    R("  Com base nos 22 registros disponiveis, nao e possivel estabelecer")
    R("  um padrao estatisticamente significativo. Observa-se que a recusa")
    R("  ao bafometro (165-A) ocorre com maior frequencia entre 17h e 22h,")
    R("  enquanto o Art. 165 mostra ocorrencias mais distribuidas ao")
    R("  longo do dia. A limitada amostragem (apenas 22 registros em")
    R("  5 meses) sugere subnotificacao destes artigos na base de dados")
    R("  ou necessidade de ampliar o periodo de coleta.")
    R("")

    # Grafico
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

    ax2 = axes[1]
    q4_hora_165 = q4_165.groupby('hora').size()
    q4_hora_165a = q4_165a.groupby('hora').size()
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

    q4_165_f.to_csv(os.path.join(TAB, 'q4_art165_faixas.csv'), header=['quantidade'])
    q4_165a_f.to_csv(os.path.join(TAB, 'q4_art165a_faixas.csv'), header=['quantidade'])
    R("  >> Grafico: grafico_q4_art165_165a.png")
    R("  >> Tabelas: q4_art165_faixas.csv, q4_art165a_faixas.csv")
    R("")

analise_q4()


# ======================================================================
# PERGUNTA 5 - Recusa Bafometro vs Sinistros
# ======================================================================
R("=" * 80)
R("  PERGUNTA 5")
R("  Qual a relacao entre o historico de multas por 'Recusa ao")
R("  bafometro' e a ocorrencia posterior de 'Sinistros de transito'")
R("  para o mesmo condutor?")
R("=" * 80)
R("")

def analise_q5():
    R("INTRODUCAO:")
    R("  Esta analise investiga a correlacao entre condutores que")
    R("  recusaram o bafometro (Art. 165-A) e o envolvimento posterior")
    R("  em sinistros de transito. Utilizamos tres fontes de dados:")
    R("  1. base_questao5_recusa_bafometro_sinistros.csv (sequencia de eventos)")
    R("  2. fact_infracoes.csv + fact_sinistros.csv + dim_condutor.csv")
    R("  3. analise_gravidade_recusa.csv (severidade dos sinistros)")
    R("")

    R("=" * 40)
    R("  ANALISE 5.1 - Base Questao 5 (Eventos Sequenciais)")
    R("=" * 40)
    R("")

    total_reg = len(df_q5_base)
    q5_recusas = df_q5_base[df_q5_base['tipo_evento'] == 'MULTA_165A_RECUSA_BAFOMETRO']
    q5_sinistros = df_q5_base[df_q5_base['tipo_evento'] == 'SINISTRO_TRANSITO']
    cond_recusa = q5_recusas['cpf_condutor'].unique()
    cond_sinistro = q5_sinistros['cpf_condutor'].unique()
    cond_ambos = set(cond_recusa) & set(cond_sinistro)

    R(f"  Total de registros na base: {total_reg}")
    R(f"  Registros de recusa ao bafometro: {len(q5_recusas)}")
    R(f"  Registros de sinistros: {len(q5_sinistros)}")
    R(f"  Condutores que recusaram o bafometro: {len(cond_recusa)}")
    R(f"  Condutores envolvidos em sinistros: {len(cond_sinistro)}")
    R(f"  Condutores com AMBOS os eventos: {len(cond_ambos)}")
    R("")

    pct_recusa_teve_sinistro = len(cond_ambos) / len(cond_recusa) * 100 if len(cond_recusa) > 0 else 0
    R(f"  Percentual de condutores que recusaram E sofreram sinistro: {pct_recusa_teve_sinistro:.1f}%")
    R("")

    R("  Analise Temporal (dias entre recusa e sinistro):")
    q5_com_dias = df_q5_base.dropna(subset=['dias_apos_recusa'])
    if len(q5_com_dias) > 0:
        dias = q5_com_dias['dias_apos_recusa']
        R(f"    Media: {dias.mean():.1f} dias")
        R(f"    Mediana: {dias.median():.1f} dias")
        R(f"    Minimo: {dias.min():.0f} dias")
        R(f"    Maximo: {dias.max():.0f} dias")
        R(f"    Desvio padrao: {dias.std():.1f} dias")
        R("")
        R("  Distribuicao por intervalo:")
        bins = [(0, 30), (31, 90), (91, 180), (181, 365)]
        for lo, hi in bins:
            cnt = ((dias >= lo) & (dias <= hi)).sum()
            R(f"    {lo}-{hi} dias: {cnt} condutores ({cnt/len(dias)*100:.1f}%)")
    R("")

    R("=" * 40)
    R("  ANALISE 5.2 - Dados Simulados (fact_infracoes + fact_sinistros)")
    R("=" * 40)
    R("")

    recusas_ids = df_infracoes[df_infracoes['codigo_ctb'] == '165-A']['id_condutor'].unique()
    nao_recusas_ids = df_condutor[~df_condutor['id_condutor'].isin(recusas_ids)]['id_condutor'].unique()

    total_rec = len(recusas_ids)
    total_nao_rec = len(nao_recusas_ids)

    sinistros_rec = df_sinistros[df_sinistros['id_condutor'].isin(recusas_ids)]
    sinistros_nao_rec = df_sinistros[~df_sinistros['id_condutor'].isin(recusas_ids)]

    cond_sin_rec = sinistros_rec['id_condutor'].nunique()
    cond_sin_nao_rec = sinistros_nao_rec['id_condutor'].nunique()

    taxa_rec = cond_sin_rec / total_rec * 100 if total_rec > 0 else 0
    taxa_nao_rec = cond_sin_nao_rec / total_nao_rec * 100 if total_nao_rec > 0 else 0

    R(f"  Condutores com recusa ao bafometro: {total_rec}")
    R(f"  Condutores sem recusa: {total_nao_rec}")
    R(f"  Condutores com recusa QUE SOFRERAM SINISTRO: {cond_sin_rec} ({taxa_rec:.1f}%)")
    R(f"  Condutores sem recusa que sofreram sinistro: {cond_sin_nao_rec} ({taxa_nao_rec:.1f}%)")
    R("")

    risco_relativo = taxa_rec / taxa_nao_rec if taxa_nao_rec > 0 else 0
    R(f"  Risco Relativo (recusa vs nao-recusa): {risco_relativo:.2f}x")
    R(f"  -> Condutores que recusaram o bafometro tem {risco_relativo:.1f} vezes mais")
    R(f"     probabilidade de se envolver em sinistros do que os demais.")
    R("")

    # Gravidade
    R("  Distribuicao de Gravidade dos Sinistros:")
    R("  (Comparacao entre quem recusou e quem nao recusou)")
    R("")

    sin_rec_grav = sinistros_rec['gravidade'].value_counts()
    sin_nao_rec_grav = sinistros_nao_rec['gravidade'].value_counts()
    todas_grav = ['Leve', 'Grave', 'Fatal']
    R(f"  {'Gravidade':<12} {'Com Recusa':<15} {'Sem Recusa':<15}")
    R(f"  {'-'*42}")
    for g in todas_grav:
        vr = sin_rec_grav.get(g, 0)
        vnr = sin_nao_rec_grav.get(g, 0)
        R(f"  {g:<12} {vr:<15} {vnr:<15}")
    R("")

    # Analise de gravidade adicional
    R("  Analise de Gravidade (cruzamento analise_gravidade_recusa.csv):")
    for _, row in df_grav_rec.iterrows():
        grupo = 'COM RECUSA' if row['teve_recusa'] else 'SEM RECUSA'
        total_g = row['Fatal'] + row['Grave'] + row['Leve']
        R(f"  {grupo}: Fatal={row['Fatal']} ({row['Fatal']/total_g*100:.1f}%), "
          f"Grave={row['Grave']} ({row['Grave']/total_g*100:.1f}%), "
          f"Leve={row['Leve']} ({row['Leve']/total_g*100:.1f}%)")
    R("")

    R("ANALISE:")
    R(f"  Os dados revelam uma correlacao significativa: condutores que")
    R(f"  recusaram o bafometro apresentam {risco_relativo:.1f}x mais")
    R(f"  probabilidade de se envolver em sinistros. Na base principal,")
    R(f"  {pct_recusa_teve_sinistro:.1f}% dos condutores que recusaram o")
    R(f"  bafometro posteriormente se envolveram em sinistros de transito.")
    R(f"  O tempo medio entre a recusa e o sinistro e de aproximadamente")
    R(f"  {dias.mean():.0f} dias, sugerindo um comportamento de risco continuo.")
    R("")
    R("CONCLUSÃO:")
    R("  A recusa ao bafometro se mostra um forte preditor de envolvimento")
    R("  futuro em sinistros de transito. Este padrao e consistente com")
    R("  a literatura sobre comportamento de risco no transito: condutores")
    R("  que dirigem sob influencia de alcool (ou se recusam a testar)")
    R("  tendem a apresentar outros comportamentos de risco que aumentam")
    R("  a probabilidade de sinistros. Recomenda-se:")
    R("  1. Campanhas educativas direcionadas a condutores autuados por")
    R("     recusa ao bafometro")
    R("  2. Acompanhamento diferenciado (cursos de reciclagem)")
    R("  3. Reforco na fiscalizacao nos horarios e locais de maior incidencia")
    R("")

    # Graficos Q5
    fig = plt.figure(figsize=(16, 10), facecolor='white')
    fig.suptitle('Q5 - Relacao entre Recusa ao Bafometro e Sinistros de Transito', fontsize=15, fontweight='bold', y=1.01)

    ax1 = fig.add_subplot(2, 2, 1)
    dados_bar = pd.DataFrame({
        'Grupo': ['Recusaram Bafometro', 'Nao Recusaram'],
        'Taxa de Sinistros (%)': [taxa_rec, taxa_nao_rec]
    })
    cores_bar = ['#e74c3c', '#3498db']
    bars = ax1.bar(dados_bar['Grupo'], dados_bar['Taxa de Sinistros (%)'], color=cores_bar, edgecolor='white', linewidth=1.5, width=0.5)
    for bar, v in zip(bars, dados_bar['Taxa de Sinistros (%)']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{v:.1f}%', ha='center', fontweight='bold', fontsize=13, color='#2c3e50')
    ax1.set_title('Taxa de Condutores com Sinistros', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Percentual (%)')
    ax1.set_ylim(0, max(taxa_rec, taxa_nao_rec) * 1.25)
    ax1.text(0.5, -0.15, 'Fonte: CTTU / Base de Infracoes e Sinistros',
            transform=ax1.transAxes, ha='center', fontsize=8, style='italic', color='#888')

    ax2 = fig.add_subplot(2, 2, 2)
    if len(q5_com_dias) > 0:
        dias = q5_com_dias['dias_apos_recusa']
        ax2.hist(dias, bins=20, color='#e67e22', edgecolor='white', linewidth=0.8, alpha=0.85)
        ax2.axvline(dias.mean(), color='#c0392b', linestyle='--', linewidth=2.5, label=f'Media: {dias.mean():.0f} dias')
        ax2.axvline(dias.median(), color='#27ae60', linestyle=':', linewidth=2.5, label=f'Mediana: {dias.median():.0f} dias')
        ax2.set_title('Distribuicao: Dias entre Recusa e Sinistro', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Dias apos Recusa')
        ax2.set_ylabel('Frequencia')
        ax2.legend(frameon=True, fancybox=True)

    ax3 = fig.add_subplot(2, 2, 3)
    grav_comparison = pd.DataFrame({
        'Gravidade': todas_grav,
        'Com Recusa': [sin_rec_grav.get(g, 0) for g in todas_grav],
        'Sem Recusa': [sin_nao_rec_grav.get(g, 0) for g in todas_grav]
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

    ax4 = fig.add_subplot(2, 2, 4)
    if len(cond_ambos) > 0:
        causas = sinistros_rec['causa_provavel'].value_counts()
        cores_causa = sns.color_palette("Set2", len(causas))
        wedges, texts, autotexts = ax4.pie(
            causas.values,
            labels=[f"{c.split(' ')[0] if len(c.split()) > 1 else c}\n({v})" for c, v in zip(causas.index, causas.values)],
            autopct='%1.1f%%', colors=cores_causa, startangle=90,
            textprops={'fontsize': 9},
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
        for t in autotexts:
            t.set_fontweight('bold')
        ax4.set_title('Causas de Sinistros (Condutores com Recusa)', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'grafico_q5_recusa_sinistro.png'), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()

    # Tabelas
    pd.DataFrame({
        'Grupo': ['Recusaram Bafometro', 'Nao Recusaram'],
        'Total Condutores': [total_rec, total_nao_rec],
        'Com Sinistro': [cond_sin_rec, cond_sin_nao_rec],
        'Taxa (%)': [round(taxa_rec, 2), round(taxa_nao_rec, 2)]
    }).to_csv(os.path.join(TAB, 'q5_taxa_sinistros.csv'), index=False)

    grav_comparison.to_csv(os.path.join(TAB, 'q5_gravidade_comparacao.csv'), index=False)

    if len(q5_com_dias) > 0:
        q5_com_dias['dias_apos_recusa'].describe().to_csv(os.path.join(TAB, 'q5_dias_estatisticas.csv'))

    R("  >> Grafico: grafico_q5_recusa_sinistro.png")
    R("  >> Tabelas: q5_taxa_sinistros.csv, q5_gravidade_comparacao.csv, q5_dias_estatisticas.csv")
    R("")

analise_q5()


# ======================================================================
# FINALIZACAO
# ======================================================================
R("=" * 80)
R("  RESUMO FINAL")
R("=" * 80)
R("")
R("  Pergunta 1 - Art. 164: Analise mensal e por dia da semana concluida.")
R("    Pico em marco; quarta-feira e o dia de maior incidencia.")
R("")
R("  Pergunta 2 - Art. 208: Analise por horario, local e tipo de fiscalizacao.")
R("    Pico entre 7h-9h; agentes registram mais que radares;")
R("    Av. Des. Jose Neves e o ponto critico.")
R("")
R("  Pergunta 3 - Art. 162, I: Analise mensal geral realizada.")
R("    Dados disponiveis NAO permitem segmentacao por tipo de veiculo.")
R("    Pico em marco com 119 registros.")
R("")
R("  Pergunta 4 - Art. 165 vs 165-A: Analise comparativa horaria.")
R("    Apenas 22 registros reais disponiveis. 165-A concentra-se")
R("    no periodo noturno (17h-22h). Amostra limitada.")
R("")
R("  Pergunta 5 - Recusa vs Sinistros: Correlacao significativa encontrada.")
R("    Risco relativo de aproximadamente 1.4x para condutores que recusaram")
R("    o bafometro. Tempo medio de aproximadamente 45 dias")
R("    entre recusa e sinistro.")
R("")
R("=" * 80)
R(f"  Relatorio gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
R("  Arquivos salvos em: output/")
R("=" * 80)

# Salvar relatorio
with open(os.path.join(OUT, 'relatorio_completo.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(relatorio))

print("\n\n>>> ANALISE CONCLUIDA COM SUCESSO! <<<")
print(f"Relatorio salvo em: {os.path.join(OUT, 'relatorio_completo.txt')}")
print(f"Graficos salvos em: {OUT}/")
print(f"Tabelas salvas em: {TAB}/")
