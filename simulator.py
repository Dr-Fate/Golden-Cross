import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, timedelta
from analysis import generate_signals
from portfolio import Portfolio

WATCHLIST_FILE = "watchlist.json"
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"SCANNER_LIST": []}

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    return []

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=4)

def get_company_name(ticker_symbol):
    """Obtiene el nombre de la empresa o alias del activo. Retorna None si no se encuentra."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        if not info or 'symbol' not in info:
            return None

        # Intentar obtener el nombre más descriptivo disponible
        name = info.get('longName') or info.get('shortName')
        return name
    except Exception:
        return None

def calculate_cagr(total_return, start_date, end_date):
    """Calcula la Tasa de Crecimiento Anual Compuesta (CAGR)."""
    years = (end_date - start_date).days / 365.25
    if years <= 0:
        return 0
    return (abs(total_return + 1) ** (1 / years)) - 1

def run_simulation(ticker, start_date, end_date, silent=False):
    if not silent:
        print(f"Descargando datos para {ticker} desde {start_date} hasta {end_date}...")

    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    except Exception as e:
        if not silent:
            print(f"Error al descargar datos para {ticker}: {e}")
        return None, None, None, 0.0

    if data is None or data.empty:
        if not silent:
            print(f"No se encontraron datos para {ticker}.")
        return None, None, None, 0.0

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # --- ESTRATEGIA GOLDEN CROSS ---
    signals = generate_signals(data)
    portfolio = Portfolio(initial_cash=10000.0)
    portfolio_values = []
    peak_value = portfolio.initial_cash
    max_drawdown = 0.0

    for i in range(len(data)):
        current_date = data.index[i]
        current_price = float(data['Close'].iloc[i])
        position_change = signals['Position'].iloc[i]

        if position_change == 1.0:
            portfolio.buy(current_date, current_price)
        elif position_change == -1.0:
            portfolio.sell(current_date, current_price)

        total_val = portfolio.update_value(current_price)
        portfolio_values.append(float(total_val))

        if total_val > peak_value:
            peak_value = total_val
        drawdown = (total_val - peak_value) / peak_value
        if drawdown < max_drawdown:
            max_drawdown = drawdown

    data['Portfolio_Value'] = portfolio_values

    # --- BENCHMARK BUY & HOLD ---
    bh_portfolio = Portfolio(initial_cash=10000.0)
    bh_values = []
    # Compra al inicio
    bh_portfolio.buy(data.index[0], float(data['Close'].iloc[0]))
    bh_peak = bh_portfolio.initial_cash
    bh_max_drawdown = 0.0

    for i in range(len(data)):
        price = float(data['Close'].iloc[i])
        val = bh_portfolio.update_value(price)
        bh_values.append(float(val))
        if val > bh_peak:
            bh_peak = val
        dd = (val - bh_peak) / bh_peak
        if dd < bh_max_drawdown:
            bh_max_drawdown = dd

    data['Buy_Hold_Value'] = bh_values

    # Cálculos finales
    years = (data.index[-1] - data.index[0]).days / 365.25
    total_return = (portfolio.total_value / portfolio.initial_cash) - 1
    cagr = calculate_cagr(total_return, data.index[0], data.index[-1])

    bh_total_return = (bh_portfolio.total_value / bh_portfolio.initial_cash) - 1
    bh_cagr = calculate_cagr(bh_total_return, data.index[0], data.index[-1])

    if not silent:
        print("\n" + "="*40)
        print(f" RESUMEN DE SIMULACIÓN: {ticker}")
        print("="*40)
        print(f"{'Métrica':<20} | {'Estrategia':<10} | {'Buy & Hold':<10}")
        print("-" * 45)
        print(f"{'Retorno Total':<20} | {total_return*100:>9.2f}% | {bh_total_return*100:>9.2f}%")
        print(f"{'CAGR':<20} | {cagr*100:>9.2f}% | {bh_cagr*100:>9.2f}%")
        print(f"{'Máximo Drawdown':<20} | {max_drawdown*100:>9.2f}% | {bh_max_drawdown*100:>9.2f}%")
        print(f"{'Operaciones':<20} | {len(portfolio.history):>10} | {len(bh_portfolio.history):>10}")
        print("="*40)

        # Logging de trades
        if len(portfolio.history) > 0:
            print("\nRegistro de Operaciones (Estrategia):")
            for h in portfolio.history:
                print(f"- {h['Date'].date()} {h['Type']:>4}: ${h['Price']:>8.2f} | Comis: ${h['Commission']:>6.2f} | Saldo: ${h['Cash']:>10.2f}")

    return data, signals, portfolio, max_drawdown

def plot_results(data, signals, ticker, company_name):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    ax1.plot(data.index, data['Close'], label='Precio de Cierre', alpha=0.5)
    ax1.plot(signals.index, signals['SMA_Short'], label='SMA 50 (Corta)', alpha=0.8)
    ax1.plot(signals.index, signals['SMA_Long'], label='SMA 200 (Larga)', color='darkgreen', alpha=0.8)

    ax1.plot(signals.loc[signals.Position == 1.0].index,
             signals.SMA_Short[signals.Position == 1.0],
             '^', markersize=10, color='g', label='Compra (Golden Cross)')

    ax1.plot(signals.loc[signals.Position == -1.0].index,
             signals.SMA_Short[signals.Position == -1.0],
             'v', markersize=10, color='r', label='Venta (Death Cross)')

    ax1.set_title(f'Análisis Golden Cross para {company_name} ({ticker})')
    ax1.set_ylabel('Precio ($)')
    ax1.legend()
    ax1.grid()

    # Ajustar margen derecho para ver marcadores de hoy
    if len(data) > 0:
        xlim_left, xlim_right = ax1.get_xlim()
        ax1.set_xlim(xlim_left, xlim_right + (xlim_right - xlim_left) * 0.05)

    ax2.plot(data.index, data['Portfolio_Value'], label='Estrategia Golden Cross', color='orange', linewidth=2)
    ax2.plot(data.index, data['Buy_Hold_Value'], label='Buy & Hold', color='gray', linestyle='--', alpha=0.7)
    ax2.set_title('Curva de Equity: Estrategia vs Buy & Hold')
    ax2.set_ylabel('Valor Total ($)')
    ax2.set_xlabel('Fecha')
    ax2.legend()
    ax2.grid()

    plt.tight_layout()
    filename = f'resultados_{ticker}.png'
    plt.savefig(filename)
    print(f"\nGráfico guardado como '{filename}'")
    plt.show()

def display_watchlist(watchlist):
    if not watchlist:
        print("\nLa watchlist está vacía.")
        return False

    print("\n--- Watchlist Actual ---")
    for i, item in enumerate(watchlist, 1):
        print(f"{i}. {item['ticker']} - {item['name']}")
    return True

def show_current_signals(watchlist):
    if not watchlist:
        print("\nNo hay activos para analizar.")
        return

    print("\n--- Estado de Señales Actuales ---")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365) # Suficiente para SMA 200

    for item in watchlist:
        ticker = item['ticker']
        # Usar silent=True para no llenar la consola de logs de descarga
        _, signals, _, mdd = run_simulation(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), silent=True)

        if signals is not None and len(signals) > 0:
            last_signal = signals['Signal'].iloc[-1]
            last_pos = signals['Position'].iloc[-1]

            # Buscar cuándo fue la última señal (Position != 0)
            signal_dates = signals[signals['Position'] != 0].index
            days_msg = ""
            warning = ""
            if not signal_dates.empty:
                last_signal_date = signal_dates[-1]
                days_passed = (datetime.now().date() - last_signal_date.date()).days
                days_msg = f" - Señal original hace {days_passed} días."
                if days_passed > 10:
                    warning = " (Fuera de margen ideal)"

            status = "NEUTRAL"
            if last_pos == 1.0:
                status = "¡SEÑAL DE COMPRA HOY! (Golden Cross)"
            elif last_pos == -1.0:
                # Si last_signal es 0 ahora, significa que antes era 1. Pero si no tenemos acciones...
                # La lógica de compra/venta es binaria aquí.
                # Si la señal previa era 1 y ahora es 0, es venta.
                status = "¡SEÑAL DE VENTA HOY! (Death Cross)"
                if signals['Signal'].iloc[-2] == 0: # Caso borde: no veníamos de compra
                     status = "MANTENERSE FUERA (Confirmación de tendencia bajista)"
            elif last_signal == 1.0:
                status = "MANTENER (Tendencia Alcista)"
            else:
                status = "FUERA DEL MERCADO (Tendencia Bajista)"

            print(f"{ticker} ({item['name']}): {status}{days_msg}{warning}")
        else:
            print(f"{ticker} ({item['name']}): Error al obtener datos")

def run_scanner(watchlist):
    config = load_config()
    scanner_list = config.get("SCANNER_LIST", [])
    if not scanner_list:
        print("\nNo hay activos configurados para escanear.")
        return

    print(f"\n--- Escaneando Mercado ({len(scanner_list)} activos) ---")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    found_assets = []
    scanned_successfully = []

    for ticker in scanner_list:
        try:
            _, signals, _, _ = run_simulation(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), silent=True)
            if signals is not None and len(signals) > 0:
                name = get_company_name(ticker) or ticker
                # Buscar señales en los últimos 5 días
                signals_only = signals[signals['Position'] != 0]
                recent_signals = signals_only[signals_only.index >= (end_date - timedelta(days=5))]
                if not recent_signals.empty:
                    last_pos = recent_signals['Position'].iloc[-1]
                    last_date = recent_signals.index[-1]
                    days_passed = (datetime.now().date() - last_date.date()).days

                    status = "COMPRA" if last_pos == 1.0 else "VENTA"
                    print(f"[*] {ticker} ({name}): Señal de {status} detectada hace {days_passed} días.")

                    if not any(item['ticker'] == ticker for item in watchlist):
                        found_assets.append({"ticker": ticker, "name": name})

                scanned_successfully.append(f"{ticker} ({name})")
        except Exception as e:
            print(f"[!] Error escaneando {ticker}: {e}")

    if found_assets:
        print(f"\nSe encontraron {len(found_assets)} activos con señales recientes que NO están en tu watchlist.")
        ans = input("¿Deseas agregarlos todos a tu watchlist permanente? (s/n): ").lower()
        if ans == 's':
            watchlist.extend(found_assets)
            save_watchlist(watchlist)
            print("Activos agregados con éxito.")
    else:
        print("\nNo se encontraron nuevas señales recientes en los activos escaneados.")
        if scanned_successfully:
            print(f"Mercados analizados: {', '.join(scanned_successfully)}")

def main_menu():
    watchlist = load_watchlist()

    while True:
        print("\n========================================")
        print("  SIMULADOR DE GESTIÓN DE PORTAFOLIO  ")
        print("========================================")
        print("1. Ver Watchlist y Señales de Hoy")
        print("2. Analizar Activo (Backtesting)")
        print("3. [+] Agregar acción")
        print("4. [-] Eliminar acción")
        print("5. Escanear Mercado (Radar)")
        print("6. Salir")

        choice = input("\nSeleccione una opción: ")

        if choice == '1':
            if display_watchlist(watchlist):
                show_current_signals(watchlist)

        elif choice == '2':
            if display_watchlist(watchlist):
                idx = input("\nIngrese el número del activo para analizar (o '0' para volver): ")
                if idx == '0' or not idx:
                    continue

                if idx.isdigit():
                    i = int(idx) - 1
                    if 0 <= i < len(watchlist):
                        ticker_to_run = watchlist[i]['ticker']
                        name_to_run = watchlist[i]['name']
                    else:
                        print("Número fuera de rango.")
                        continue
                else:
                    ticker_to_run = idx.upper()
                    name_to_run = get_company_name(ticker_to_run) or ticker_to_run

                sim_data, sim_signals, sim_portfolio, _ = run_simulation(
                    ticker_to_run, "2020-01-01", datetime.now().strftime('%Y-%m-%d')
                )
                if sim_data is not None and sim_signals is not None:
                    plot_results(sim_data, sim_signals, ticker_to_run, name_to_run)

        elif choice == '3':
            new_ticker = input("\nIngrese el ticker del nuevo activo (o Intro para volver): ").upper()
            if not new_ticker:
                continue

            if any(item['ticker'] == new_ticker for item in watchlist):
                print(f"{new_ticker} ya está en la watchlist.")
            else:
                print(f"Verificando {new_ticker} en Yahoo Finance...")
                name = get_company_name(new_ticker)
                if name:
                    watchlist.append({"ticker": new_ticker, "name": name})
                    save_watchlist(watchlist)
                    print(f"Agregado con éxito: {new_ticker} - {name}")
                else:
                    print(f"Error: No se pudo encontrar el activo '{new_ticker}'. Verifique el ticker e intente de nuevo.")

        elif choice == '4':
            if display_watchlist(watchlist):
                idx = input("\nIngrese el número del activo a eliminar (o '0' para volver): ")
                if idx == '0' or not idx:
                    continue

                if idx.isdigit():
                    i = int(idx) - 1
                    if 0 <= i < len(watchlist):
                        removed = watchlist.pop(i)
                        save_watchlist(watchlist)
                        print(f"Eliminado: {removed['ticker']}")
                    else:
                        print("Número fuera de rango.")
                else:
                    print("Por favor, ingrese un número válido.")

        elif choice == '5':
            run_scanner(watchlist)

        elif choice == '6':
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main_menu()
