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
