from app.models import Cut, Stock
from app.optimizer import expand_cuts, merge_sort

cuts = [
    Cut(5.0, 2),
    Cut(10.5, 3),
    Cut(7.0, 1),
    Cut(15.0, 2)
]

expanded = expand_cuts(cuts)
sorted_cuts = merge_sort(expanded)

print("Expanded:", expanded)
print("Sorted:", sorted_cuts)