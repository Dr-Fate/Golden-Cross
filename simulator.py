import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from analysis import generate_signals
from portfolio import Portfolio

def run_simulation(ticker, start_date, end_date):
    print(f"Descargando datos para {ticker} desde {start_date} hasta {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        print("No se encontraron datos.")
        return

    # Aplanar MultiIndex si existe (yfinance v0.2.x+)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Generar señales
    signals = generate_signals(data)

    # Inicializar portafolio
    portfolio = Portfolio(initial_cash=10000.0)

    # Simulación paso a paso
    portfolio_values = []

    for i in range(len(data)):
        current_date = data.index[i]
        current_price = float(data['Close'].iloc[i])

        # Obtener señal de hoy
        position_change = signals['Position'].iloc[i]

        if position_change == 1.0: # Golden Cross -> Buy
            portfolio.buy(current_date, current_price)
        elif position_change == -1.0: # Death Cross -> Sell
            portfolio.sell(current_date, current_price)

        # Actualizar y guardar valor total
        total_val = portfolio.update_value(current_price)
        portfolio_values.append(float(total_val))

    # Añadir valores al dataframe para visualización
    data['Portfolio_Value'] = portfolio_values

    # Mostrar resultados finales
    print("\nResumen de Simulación:")
    print(f"Saldo Inicial: ${portfolio.initial_cash:,.2f}")
    print(f"Saldo Final: ${portfolio.total_value:,.2f}")
    print(f"Rendimiento Total: {((portfolio.total_value / portfolio.initial_cash) - 1) * 100:.2f}%")
    print(f"Número de operaciones: {len(portfolio.history)}")

    return data, signals, portfolio

def plot_results(data, signals, ticker):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Gráfico de Precios y Medias Móviles
    ax1.plot(data.index, data['Close'], label='Precio de Cierre', alpha=0.5)
    ax1.plot(signals.index, signals['SMA_Short'], label='SMA 50 (Corta)', alpha=0.8)
    ax1.plot(signals.index, signals['SMA_Long'], label='SMA 200 (Larga)', alpha=0.8)

    # Marcar Compras y Ventas
    ax1.plot(signals.loc[signals.Position == 1.0].index,
             signals.SMA_Short[signals.Position == 1.0],
             '^', markersize=10, color='g', label='Compra (Golden Cross)')

    ax1.plot(signals.loc[signals.Position == -1.0].index,
             signals.SMA_Short[signals.Position == -1.0],
             'v', markersize=10, color='r', label='Venta (Death Cross)')

    ax1.set_title(f'Análisis Golden Cross para {ticker}')
    ax1.set_ylabel('Precio ($)')
    ax1.legend()
    ax1.grid()

    # Gráfico de Valor del Portafolio
    ax2.plot(data.index, data['Portfolio_Value'], label='Valor del Portafolio', color='orange')
    ax2.set_title('Evolución del Valor del Portafolio')
    ax2.set_ylabel('Valor Total ($)')
    ax2.set_xlabel('Fecha')
    ax2.legend()
    ax2.grid()

    plt.tight_layout()
    plt.savefig(f'resultados_{ticker}.png')
    print(f"\nGráfico guardado como 'resultados_{ticker}.png'")
    # plt.show() # Desactivado para entorno sin display

if __name__ == "__main__":
    ticker_input = "AAPL" # Ejemplo predeterminado
    data, signals, portfolio = run_simulation(ticker_input, "2020-01-01", "2023-01-01")
    if data is not None:
        plot_results(data, signals, ticker_input)
