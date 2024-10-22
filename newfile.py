import kivy
kivy.require('2.2.1')  # Ensure you have the correct version of Kivy

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

# Sample data
data = {
    'Date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
    'Open': pd.np.random.uniform(low=100, high=200, size=100),
    'High': pd.np.random.uniform(low=200, high=300, size=100),
    'Low': pd.np.random.uniform(low=50, high=100, size=100),
    'Close': pd.np.random.uniform(low=100, high=200, size=100),
    'Volume': pd.np.random.randint(low=1000, high=10000, size=100)
}
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

class TradingApp(App):
    def build(self):
        layout = FloatLayout()

        # Create a button to update the chart
        button = Button(text='Update Chart', size_hint=(0.2, 0.1), pos_hint={'x': 0.4, 'y': 0.9})
        button.bind(on_press=self.update_chart)
        layout.add_widget(button)

        # Add a placeholder for the chart
        self.chart_placeholder = FloatLayout(size_hint=(1, 0.9))
        layout.add_widget(self.chart_placeholder)

        return layout

    def update_chart(self, instance):
        # Clear existing chart
        self.chart_placeholder.clear_widgets()

        # Create a new figure and axis
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot the candlestick chart
        mpf.plot(df, type='candle', ax=ax, style='charles', title='Candlestick Chart', returnfig=True)

        # Convert the Matplotlib figure to Kivy
        canvas = FigureCanvasKivyAgg(fig)
        self.chart_placeholder.add_widget(canvas)

if __name__ == '__main__':
    TradingApp().run()
