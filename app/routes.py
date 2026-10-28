from flask import Blueprint, render_template, request
from app.models import Cut
from app.optimizer import (
    expand_cuts,
    merge_sort,
    optimize_cuts,
    calculate_waste,
    calculate_utilization
)
from app.extensions import db
from app.db_models import OptimizationResult

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        stock_length_raw = request.form.get("stock_length")
        cut_lengths = request.form.getlist("cut_length")
        quantities = request.form.getlist("quantity")
        if len(cut_lengths) != len(quantities):
            return render_template(
                "index.html",
                error="Each cut length must have a quantity."
            )

        # Validate stock length input

        if not stock_length_raw:
            return render_template(
                "index.html",
                error="Please enter a valid stock length."
            )
        
        stock_length = float(stock_length_raw)
        
        if stock_length <= 0:
            return render_template(
                "index.html",
                error="Stock length must be a positive number."
            )

        #validate cuts


        cuts = []

        for cut_length, quantity in zip(cut_lengths, quantities):
            
            cut_length = float(cut_length)
            quantity = int(quantity)

            if cut_length<=0:
                return render_template(
                    "index.html",
                    error="Cut lengths must be positive numbers."
                )
            if cut_length > stock_length:
                return render_template(
                    "index.html",
                    error="Cut lengths cannot exceed stock length."
                )
            if quantity <= 0:
                return render_template(
                    "index.html",
                    error="Quantities must be positive integers."
                )
            
            cuts.append(Cut(cut_length, quantity))

            
        expanded = expand_cuts(cuts)
        sorted_cuts = merge_sort(expanded)
        stocks = optimize_cuts(sorted_cuts, stock_length)

        stocks_used = len(stocks)
        
        waste = calculate_waste(stocks, stock_length)
        utilization = calculate_utilization(stocks, stock_length)

        total_cut_length = sum(expanded)
        total_cuts = len(expanded)
        result = OptimizationResult(
            stocks_used=stocks_used,
            waste=waste,
            utilization=utilization
        )
        db.session.add(result)
        db.session.commit()


        return render_template  (
            "index.html",
            stocks=stocks,
            waste=waste,
            utilization=utilization,
            stocks_used=stocks_used,
            total_cut_length=total_cut_length,
            total_cuts=total_cuts
            )

    return render_template("index.html")

@main.route("/history")
def history():
    results = OptimizationResult.query.order_by(
        OptimizationResult.created_at.desc()
    ).limit(10).all()

    return render_template("history.html", results=results)