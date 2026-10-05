def expand_cuts(cuts):
    expanded=[]
    for cut in cuts:
        for i in range(cut.quanity):
            expanded.append(cut.length)
    return expanded
