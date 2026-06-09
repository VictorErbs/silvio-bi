import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar dados
df_infracoes = pd.read_csv('fact_infracoes.csv')
df_sinistros = pd.read_csv('fact_sinistros.csv')
df_condutor = pd.read_csv('dim_condutor.csv')

# Análise: Condutores com Recusa vs Sinistros
recusas = df_infracoes[df_infracoes['codigo_ctb'] == '165-A']['id_condutor'].unique()
nao_recusas = df_condutor[~df_condutor['id_condutor'].isin(recusas)]['id_condutor'].unique()

# Calcular proporção de sinistros por grupo
total_condutores_recusa = len(recusas)
total_condutores_nao_recusa = len(nao_recusas)

sinistros_recusa = df_sinistros[df_sinistros['id_condutor'].isin(recusas)]['id_condutor'].nunique()
sinistros_nao_recusa = df_sinistros[df_sinistros['id_condutor'].isin(nao_recusas)]['id_condutor'].nunique()

taxa_recusa = (sinistros_recusa / total_condutores_recusa) * 100
taxa_nao_recusa = (sinistros_nao_recusa / total_condutores_nao_recusa) * 100

# Criar visualização
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")
data = {
    'Grupo': ['Recusaram Bafômetro', 'Não Recusaram'],
    'Taxa de Sinistros (%)': [taxa_recusa, taxa_nao_recusa]
}
df_plot = pd.DataFrame(data)

barplot = sns.barplot(x='Grupo', y='Taxa de Sinistros (%)', data=df_plot, palette='viridis')
plt.title('Relação entre Recusa ao Bafômetro e Sinistros Posteriores (Simulado 2025)', fontsize=14)
plt.ylabel('Taxa de Condutores com Sinistros (%)')
plt.ylim(0, max(taxa_recusa, taxa_nao_recusa) + 5)

# Adicionar rótulos nas barras
for p in barplot.patches:
    barplot.annotate(format(p.get_height(), '.1f') + '%', 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points')

plt.savefig('analise_recusa_sinistro.png')

# Tabela de Correlação por Gravidade
df_merged = df_sinistros.merge(df_infracoes[df_infracoes['codigo_ctb'] == '165-A'], on='id_condutor', how='left', suffixes=('_sin', '_inf'))
df_merged['teve_recusa'] = df_merged['codigo_ctb'].notna()

gravidade_analise = df_merged.groupby(['teve_recusa', 'gravidade']).size().unstack(fill_value=0)
gravidade_analise.to_csv('analise_gravidade_recusa.csv')

print("Análise de BI concluída e gráficos gerados!")
