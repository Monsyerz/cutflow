from app.models import Cut, Stock
from app.optimizer import expand_cuts, merge_sort, optimize_cuts,calculate_waste,calculate_utilization


cuts = [
    Cut(5.0, 2),
    Cut(10.5, 3),
    Cut(7.0, 1),
    Cut(15.0, 2)
]

expanded = expand_cuts(cuts)
sorted_cuts = merge_sort(expanded)
stocks = optimize_cuts(sorted_cuts, 20.0)
wasted=calculate_waste(stocks, 20.0)
uti=calculate_utilization(stocks, 20.0)



print("Expanded:", expanded)
print("Sorted:", sorted_cuts)
print("Stocks:", stocks)
print("Waste:", wasted)
print("Utilization:", uti, "%")