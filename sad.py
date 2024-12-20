import streamlit as st
import pandas as pd
import plotly.express as px
import math

# Etapa 1: Estruturação do Problema e Definição dos Critérios
st.title("Aplicação do Modelo Proposto - Seleção de Fornecedores")
st.subheader("Estruturação do Problema")

st.write("""
O processo de seleção de fornecedores de serviços de terraplanagem envolve critérios econômicos, ambientais, sociais e gerais. 
Por favor, selecione os critérios que você deseja considerar e os fornecedores que serão avaliados.
""")

criterios = {
    'C1': 'Preço/Custo do serviço',
    'C2': 'Qualidade',
    'C3': 'Entrega',
    'C4': 'Tecnologia',
    'C5': 'Custos ambientais',
    'C6': 'Projeto verde',
    'C7': 'Gestão ambiental',
    'C8': 'Partes interessadas (direito, atendimento)',
    'C9': 'Segurança e saúde no trabalho',
    'C10': 'Respeito pela política dos funcionários',
    'C11': 'Gestão social',
    'C12': 'Histórico de desempenho',
    'C13': 'Reputação'
}

st.write("### Selecione os critérios que você deseja incluir na avaliação:")
criterios_selecionados = st.multiselect(
    "Critérios disponíveis", list(criterios.values()), default=list(criterios.values())
)

# Etapa 2: Seleção de Fornecedores
st.write("### Selecione os fornecedores que você deseja avaliar:")
fornecedores_disponiveis = ['Fornecedor A', 'Fornecedor B', 'Fornecedor C', 'Fornecedor D']
fornecedores_selecionados = st.multiselect(
    "Fornecedores disponíveis", fornecedores_disponiveis, default=fornecedores_disponiveis
)

# Etapa 3: Atribuição de Pesos aos Critérios (ajustando para refletir os valores reais)
st.subheader("Atribuição de Pesos aos Critérios")
st.write("""
Atribua os pesos de importância relativa para cada critério selecionado com base nos valores da Tabela 27. O peso padrão é 10.
""")

pesos = {}
for criterio in criterios_selecionados:
    pesos[criterio] = st.slider(f"Peso para o critério {criterio}", 0.0, 25.0, 10.0)

# Funções de Preferência disponíveis
funcoes_preferencia = {
    'Linear': 'Linear',
    'U-Shape': 'U-Shape',
    'V-Shape': 'V-Shape',
    'Level': 'Level',
    'V-Shape I': 'V-Shape I',
    'Gaussian': 'Gaussian'
}

# Etapa 4: Entrada de Desempenho dos Fornecedores e Função de Preferência
st.subheader("Desempenho dos Fornecedores em cada Critério")
st.write("""
Insira o desempenho de cada fornecedor em relação aos critérios selecionados. 
Em seguida, escolha a função de preferência para cada critério.
""")

# Dicionário para armazenar as entradas de desempenho e funções de preferência
desempenho_fornecedores = {}
funcoes_selecionadas = {}
parametros = {}

for fornecedor in fornecedores_selecionados:
    st.write(f"### Desempenho para {fornecedor}")
    desempenho_fornecedores[fornecedor] = {}
    funcoes_selecionadas[fornecedor] = {}
    parametros[fornecedor] = {}
    
    for criterio in criterios_selecionados:
        desempenho_fornecedores[fornecedor][criterio] = st.number_input(
            f"Desempenho de {fornecedor} no critério {criterio}",
            min_value=0, max_value=1000000 if criterio == 'Preço/Custo do serviço' else 100,
            value=50
        )
        
        # Seleção da função de preferência ao lado da entrada de desempenho
        funcoes_selecionadas[fornecedor][criterio] = st.selectbox(
            f"Função de preferência para {fornecedor} no critério {criterio}",
            list(funcoes_preferencia.values()), key=f"{fornecedor}_{criterio}"
        )
        
        # Inserir parâmetros q, r ou s dependendo da função de preferência
        if funcoes_selecionadas[fornecedor][criterio] in ['U-Shape', 'V-Shape', 'Level', 'V-Shape I']:
            parametros[fornecedor][criterio] = {
                'q': st.number_input(f"Limiar de indiferença (q) para o critério {criterio} ({fornecedor})", min_value=0.0, max_value=100.0, value=10.0, key=f"q_{fornecedor}_{criterio}"),
                'r': st.number_input(f"Limiar de preferência (r) para o critério {criterio} ({fornecedor})", min_value=0.0, max_value=100.0, value=20.0, key=f"r_{fornecedor}_{criterio}")
            }
        if funcoes_selecionadas[fornecedor][criterio] == 'Gaussian':
            parametros[fornecedor][criterio] = {
                's': st.number_input(f"Parâmetro Gaussiano (s) para o critério {criterio} ({fornecedor})", min_value=0.1, max_value=10.0, value=1.0, key=f"s_{fornecedor}_{criterio}")
            }

# Exibir o desempenho inserido
st.write("### Desempenho dos Fornecedores:")
df_desempenho = pd.DataFrame(desempenho_fornecedores)
st.dataframe(df_desempenho)

# Função para calcular o diferencial de desempenho
def calcular_diferencial(df, fornecedor_1, fornecedor_2, criterio):
    return abs(df[fornecedor_1][criterio] - df[fornecedor_2][criterio])

# Função para aplicar a função de preferência
def aplicar_funcao_preferencia(funcao, diferenca, parametros):
    if funcao == 'Linear':
        return 1 if diferenca > 0 else 0
    elif funcao == 'U-Shape':
        return 1 if diferenca > parametros['q'] else 0
    elif funcao == 'V-Shape':
        return min(diferenca / parametros['r'], 1)
    elif funcao == 'Level':
        if diferenca <= parametros['q']:
            return 0
        elif parametros['q'] < diferenca <= parametros['r']:
            return 0.5
        else:
            return 1
    elif funcao == 'V-Shape I':
        if diferenca <= parametros['q']:
            return 0
        elif parametros['q'] < diferenca <= parametros['r']:
            return (diferenca - parametros['q']) / (parametros['r'] - parametros['q'])
        else:
            return 1
    elif funcao == 'Gaussian':
        return 1 - math.exp(-(diferenca ** 2) / (2 * (parametros['s'] ** 2)))

# Etapa 5: Cálculo dos Fluxos Positivos, Negativos e Líquidos (PROMETHEE II)
st.subheader("Cálculo dos Fluxos (PROMETHEE II)")

# Função para calcular os fluxos (considerando as funções de preferência)
def calcular_fluxos(df, pesos, funcoes_selecionadas, parametros):
    fluxos_positivos = {}
    fluxos_negativos = {}
    for fornecedor in df.columns:
        fluxo_positivo = 0
        fluxo_negativo = 0
        for outro_fornecedor in df.columns:
            if fornecedor != outro_fornecedor:
                for criterio in df.index:
                    diferenca = calcular_diferencial(df, fornecedor, outro_fornecedor, criterio)
                    pref_value = aplicar_funcao_preferencia(funcoes_selecionadas[fornecedor][criterio], diferenca, parametros[fornecedor].get(criterio, {}))
                    if df[fornecedor][criterio] > df[outro_fornecedor][criterio]:
                        fluxo_positivo += pesos[criterio] * pref_value
                    else:
                        fluxo_negativo += pesos[criterio] * pref_value
        fluxos_positivos[fornecedor] = fluxo_positivo
        fluxos_negativos[fornecedor] = fluxo_negativo
    return fluxos_positivos, fluxos_negativos

# Calcular os fluxos
fluxos_positivos, fluxos_negativos = calcular_fluxos(df_desempenho, pesos, funcoes_selecionadas, parametros)

# Calcular os fluxos líquidos
fluxos_liquidos = {fornecedor: fluxos_positivos[fornecedor] - fluxos_negativos[fornecedor] for fornecedor in fornecedores_selecionados}

# Exibir os fluxos calculados
df_fluxos = pd.DataFrame({
    'Fornecedor': fornecedores_selecionados,
    'Fluxo Positivo (ϕ+)': [fluxos_positivos[fornecedor] for fornecedor in fornecedores_selecionados],
    'Fluxo Negativo (ϕ-)': [fluxos_negativos[fornecedor] for fornecedor in fornecedores_selecionados],
    'Fluxo Líquido (ϕ)': [fluxos_liquidos[fornecedor] for fornecedor in fornecedores_selecionados]
})
st.write("### Resultados dos Fluxos:")
st.dataframe(df_fluxos)

# Gráfico interativo dos fluxos líquidos
fig = px.bar(df_fluxos, x='Fornecedor', y='Fluxo Líquido (ϕ)', title="Fluxo Líquido dos Fornecedores")
st.plotly_chart(fig)
