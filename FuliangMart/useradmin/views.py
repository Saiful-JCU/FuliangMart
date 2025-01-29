from django.shortcuts import render, redirect, get_object_or_404
from martApp.models import CartOrder, Product, Category, ProductReview, CartOrderItems, Vendor
from django.db.models import Sum
from userauths.models import User
from useradmin.forms import AddProductForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


import datetime

# Create your views here.

def dashboard(request):
    revenue = CartOrder.objects.aggregate(price=Sum("price"))
    vendor = Vendor.objects.filter(user=request.user).first()
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_category = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")
    latest_orders = CartOrder.objects.all()

    this_month = datetime.datetime.now().month

    monthly_revenue = CartOrder.objects.filter(order_date__month = this_month).aggregate(price=Sum("price"))

    context = {
        "revenue": revenue,
        "total_orders_count": total_orders_count,
        "all_products": all_products,
        "all_category": all_category,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "this_month": this_month,
        "monthly_revenue": monthly_revenue,
        "vendor": vendor,
    }

    return render(request, "useradmin/dashboard.html", context)


def products(request):
    all_products = Product.objects.all().order_by("-id")
    all_category = Category.objects.all()

    context = {
        "all_products": all_products,
        "all_category": all_category,
    }

    return render(request, "useradmin/dashboard-products.html", context)


def add_product(request):
    if request.method == "POST":
        m_from = AddProductForm(request.POST, request.FILES)
        if m_from.is_valid():
            new_form = m_from.save(commit = False)
            new_form.user = request.user
            new_form.save()

            m_from.save_m2m()
            return redirect("useradmin:dashboard")
    else:
        m_from = AddProductForm()

    context = {
        "form":m_from
    }
    return render(request, "useradmin/dashboard-add-products.html", context)


def edit_product(request, pid):
    product = Product.objects.get(pid = pid)
    if request.method == "POST":
        m_from = AddProductForm(request.POST, request.FILES, instance = product)
        if m_from.is_valid():
            new_form = m_from.save(commit = False)
            new_form.user = request.user
            new_form.save()

            m_from.save_m2m()
            return redirect("useradmin:products")
    else:
        m_from = AddProductForm(instance = product)

    context = {
        "form":m_from,
        "product":product,
    }
    return render(request, "useradmin/dashboard-edit-products.html", context)


def delete_products(request, pid):
    product = Product.objects.get(pid = pid)
    product.delete()
    return redirect("useradmin:products")


def orders(request):
    orders = CartOrder.objects.all()
    context = {
        "orders":orders,
    }

    return render(request, "useradmin/orders.html", context)


def order_detail(request, oid):
    order = CartOrder.objects.get(oid=oid)
    print(order.oid)
    order_item = CartOrderItems.objects.filter(order=order)

    context = {
        "order":order,
        "order_item":order_item,
    }

    return render(request, "useradmin/order_detail.html", context)

@csrf_exempt 
def change_order_status(request, oid):
    order = CartOrder.objects.get(oid=oid)
    if request.method == 'POST':
        status = request.POST.get("status")
        print("status", status)
        order.product_status = status
        order.save()
        messages.success(request, f"Order status changed to {status}")

    return redirect("useradmin:order_detail", order.oid)


# def shop_page(request):
#     products = Product.objects.all()
#     revenue = CartOrder.objects.filter(paid_status=True).aggregate(price=Sum("price"))
#     vendor = Vendor.objects.all()
#     total_seles = CartOrderItems.objects.filter(order__paid_status = True).aggregate(qty=Sum("qty"))

#     context = {
#         "products":products,
#         "revenue":revenue,
#         "total_seles":total_seles,
#         "vendor":vendor,
#     }

#     return render(request, "useradmin/shop_page.html", context)

# def shop_page(request, vid):
#     vendor = Vendor.objects.filter(vid = vid)
#     if not vendor:
#         return HttpResponse("Vendor not found", status=404)
#     products = Product.objects.filter(vendor=vendor)

#     revenue = CartOrder.objects.filter(paid_status=True, cartorderitems__product__vendor=vendor).aggregate(price=Sum("price"))
#     total_seles = CartOrderItems.objects.filter(order__paid_status = True, product__vendor=vendor).aggregate(qty=Sum("qty"))

#     context = {
#         "products":products,
#         "revenue":revenue,
#         "total_seles":total_seles,
#         "vendor":vendor,
#     }

#     return render(request, "useradmin/shop_page.html", context)

def shop_page(request, vid):
    vendor = get_object_or_404(Vendor, vid=vid) 
    products = Product.objects.filter(vendor=vendor)
    revenue = CartOrder.objects.filter(paid_status=True).aggregate(price=Sum("price"))
    total_sales = CartOrderItems.objects.filter(order__paid_status = True).aggregate(qty=Sum("qty"))

    context = {
        "products": products,
        "revenue": revenue,
        "total_sales": total_sales,
        "vendor": vendor,
    }
    return render(request, "useradmin/shop_page.html", context)

# def reviews(request):
    reviews = ProductReview.objects.all()
    context = {
        "reviews":reviews
    }

    return render(request, "useradmin/reviews.html", context)

def reviews(request):
    vendor = Vendor.objects.filter(user=request.user).first()
    reviews = ProductReview.objects.filter(product__vendor=vendor) if vendor else []
    context = {
        "vendor":vendor,
        "reviews":reviews,
    }

    return render(request, "useradmin/reviews.html", context)





