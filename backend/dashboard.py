import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt

def plot_prices(prices):
    plt.figure()
    plt.plot(prices)
    plt.title("Price Trend")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.savefig("price_plot.png")   
    plt.close()