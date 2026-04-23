# Simulador de Gestión de Portafolio y Análisis Golden Cross

Este proyecto es un simulador de trading y gestión de portafolio basado en la estrategia técnica **Golden Cross** (Cruce Dorado). Permite realizar backtesting sobre datos históricos de acciones para evaluar el rendimiento de la estrategia.

## Características

- **Watchlist Dinámica**: Sistema de seguimiento de activos con persistencia en `watchlist.json`.
- **Mapeo de Nombres**: Obtención automática del nombre real de la empresa/activo vía Yahoo Finance.
- **Interfaz Numerada**: Menú interactivo que permite seleccionar activos por su índice.
- **Estado de Señales**: Reporte instantáneo del estado de compra/venta para el día de hoy en todos los activos de la watchlist.
- **Análisis Técnico**: Cálculo de Medias Móviles Simples (SMA) de corto y largo plazo.
- **Backtesting**: Simulación de ejecución de trades basada en datos históricos reales.
- **Visualización**: Gráficos de precios, medias móviles y puntos de ejecución de compra/venta.

## Requisitos

- Python 3.x
- Bibliotecas: `yfinance`, `pandas`, `matplotlib`

## Uso

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el simulador:
   ```bash
   python3 simulator.py
   ```
3. Sigue las instrucciones del menú interactivo para agregar acciones, ver señales de hoy o realizar un backtesting detallado.

## Estrategia Golden Cross

La estrategia utiliza dos medias móviles:
- **SMA 50**: Media móvil simple de 50 días (corto plazo).
- **SMA 200**: Media móvil simple de 200 días (largo plazo).

Se genera una **señal de compra** cuando la SMA 50 cruza por encima de la SMA 200.
Se genera una **señal de venta** cuando la SMA 50 cruza por debajo de la SMA 200.
