import yfinance as yf
import pandas as pd
import pandas_ta as ta

def obter_dados_e_tendencia(ticker_symbol):
    print(f"Analisando {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    
    # 1. Baixando os dados
    # Para a média de 72 semanas, precisamos de bastante histórico (2 anos)
    df_semanal = ticker.history(period="2y", interval="1wk")
    # Para o diário, 1 ano é suficiente
    df_diario = ticker.history(period="1y", interval="1d")
    
    if df_semanal.empty or df_diario.empty:
        print(f"Erro: Não foi possível baixar os dados de {ticker_symbol}")
        return None

    # 2. Calculando as Médias Móveis Exponenciais (EMA)
    # A biblioteca pandas_ta adiciona essas colunas magicamente no nosso dataframe
    df_semanal['EMA_72'] = ta.ema(df_semanal['Close'], length=72)
    df_diario['EMA_17'] = ta.ema(df_diario['Close'], length=17)
    df_diario['EMA_72'] = ta.ema(df_diario['Close'], length=72)

    # 3. Pegando os valores mais recentes (o último candle da tabela)
    preco_atual = df_diario['Close'].iloc[-1]
    ema_72_sem_atual = df_semanal['EMA_72'].iloc[-1]
    
    # Prevenção de erro caso o ativo seja muito novo e não tenha 72 semanas de vida
    if pd.isna(ema_72_sem_atual):
        print(f"Aviso: {ticker_symbol} não tem histórico suficiente para a EMA 72.")
        return None

    # 4. Aplicando o Filtro da Estratégia (Tendência de Alta)
    # O preço precisa estar acima da Média de 72 no gráfico semanal
    tendencia_alta = preco_atual > ema_72_sem_atual

    # 5. Organizando o resultado
    resultado = {
        "Ticker": ticker_symbol,
        "Preço Atual": round(preco_atual, 2),
        "EMA 72 Semanal": round(ema_72_sem_atual, 2),
        "Tendência de Alta": "Aprovado" if tendencia_alta else "Reprovado"
    }
    
    return resultado

if __name__ == "__main__":
    # Testando com a Petrobras
    analise = obter_dados_e_tendencia("PETR4.SA")
    
    print("\n--- Resultado da Análise ---")
    for chave, valor in analise.items():
        print(f"{chave}: {valor}")