from decimal import Decimal
def expand_cuts(cuts):
    expanded=[]
    for cut in cuts:
        for i in range(cut.quantity):
            expanded.append(cut.length)
    return expanded

def merge_sort(cuts):
    if len(cuts) <= 1:
        return cuts

    mid = len(cuts) // 2
    left_half = merge_sort(cuts[:mid])
    right_half = merge_sort(cuts[mid:])

    return merge(left_half, right_half)

def merge(left, right):
    result=[]
    i=j=0
    while i < len(left) and j < len(right):
        if left[i] >= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    while i < len(left):
        result.append(left[i])
        i += 1

    while j < len(right):
        result.append(right[j])
        j += 1
    return result



def optimize_cuts(cuts, stock_length):
    stocks_used = []
    capacity = Decimal(str(stock_length))

    for cut in cuts:
        placed = False
        cut_value = Decimal(str(cut))

        for stock in stocks_used:
            used_length = sum(
                Decimal(str(piece)) for piece in stock
            )

            if used_length + cut_value <= capacity:
                stock.append(cut)
                placed = True
                break

        if not placed:
            stocks_used.append([cut])

    return stocks_used

def calculate_waste(stocks_used, stock_length):
    capacity = Decimal(str(stock_length))
    waste = Decimal("0")

    for stock in stocks_used:
        used = sum(
            Decimal(str(piece)) for piece in stock
        )
        waste += capacity - used

    return float(waste)

def calculate_utilization(stocks_used, stock_length):
    total_stock_length = (
        Decimal(str(stock_length)) * len(stocks_used)
    )

    if total_stock_length <= 0:
        return 0

    total_cut_length = sum(
        Decimal(str(cut))
        for stock in stocks_used
        for cut in stock
    )

    return float(
        total_cut_length / total_stock_length * 100
    )
