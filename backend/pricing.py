def adjust_price(predicted_price, demand):
    if demand > 150:
        return predicted_price + 10
    else:
        return predicted_price - 10