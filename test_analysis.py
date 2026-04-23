import unittest
import pandas as pd
from analysis import calculate_sma, generate_signals

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        # Crear datos de prueba: 300 días de precios crecientes
        dates = pd.date_range(start='2020-01-01', periods=300)
        self.data = pd.DataFrame({'Close': range(300)}, index=dates)

    def test_calculate_sma(self):
        sma_10 = calculate_sma(self.data, 10)
        self.assertEqual(len(sma_10), 300)
        self.assertTrue(pd.isna(sma_10.iloc[8]))
        self.assertFalse(pd.isna(sma_10.iloc[9]))
        # La media de 0..9 es 4.5
        self.assertAlmostEqual(sma_10.iloc[9], 4.5)

    def test_generate_signals(self):
        # Con precios crecientes, SMA_Short (50) siempre será mayor que SMA_Long (200)
        # después de que ambas se calculen.
        signals = generate_signals(self.data, short_window=50, long_window=200)

        # En el día 200 (índice 199), la SMA_Short es la media de 150..199
        # La SMA_Long es la media de 0..199
        # Por lo tanto SMA_Short > SMA_Long
        self.assertEqual(signals['Signal'].iloc[199], 1.0)

        # El primer cruce (Position == 1) debería ocurrir en el índice 199 (primer día con SMA_Long)
        self.assertEqual(signals['Position'].iloc[199], 1.0)

if __name__ == '__main__':
    unittest.main()
