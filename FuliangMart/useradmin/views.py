from django.shortcuts import render, redirect
from martApp..models import CartOrder, Product, Category
from django.db.models import Sum
from userauths.models import User

import datetime

# Create your views here.

def dashboard(request):
    revenue = CartOrder.objects.aggregate(price = Sum("price"))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_category = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")
    latest_orders = CartOrder.objects.all()

    this_month = datetime.datetime.now().month

    monthly_revenue = CartOrder.objects.filter(order_date_month = this_month).aggregate(price=Sum("price"))

    context = {
        "revenue": revenue,
        "total_orders_count": total_orders_count,
        "all_products": all_products,
        "all_category": all_category,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "this_month": this_month,
        "monthly_revenue": monthly_revenue,
    }


