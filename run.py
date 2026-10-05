from app.models import Cut, Stock
from app.optimizer import expand_cuts

cut=Cut(10.5, 3)
stock=Stock(20.0, 5)
cuts=[
    Cut(10.5, 3),
    Cut(5.0,2)
]
    
expanded=expand_cuts(cuts)
print(cut.length)
print(cut.quanity)
print(stock.length)
print(stock.quanity)
print(expanded)
