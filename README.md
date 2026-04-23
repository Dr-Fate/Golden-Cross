# Simulador de Gestión de Portafolio y Análisis Golden Cross

Este proyecto es un simulador de trading y gestión de portafolio basado en la estrategia técnica **Golden Cross** (Cruce Dorado). Permite realizar backtesting sobre datos históricos de acciones para evaluar el rendimiento de la estrategia.

## Características

- **Análisis Técnico**: Cálculo de Medias Móviles Simples (SMA) de corto y largo plazo.
- **Detección de Señales**: Identificación automática de *Golden Cross* (señal de compra) y *Death Cross* (señal de venta).
- **Gestión de Portafolio**: Seguimiento de saldo en efectivo, tenencia de activos y registro de transacciones.
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
   python simulator.py
   ```

## Estrategia Golden Cross

La estrategia utiliza dos medias móviles:
- **SMA 50**: Media móvil simple de 50 días (corto plazo).
- **SMA 200**: Media móvil simple de 200 días (largo plazo).

Se genera una **señal de compra** cuando la SMA 50 cruza por encima de la SMA 200.
Se genera una **señal de venta** cuando la SMA 50 cruza por debajo de la SMA 200.
