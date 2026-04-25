class Portfolio:
    def __init__(self, initial_cash=10000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.holdings = 0
        self.position_value = 0
        self.total_value = initial_cash
        self.history = []

    def calculate_commission(self, trade_value):
        """Calcula la comisión: 0.75% con un mínimo de $10."""
        return max(0.0075 * trade_value, 10.0)

    def buy(self, date, price, quantity=None):
        """Compra activos considerando comisiones."""
        if quantity is None:
            # Reservar efectivo para la comisión mínima aproximada
            available_cash = self.cash - 10.0
            if available_cash < 0:
                return False
            quantity = available_cash // (price * 1.0075)

        trade_value = quantity * price
        commission = self.calculate_commission(trade_value)
        total_cost = trade_value + commission

        if total_cost <= self.cash and quantity > 0:
            self.cash -= total_cost
            self.holdings += quantity
            self.history.append({
                'Date': date, 'Type': 'BUY', 'Price': price,
                'Quantity': quantity, 'Commission': commission, 'Cash': self.cash
            })
            return True
        return False

    def sell(self, date, price, quantity=None):
        """Vende los activos considerando comisiones."""
        if quantity is None:
            quantity = self.holdings

        if quantity > 0 and quantity <= self.holdings:
            trade_value = quantity * price
            commission = self.calculate_commission(trade_value)
            net_revenue = trade_value - commission

            self.cash += net_revenue
            self.holdings -= quantity
            self.history.append({
                'Date': date, 'Type': 'SELL', 'Price': price,
                'Quantity': quantity, 'Commission': commission, 'Cash': self.cash
            })
            return True
        return False

    def update_value(self, current_price):
        """Actualiza el valor total del portafolio basado en el precio actual."""
        self.position_value = self.holdings * current_price
        self.total_value = self.cash + self.position_value
        return self.total_value
