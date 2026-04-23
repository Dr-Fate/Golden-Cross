import pandas as pd

def calculate_sma(data, window):
    """Calcula la Media Móvil Simple (SMA) para una ventana dada."""
    return data['Close'].rolling(window=window).mean()

def generate_signals(data, short_window=50, long_window=200):
    """
    Genera señales de compra (1) y venta (-1) basadas en el cruce de SMAs.
    Golden Cross: SMA corta cruza por encima de SMA larga.
    Death Cross: SMA corta cruza por debajo de SMA larga.
    """
    signals = pd.DataFrame(index=data.index)
    signals['Signal'] = 0.0

    # Calcular SMAs
    signals['SMA_Short'] = calculate_sma(data, short_window)
    signals['SMA_Long'] = calculate_sma(data, long_window)

    # Crear señales
    # 1.0 cuando la corta es mayor que la larga
    signals.loc[signals.index[short_window:], 'Signal'] = [1.0 if signals['SMA_Short'].iloc[i] > signals['SMA_Long'].iloc[i] else 0.0
                                                 for i in range(short_window, len(signals))]

    # Identificar el cruce (la diferencia entre señales consecutivas)
    signals['Position'] = signals['Signal'].diff()

    return signals
