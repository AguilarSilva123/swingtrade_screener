import yfinance as yf
import pandas as pd
import pandas_ta as ta
from scipy.signal import find_peaks
import streamlit as st

# --- FUNÇÃO DE ANÁLISE ---
def analisar_ativo(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        df_semanal = ticker.history(period="2y", interval="1wk")
        df_diario = ticker.history(period="1y", interval="1d")
        df_60m = ticker.history(period="1mo", interval="60m")
        
        if df_semanal.empty or df_diario.empty or df_60m.empty:
            return None

        df_semanal['EMA_72'] = ta.ema(df_semanal['Close'], length=72)
        preco_atual = df_diario['Close'].iloc[-1]
        ema_72_sem_atual = df_semanal['EMA_72'].iloc[-1]
        
        if pd.isna(ema_72_sem_atual):
            return None

        tendencia_alta = preco_atual > ema_72_sem_atual

        topos_indices, _ = find_peaks(df_60m['High'], distance=3)
        fundos_indices, _ = find_peaks(-df_60m['Low'], distance=3) 

        if len(topos_indices) == 0 or len(fundos_indices) == 0:
            return None

        ultimo_topo = df_60m['High'].iloc[topos_indices[-1]]
        ultimo_fundo = df_60m['Low'].iloc[fundos_indices[-1]]

        entrada = ultimo_topo + 0.01
        stop_loss = ultimo_fundo - 0.01
        risco = entrada - stop_loss
        alvo = entrada + (risco * 3)

        status = "APROVADO" if tendencia_alta else "DESCARTADO"

        return {
            "Ticker": ticker_symbol,
            "Status": status,
            "Preço Atual": f"R$ {preco_atual:.2f}",
            "Entrada": f"R$ {entrada:.2f}",
            "Stop Loss": f"R$ {stop_loss:.2f}",
            "Alvo (1:3)": f"R$ {alvo:.2f}"
        }
    except Exception:
        return None

# --- INTERFACE WEB (STREAMLIT) ---
st.set_page_config(page_title="Screener André Moraes", layout="wide")
st.title("📈 Screener de Swing Trade")
st.markdown("Identificador automático de entradas seguindo a estratégia de André Moraes (Ciclos e Price Action).")

st.sidebar.header("Painel de Controle")
st.sidebar.markdown("Faça o upload de uma planilha contendo os tickers na primeira coluna (ex: PETR4.SA).")

# Botão de Upload para a sua planilha
uploaded_file = st.sidebar.file_uploader("Suba sua planilha (CSV ou Excel)", type=["csv", "xlsx"])

lista_acoes = []

if uploaded_file is not None:
    try:
        # Lê o arquivo dependendo da extensão
        if uploaded_file.name.endswith('.csv'):
            df_user = pd.read_csv(uploaded_file)
        else:
            df_user = pd.read_excel(uploaded_file)
        
        # Pega todos os valores da primeira coluna da planilha
        primeira_coluna = df_user.columns[0]
        lista_acoes = df_user[primeira_coluna].dropna().astype(str).tolist()
        st.sidebar.success(f"{len(lista_acoes)} ativos carregados da planilha!")
    except Exception as e:
        st.sidebar.error("Erro ao ler o arquivo. Certifique-se de que é uma tabela válida.")
else:
    st.sidebar.info("Nenhuma planilha enviada. Usando lista de teste padrão.")
    lista_acoes = ["PETR4.SA", "VALE3.SA", "WEGE3.SA", "ITUB4.SA", "BBDC4.SA"]

# Botão de Execução
if st.sidebar.button("Executar Análise"):
    st.info("Analisando o mercado... Isso pode levar alguns segundos dependendo da quantidade de ativos.")
    
    # Adicionando uma barra de progresso visual
    progress_bar = st.progress(0)
    resultados_finais = []
    
    for i, acao in enumerate(lista_acoes):
        # Limpa o texto: tira espaços, deixa maiúsculo, tira o $ e troca .BR por .SA
        acao_limpa = str(acao).strip().upper().replace('$', '').replace('.BR', '.SA')
        
        # Se a ação veio sem o .SA (ex: apenas PETR4), adicionamos automaticamente
        if not acao_limpa.endswith('.SA') and not acao_limpa.endswith('.US'): 
            acao_limpa = f"{acao_limpa}.SA"

        analise = analisar_ativo(acao_limpa)
        if analise:
            resultados_finais.append(analise)
        
        # Atualiza a barra a cada ação analisada
        progress_bar.progress((i + 1) / len(lista_acoes))
        
    if resultados_finais:
        st.success("Análise concluída com sucesso!")
        tabela = pd.DataFrame(resultados_finais)
        
        # --- NOVA FUNÇÃO DE ESTILO ---
        def colorir_status(valor):
            """Define as cores baseadas no texto da célula"""
            if valor == "APROVADO":
                # Fundo verde claro, texto verde escuro e negrito
                return "color: #155724; font-weight: bold;"
            elif valor == "DESCARTADO":
                # Fundo vermelho claro, texto vermelho escuro e negrito
                return "color: #721c24; font-weight: bold;"
            return ""

        # Aplicamos o estilo na coluna 'Status'. 
        # (Usamos um try/except porque o pandas mudou de 'applymap' para 'map' nas versões mais recentes)
        try:
            tabela_estilizada = tabela.style.map(colorir_status, subset=['Status'])
        except AttributeError:
            tabela_estilizada = tabela.style.applymap(colorir_status, subset=['Status'])
        
        # Exibe a tabela interativa já colorida na página web
        st.dataframe(tabela_estilizada, use_container_width=True)
    else:
        st.warning("Nenhum ativo retornou dados válidos.")