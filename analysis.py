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

    # Crear señales con filtro de sensibilidad (0.1% del precio actual)
    # 1.0 cuando la corta es mayor que la larga + margen
    # Mantener el estado anterior si la diferencia está dentro del margen para evitar ruido
    current_signal = 0.0
    signal_list = []

    for i in range(len(data)):
        if i < long_window:
            signal_list.append(0.0)
            continue

        sma_short = signals['SMA_Short'].iloc[i]
        sma_long = signals['SMA_Long'].iloc[i]
        price = data['Close'].iloc[i]
        threshold = price * 0.005 # 0.5% del precio (Baja Frecuencia)

        if sma_short > (sma_long + threshold):
            current_signal = 1.0
        elif sma_short < (sma_long - threshold):
            current_signal = 0.0

        signal_list.append(current_signal)

    signals['Signal'] = signal_list

    # Identificar el cruce (la diferencia entre señales consecutivas)
    signals['Position'] = signals['Signal'].diff()

    return signals
