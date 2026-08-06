import yfinance as yf
import pandas as pd
import pandas_ta as ta
from scipy.signal import find_peaks

def analisar_ativo(ticker_symbol):
    print(f"Analisando {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    
    # 1. Baixando os dados
    df_semanal = ticker.history(period="2y", interval="1wk")
    df_diario = ticker.history(period="1y", interval="1d")
    df_60m = ticker.history(period="1mo", interval="60m")
    
    if df_semanal.empty or df_diario.empty or df_60m.empty:
        return None

    # 2. Calculando a Tendência (Filtro Macro)
    df_semanal['EMA_72'] = ta.ema(df_semanal['Close'], length=72)
    preco_atual = df_diario['Close'].iloc[-1]
    ema_72_sem_atual = df_semanal['EMA_72'].iloc[-1]
    
    if pd.isna(ema_72_sem_atual):
        return None

    tendencia_alta = preco_atual > ema_72_sem_atual

    # 3. Encontrando Topos e Fundos nos 60 Minutos
    topos_indices, _ = find_peaks(df_60m['High'], distance=3)
    fundos_indices, _ = find_peaks(-df_60m['Low'], distance=3) 

    if len(topos_indices) == 0 or len(fundos_indices) == 0:
        return None

    ultimo_topo = df_60m['High'].iloc[topos_indices[-1]]
    ultimo_fundo = df_60m['Low'].iloc[fundos_indices[-1]]

    # 4. Matemática do Trade (Gerenciamento de Risco)
    # Entrada um centavo acima do topo e Stop um centavo abaixo do fundo
    entrada = ultimo_topo + 0.01
    stop_loss = ultimo_fundo - 0.01
    
    # Risco assumido na operação e Alvo (3 vezes o risco)
    risco = entrada - stop_loss
    alvo = entrada + (risco * 3)

    # 5. O Veredito
    # Para compras, só aprovamos se a tendência semanal for de ALTA
    status = "APROVADO" if tendencia_alta else "DESCARTADO"

    # Organizando o resultado final
    resultado = {
        "Ticker": ticker_symbol,
        "Status": status,
        "Preço Atual": round(preco_atual, 2),
        "Entrada": round(entrada, 2),
        "Stop Loss": round(stop_loss, 2),
        "Alvo (1:3)": round(alvo, 2)
    }
    
    return resultado

if __name__ == "__main__":
    # Nossa lista de teste (aqui no futuro entrará a leitura da sua planilha)
    lista_acoes = ["PETR4.SA", "VALE3.SA", "WEGE3.SA", "ITUB4.SA", "BBDC4.SA"]
    resultados_finais = []

    print("\nIniciando o Screener de Swing Trade...\n")
    
    for acao in lista_acoes:
        analise = analisar_ativo(acao)
        if analise:
            resultados_finais.append(analise)
            
    # Transformando a lista de resultados em uma tabela (DataFrame) do Pandas para visualização
    if resultados_finais:
        tabela = pd.DataFrame(resultados_finais)
        print("\n--- Relatório Final de Estratégia ---")
        # Imprime a tabela sem o índice lateral para ficar mais limpo
        print(tabela.to_string(index=False))
    else:
        print("Nenhum ativo retornou dados válidos.")