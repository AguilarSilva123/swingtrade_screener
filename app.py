import yfinance as yf
import pandas as pd
import pandas_ta as ta
from scipy.signal import find_peaks

def analisar_ativo(ticker_symbol):
    print(f"Analisando {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    
    # 1. Baixando os dados (Agora incluindo os 60 minutos)
    df_semanal = ticker.history(period="2y", interval="1wk")
    df_diario = ticker.history(period="1y", interval="1d")
    # Para 60 minutos, 1 mês de histórico (1mo) é mais do que suficiente para achar o último topo/fundo
    df_60m = ticker.history(period="1mo", interval="60m")
    
    if df_semanal.empty or df_diario.empty or df_60m.empty:
        print(f"Erro: Dados insuficientes para {ticker_symbol}")
        return None

    # 2. Calculando a Tendência (Filtro Macro)
    df_semanal['EMA_72'] = ta.ema(df_semanal['Close'], length=72)
    preco_atual = df_diario['Close'].iloc[-1]
    ema_72_sem_atual = df_semanal['EMA_72'].iloc[-1]
    
    if pd.isna(ema_72_sem_atual):
        return None

    tendencia_alta = preco_atual > ema_72_sem_atual

    # 3. Encontrando Topos e Fundos nos 60 Minutos
    # distance=3 significa que um topo precisa estar a pelo menos 3 candles de distância do próximo
    topos_indices, _ = find_peaks(df_60m['High'], distance=3)
    
    # Multiplicamos por -1 para a função achar os "picos invertidos" (fundos)
    fundos_indices, _ = find_peaks(-df_60m['Low'], distance=3) 

    # Se a função não achou nenhum topo ou fundo, descartamos
    if len(topos_indices) == 0 or len(fundos_indices) == 0:
        print(f"Aviso: Não foi possível identificar topos/fundos em {ticker_symbol}.")
        return None

    # Pegando o ÚLTIMO topo e o ÚLTIMO fundo (o índice -1 da lista)
    ultimo_topo = df_60m['High'].iloc[topos_indices[-1]]
    ultimo_fundo = df_60m['Low'].iloc[fundos_indices[-1]]

    # 4. Organizando o resultado
    resultado = {
        "Ticker": ticker_symbol,
        "Preço Atual": round(preco_atual, 2),
        "Tendência": "ALTA" if tendencia_alta else "BAIXA",
        "Último Topo (60m)": round(ultimo_topo, 2),
        "Último Fundo (60m)": round(ultimo_fundo, 2)
    }
    
    return resultado

if __name__ == "__main__":
    # Testando com a Petrobras
    analise = analisar_ativo("PETR4.SA")
    
    print("\n--- Resultado da Análise (Dia 3) ---")
    if analise:
        for chave, valor in analise.items():
            print(f"{chave}: {valor}")