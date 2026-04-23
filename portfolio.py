class Portfolio:
    def __init__(self, initial_cash=10000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.holdings = 0
        self.position_value = 0
        self.total_value = initial_cash
        self.history = []

    def buy(self, date, price, quantity=None):
        """Compra activos con el efectivo disponible o una cantidad específica."""
        if quantity is None:
            quantity = self.cash // price

        cost = quantity * price
        if cost <= self.cash and quantity > 0:
            self.cash -= cost
            self.holdings += quantity
            self.history.append({'Date': date, 'Type': 'BUY', 'Price': price, 'Quantity': quantity, 'Cash': self.cash})
            return True
        return False

    def sell(self, date, price, quantity=None):
        """Vende los activos en cartera."""
        if quantity is None:
            quantity = self.holdings

        if quantity > 0 and quantity <= self.holdings:
            revenue = quantity * price
            self.cash += revenue
            self.holdings -= quantity
            self.history.append({'Date': date, 'Type': 'SELL', 'Price': price, 'Quantity': quantity, 'Cash': self.cash})
            return True
        return False

    def update_value(self, current_price):
        """Actualiza el valor total del portafolio basado en el precio actual."""
        self.position_value = self.holdings * current_price
        self.total_value = self.cash + self.position_value
        return self.total_value
