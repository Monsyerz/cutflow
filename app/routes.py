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
        cut_length = float(request.form.get("cut_length"))
        quantity = int(request.form.get("quantity"))

        cut = Cut(cut_length, quantity)

        cuts = [cut]

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