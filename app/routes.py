from flask import Blueprint, render_template, request, Response, jsonify

from app.models import Cut
from app.optimizer import (
    expand_cuts,
    merge_sort,
    optimize_cuts,
    calculate_waste,
    calculate_utilization
)

import math
import csv

from io import StringIO

from app.extensions import db
from app.db_models import OptimizationResult
from sqlalchemy.exc import SQLAlchemyError

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
        if not cut_lengths:
            return render_template(
                "index.html",
                error="Please enter at least one cut."
            )

        # Validate stock length input

        if not stock_length_raw:
            return render_template(
                "index.html",
                error="Please enter a valid stock length."
            )
        
        try:
            stock_length = float(stock_length_raw)
        except (ValueError, TypeError):
            return render_template(
                "index.html",
                error="Stock length must be a valid number.")
        
        if not math.isfinite(stock_length) or stock_length <= 0:
            return render_template(
                "index.html",
                error="Stock length must be a positive number."
            )

        #validate cuts


        cuts = []
        total_quantity = 0

        for cut_length_raw, quantity_raw in zip(cut_lengths, quantities):

            try:
                cut_length = float(cut_length_raw)
                quantity = int(quantity_raw)

            except (ValueError, TypeError):
                return render_template(
                    "index.html",
                    error="Cut length must be a valid number and quantity must be a whole number."
                )

            if not math.isfinite(cut_length) or cut_length <= 0:
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
            total_quantity += quantity
            if total_quantity > 1000:
                return render_template(
                    "index.html",
                    error="Too many cuts requested. Please limit to 1000 cuts."
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
        try:
            db.session.add(result)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return render_template(
                "index.html",
                error="Unable to save optimization results. Please try again."
            )


        return render_template  (
            "index.html",
            stocks=stocks,
            stock_length=stock_length,
            waste=waste,
            utilization=utilization,
            stocks_used=stocks_used,
            total_cut_length=total_cut_length,
            total_cuts=total_cuts
            )

    return render_template("index.html")

@main.route("/history")
def history():
    try:
        results = OptimizationResult.query.order_by(
            OptimizationResult.created_at.desc()
        ).limit(10).all()
        return render_template("history.html", results=results)
    except SQLAlchemyError:
        return render_template(
            "history.html",
            results=[],
            error="Unable to fetch optimization history."
        )

    
@main.route("/export")
def export_history():
    try:
        results = OptimizationResult.query.order_by(
            OptimizationResult.created_at.desc()
        ).all()
    except SQLAlchemyError:
        return render_template(
            "history.html",
            results=[],
            error="Unable to export optimization history. Please try again."
        ), 503

    output = StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow([
        "ID", "Stocks Used", "Waste", "Utilization", "Created At"
    ])

    for result in results:
        csv_writer.writerow([
            result.id,
            result.stocks_used,
            result.waste,
            result.utilization,
            result.created_at
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=history.csv"
        }
    )

@main.route("/api/optimize", methods=["POST"])
def optimize_api():
    data = request.get_json()

    stock_length = data.get("stock_length")
    cuts = data.get("cuts")
    
    if type(cuts) is not list:
        return jsonify({"error": "Cuts must be a list"}), 400

    if not cuts:
        return jsonify({"error": "Cuts cannot be empty"}), 400

    try:
        stock_length = float(stock_length)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid stock length"}), 400
    if stock_length<=0:
        return jsonify({"error": "Invalid stock length"}), 400
    
    if not math.isfinite(stock_length) or stock_length <= 0:
        return jsonify({"error": "Invalid stock length"}), 400
    
    cuts_data = []
    total_quantity = 0

    for cut in cuts:
        if type(cut) is not dict:
            return jsonify({"error": "Each cut must be a dictionary"}), 400

    for cut in cuts:
        length = cut.get("length")
        quantity = cut.get("quantity")

        if length is None or quantity is None:
            return jsonify({"error": "Cut length and quantity are required"}), 400

        
        try:
            length = float(length)
        except(ValueError, TypeError):
            return jsonify({"error": "Invalid cut length"}), 400

        if not math.isfinite(length) or length <= 0:
            return jsonify({"error": "Invalid cut length"}), 400

        if length > stock_length:
            return jsonify({"error": "Cut length exceeds stock length"}), 400

        if type(quantity) is not int:
            return jsonify({"error": "Invalid cut quantity"}), 400

        if quantity <= 0:
            return jsonify({"error": "Invalid cut quantity"}), 400

        total_quantity += quantity
        if total_quantity > 1000:
            return jsonify({ "error": "Too many cuts requested. Please limit to 1000 cuts."}), 400
        
        new_cut = Cut(length, quantity)
        cuts_data.append(new_cut)

    expanded = expand_cuts(cuts_data)
    sorted_cuts = merge_sort(expanded)
    stocks = optimize_cuts(sorted_cuts, stock_length)
    stocks_used = len(stocks)
    total_cuts = len(expanded)
    waste = calculate_waste(stocks, stock_length)
    utilization = calculate_utilization(stocks, stock_length)
    total_cut_length = sum(expanded)
    
    return jsonify({
    "stocks_used": stocks_used,
    "total_cuts": total_cuts,
    "waste": waste,
    "utilization": utilization,
    "total_cut_length": total_cut_length
    }), 200