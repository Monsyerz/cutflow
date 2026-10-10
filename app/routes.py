from flask import Blueprint, render_template, request
from app.models import Cut
from app.optimizer import (
    expand_cuts,
    merge_sort,
    optimize_cuts,
    calculate_waste,
    calculate_utilization
)

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        stock_length = float(request.form.get("stock_length"))
        cut_lengths = request.form.getlist("cut_length")
        quantities = request.form.getlist("quantity")
        
        
        cuts=[]
        for cut_length, quantity in zip(cut_lengths, quantities):
            cuts.append(Cut(float(cut_length), int(quantity)))

        expanded = expand_cuts(cuts)
        sorted_cuts = merge_sort(expanded)
        stocks = optimize_cuts(sorted_cuts, stock_length)

        waste = calculate_waste(stocks, stock_length)
        utilization = calculate_utilization(stocks, stock_length)

        return render_template  (
            "index.html",
            stocks=stocks,
            waste=waste,
            utilization=utilization,
            )

    return render_template("index.html")