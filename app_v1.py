import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(layout="wide")
st.title('📊 Dashboard - Métricas por Ano e Dimensão')

# ==================== Carregar dados ====================
url = "https://raw.githubusercontent.com/OtavioAntonio/Ciencia_de_dadosDCA3501/main/Global_AI_Content_Impact_Dataset.csv"
df = pd.read_csv(url)

# ==================== Valores únicos ====================
all_countries = sorted(df['Country'].unique())
all_industries = sorted(df['Industry'].unique())
all_tools = sorted(df['Top AI Tools Used'].unique())

# ==================== Painel de Filtros ====================
with st.sidebar:
    st.markdown('## 🎛️ Filtros')
    with st.expander('Filtros Avançados', expanded=True):

        # Botão de reset que redefine o estado antes de recarregar
        if st.button("🔄 Resetar filtros"):
            st.session_state['countries'] = all_countries
            st.session_state['industries'] = all_industries
            st.session_state['tools'] = all_tools
            st.session_state['check_all_countries'] = True
            st.session_state['check_all_industries'] = True
            st.session_state['check_all_tools'] = True
            st.rerun() # ou st.rerun(), conforme sua versão do Streamlit

        # Checkbox Selecionar todos e multiselect para Países
        select_all_countries = st.checkbox(
            "🌍 Selecionar todos os países",
            value=True,
            key='check_all_countries'
        )
        countries = st.multiselect(
            'Países:',
            options=all_countries,
            default=all_countries if select_all_countries else [],
            key='countries'
        )

        # Checkbox Selecionar todas e multiselect para Indústrias
        select_all_industries = st.checkbox(
            "🏭 Selecionar todas as indústrias",
            value=True,
            key='check_all_industries'
        )
        industries = st.multiselect(
            'Indústrias:',
            options=all_industries,
            default=all_industries if select_all_industries else [],
            key='industries'
        )

        # Checkbox Selecionar todas e multiselect para Ferramentas
        select_all_tools = st.checkbox(
            "🛠️ Selecionar todas as ferramentas",
            value=True,
            key='check_all_tools'
        )
        tools = st.multiselect(
            'Ferramentas de IA:',
            options=all_tools,
            default=all_tools if select_all_tools else [],
            key='tools'
        )

    st.markdown('---')
    metric_options = [
        "AI Adoption Rate (%)",
        "Job Loss Due to AI (%)",
        "Revenue Increase Due to AI (%)",
        "Human-AI Collaboration Rate (%)",
        "Consumer Trust in AI (%)",
        "Market Share of AI Companies (%)"
    ]
    metric = st.selectbox(
        "📐 Métrica a visualizar (gráfico 2)",
        options=metric_options,
        index=0,
        key="metric_selectbox"
    )

# ==================== Filtro para a dimensão da legenda ====================
legend_option = st.selectbox(
    "🎨 Agrupar por:",
    options=['Country', 'Industry', 'Top AI Tools Used'],
    index=0,
    key='legend_option'
)

# ==================== Aplicar filtros ====================
df_filtered = df[
    (df['Country'].isin(countries)) &
    (df['Industry'].isin(industries)) &
    (df['Top AI Tools Used'].isin(tools))
]

# ==================== Gráfico 1: Conteúdo Gerado por IA ====================
metric1 = "AI-Generated Content Volume (TBs per year)"
agg_func1 = "sum"
df_grouped_1 = df_filtered.groupby(['Year', legend_option])[metric1].agg(agg_func1).reset_index()

st.header(f'📊 {metric1} por Year e {legend_option}')
st.altair_chart(
    alt.Chart(df_grouped_1).mark_line(point=True).encode(
        x='Year:O',
        y=alt.Y(f'{metric1}:Q'),
        color=f'{legend_option}:N',
        tooltip=['Year', legend_option, metric1]
    ).properties(height=400, width='container'),
    use_container_width=True
)

# ==================== Gráfico 2: Métrica Selecionada ====================
agg_func2 = "mean"
df_grouped_2 = df_filtered.groupby(['Year', 'Top AI Tools Used'])[metric].agg(agg_func2).reset_index()

st.header(f'📊 {metric} por Ferramenta ao longo do tempo (barras agrupadas)')
chart = alt.Chart(df_grouped_2).mark_bar().encode(
    x=alt.X('Year:O'),
    y=alt.Y(f'{metric}:Q'),
    color='Top AI Tools Used:N',
    xOffset='Top AI Tools Used:N',
    tooltip=['Year', 'Top AI Tools Used', metric]
).properties(width='container', height=400)
st.altair_chart(chart, use_container_width=True)

# ==================== Gráfico 3: Radar Chart ====================
st.header("📡 Comparação de Métricas por Ferramenta de IA (Radar Chart)")

available_years = sorted(df_filtered['Year'].unique())
year_selected = st.selectbox(
    "📅 Selecione o Ano para análise",
    available_years,
    index=len(available_years)-1,
    key="radar_year"
)

df_radar = df_filtered[df_filtered['Year'] == year_selected]
radar_metrics = metric_options

radar_df = df_radar.groupby('Top AI Tools Used')[radar_metrics].mean().reset_index()
radar_df = pd.melt(radar_df, id_vars=['Top AI Tools Used'], var_name='Métrica', value_name='Valor')

fig_radar = px.line_polar(
    radar_df,
    r='Valor',
    theta='Métrica',
    color='Top AI Tools Used',
    line_close=True,
    template="plotly_dark",
    height=500
)
st.plotly_chart(fig_radar, use_container_width=True)

# ==================== Visualização da Tabela ====================
st.header('🔍 Dados filtrados')
st.dataframe(df_filtered.sort_values(by=['Year', 'Country']), use_container_width=True)

# ==================== Exportar CSV ====================
st.markdown("### 📤 Exportar Dados Filtrados")
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar como CSV",
    data=csv,
    file_name='dados_filtrados.csv',
    mime='text/csv'
)
