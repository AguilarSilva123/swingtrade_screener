import yfinance as yf
import pandas as pd

def testar_conexao():
    print("Conectando ao Yahoo Finance...")
    
    # Baixando dados da Petrobras (PETR4.SA)
    ticker = yf.Ticker("PETR4.SA")
    
    # Pegando os últimos 5 dias no tempo gráfico diário
    dados = ticker.history(period="5d", interval="1d")
    
    if not dados.empty:
        print("Sucesso! Aqui estão os últimos dias da PETR4:")
        print(dados[['Open', 'High', 'Low', 'Close']])
    else:
        print("Falha ao baixar os dados.")

if __name__ == "__main__":
    testar_conexao()