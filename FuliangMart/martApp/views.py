from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from martApp.models import Product, Coupon, Category, Vendor, CartOrder, CartOrderItems, ProductImages, Address, Wishlist, ProductReview
from userauths.models import ContactUs, Profile
from django.db.models import Count , Avg
from taggit.models import Tag
from django.shortcuts import render, get_object_or_404
from martApp.form import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# for charts
import calendar
from django.db.models.functions import ExtractMonth



# Create your views here.
def index(request):
    # product = Product.objects.all().order_by("-id")
    product = Product.objects.filter(featured=True, product_status="published").order_by("-id")

    print("Featured Product Count:", product.count())  # Debugging line
    context = {
        "product": product
    }
    return render(request, 'core/index.html', context)

def product_list_view(request):
    product = Product.objects.filter( product_status="published")
    

    context = {
        "product": product
    }
    return render(request, "core/product-list.html", context)

def categories_list(request):
    categories = Category.objects.all()
    # cat_count = Category.objects.all().annotate(product_count=Count("product"))

    context = {
        "categories": categories,
        # "cat_count": cat_count,
    }
    return render(request, "core/category-list.html", context)

def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    product = Product.objects.filter( product_status="published", category=category)

    context={
        "category": category,
        "product":product
    }

    return render(request, "core/category-product-list.html", context)


def vendor_list_view(request):
    vendor = Vendor.objects.all()

    context = {
        "vendor" : vendor
    }
    return render(request, "core/vendor-list.html", context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid = vid)
    products = Product.objects.filter(vendor=vendor, featured=True, product_status="published").order_by("-id")

    context = {
        "vendor":vendor,
        "product":products
    }

    return render(request, "core/vendor-detail.html", context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)

    products = Product.objects.filter(category = product.category).exclude(pid=pid)

    review = ProductReview.objects.filter(product=product).order_by("-date")

    average_rating = ProductReview.objects.filter(product=product).aggregate(rating = Avg('rating'))
    

    make_review = True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user = request.user, product=product).count()
        if user_review_count > 0:
            
            make_review = True 

    # product review form
    review_form = ProductReviewForm()

    p_images = product.p_images.all()
    
    address = "Login To Continue"

    context = {
        "p": product,
        "address": address,
        "p_images": p_images,
        "review": review,
        "make_review": make_review,
        "average_rating": average_rating,
        "review_form": review_form,
        "products": products,
        
        # "cat": cat
    }
    return render(request, "core/product-detail.html", context)


def tag_list(request, tag_slug = None):
    product = Product.objects.filter(product_status="published").order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        products = product.filter(tags__in=[tag])

    context = {
        "products":products,
        "tag":tag
    }
    return render(request, "core/tag.html", context)

#add review on product
def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    # review = ProductReviewForm.objects.create(
    review = ProductReview.objects.create(

        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating']
    )

    context = {
        "user":user.username,
        "review":request.POST['review'],
        "rating": request.POST['rating'],
    }

    average_review = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
            'bool': True,
            'context':context,
            'average_review':average_review
        }
    )


def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains = query).order_by("-date")

    context = {
        "products" : products,
        "query" : query
    }

    return render(request, "core/search.html", context)


def filter_product(request):
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')

    min_price = request.GET["min_price"]
    max_price = request.GET["max_price"]

    products = Product.objects.filter(product_status = "published").order_by("-id").distinct()

    products = products.filter(price__gte = min_price)
    products = products.filter(price__lte = max_price)

    if len(categories)  > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors)  > 0:
        vendors = products.filter(vendors__id__in=vendors).distinct()

    context = {
        "products":products,
    }
    data = render_to_string("core/async/product-list.html",context )

    return JsonResponse({"data":data})


def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }

    # # for checking 
    if 'cart_data_obj' not in request.session:
        request.session['cart_data_obj'] = {}

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            # cart_data[product_id]['qty'] +=int(request.GET['qty'])
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj']

    return JsonResponse({
            'data':request.session['cart_data_obj'], 
            'totalcartitems':len(request.session['cart_data_obj'])
    })


def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        # for p_id, item in request.session['cart_data_obj']:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {
                'cart_data':request.session['cart_data_obj'], 
                'totalcartitems':len(request.session['cart_data_obj']),
                'cart_total_amount':cart_total_amount })
    else:
        messages.warning(request, "Your cart is empty!")
        return redirect("martApp:index")
        # return render(request, "core/cart.html")
        # return render(request, "core/cart.html", {'cart_data':'', 'totalcartitems':len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount })


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data
    # after deleting the product
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
       
    context = render_to_string("core/async/cart-list.html", {
            'cart_data': request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        })            

    return JsonResponse({
        "data": context, 
        'totalcartitems':len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    })

@login_required
def update_cart(request):
    product_id = str(request.GET.get('id'))  
    product_qty = int(request.GET.get('qty'))  

    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        
        # Check if the product exists in the cart and update its quantity
        if product_id in cart_data:
            cart_data = request.session['cart_data_obj'] 
            # cart_data[product_id]['qty'] = product_qty
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data
            # request.session.modified = True  


    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {
        'cart_data': request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    })

    return JsonResponse({
        "data": context, 
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    })


def save_checkout_info(request):
    if 'cart_data_obj' not in request.session or not request.session['cart_data_obj']:
        messages.warning(request, "Your cart is empty. Please add items to your cart before proceeding to checkout.")
        return redirect('martApp:index')

    cart_total_amount = 0
    total_amount = 0
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        house_address = request.POST.get("house")
        road_name = request.POST.get("road")
        city = request.POST.get("city")
        print(full_name, email, phone, house_address, road_name, city)

        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['phone'] = phone
        request.session['house_address'] = house_address
        request.session['road_name'] = road_name
        request.session['city'] = city
        # print(request.POST

    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        house_address = request.POST.get("house")
        road_name = request.POST.get("road")
        city = request.POST.get("city")

        order = CartOrder.objects.create(
            user = request.user,
            price = cart_total_amount,
            full_name = full_name,
            email = email,
            phone = phone,
            house_address=house_address,
            road_name=road_name,
            city = city,
            
        )

        del request.session['full_name']
        del request.session['email']
        del request.session['phone']
        del request.session['house_address']
        del request.session['road_name']
        del request.session['city']

        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

            cart_order_items = CartOrderItems.objects.create(
                order = order,
                invoice_no="INVOICE_NO" +str(order.id),
                    
                # product_status="Pending",
                items=item['title'],
                image=item['image'], 
                qty=int(item['qty']),
                price=float(item['price']),
                total=float(item['price']) * int(item['qty']),

            )
        # Clear session data
        # request.session.pop('cart_data_obj', None)


        return redirect("martApp:checkout", order.oid)
    return redirect("martApp:checkout", order.oid)

@login_required
def checkout(request, oid):
    order = CartOrder.objects.get(oid=oid)
    order_items = CartOrderItems.objects.filter(order=order)

    # cart_total_amount = 0
    # for item in order_items:
    #     cart_total_amount += item.qty * item.price
    
    if request.method == "POST":
        code = request.POST.get('code')
        # print(code)
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            if coupon in order.coupons.all():
                messages.warning(request, "Coupon already activated.")
                # return redirect("martApp:checkout", order.oid)
            else:
                discount = order.price * coupon.discount / 100
                order.coupons.add(coupon)
                order.price -= discount
                order.saved += discount
                order.save()

                messages.success(request, "Coupon activated.")
                # return redirect("martApp:checkout", oid=order.oid)
                request.session.pop('cart_data_obj', None)
        # else:
        #     messages.warning(request, "Coupon Doesnot Exists.")
        #     return redirect("martApp:checkout", oid=order.oid)

    # latest_order = CartOrder.objects.filter(user=request.user)
    cart_total_amount = sum(item.total for item in order_items)
    context = {
        "order":order,
        "order_items":order_items,
        "cart_total_amount": cart_total_amount,
    }

    # return render(request, "core/payment-completed.html", context)
    return render(request, "core/checkout.html", context)


@login_required 
def order_success(request):
    latest_order = CartOrder.objects.filter(user=request.user).order_by('-order_date').first()
    
    order_items = CartOrderItems.objects.filter(order=latest_order)

    return render(request, "core/payment-completed.html", {
        'order': latest_order,
        'order_items': order_items,
        'totalcartitems': order_items.count(),
        'cart_total_amount': latest_order.price,
    })


@login_required 
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user)

    address = Address.objects.filter(user=request.user)

    
    # for charts
    orders = CartOrder.objects.annotate(month=ExtractMonth("order_date")).values("month").annotate(count=Count("id")).values("month", "count")
    month = []
    total_orders = []

    for o in orders:
        month.append(calendar.month_name[o['month']])
        total_orders.append(o["count"])

    if request.method == "POST":
        address = request.POST["address"]
        mobail = request.POST.get("mobail")

        new_address = Address.objects.create(
            user = request.user,
            address = address,
            mobail = mobail
        )
        messages.success(request, "Address added Successfully.")
        return redirect("martApp:dashboard")


    user_profile = Profile.objects.get(user=request.user)
    context = {
        # "profile":profile,
        "orders_list":orders_list,
        "orders":orders,
        "month":month,
        "total_orders":total_orders,
        "user_profile":user_profile,
        "address":address,
    }
    return render(request, 'core/dashboard.html',context)


@login_required 
def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id = id)
    products = CartOrderItems.objects.filter(order=order)

    context = {
        "products": products
    }
    return render(request, 'core/order-detail.html', context)

@login_required
def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status = False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})


@login_required 
def wishlist_view(request):
    wishlist = Wishlist.objects.all()
    context = {
        "w":wishlist
    }

    return render(request, "core/wishlist.html", context)


@login_required 
def add_to_wishlist(request):
    product_id = request.GET['id']
    product= Product.objects.get(id = product_id)

    context = {
        # "w":wishlilst
    }
    wishlist_count = Wishlist.objects.filter(product = product, user = request.user).count()
    # print("wishlist count", wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool":True
        }
    else:
        new_wishlist = Wishlist.objects.create(
            product = product,
            user = request.user
        )
    context = {
        'bool':True
    }
    return JsonResponse(context)
        

@login_required 
def remove_wishlist(request):
    pid = request.GET['id']
    wishlilst = Wishlist.objects.filter(user=request.user)
    wishlilst_d = Wishlist.objects.get(id=pid)

    # product = Wishlist.objects.get(id=pid)
    delete_product =wishlilst_d.delete()

    context = {
        "bool":True,
        "wishlist":wishlilst,
    }
    wishlist_jeson = serializers.serialize('jeson', wishlilst)
    data = render_to_string("core/async/wishlist-list.html", context)
    return JsonResponse({"data":data, "w":wishlist_jeson})


@login_required 
def contact(request):
    return render(request, 'core/contact.html')


@login_required
def ajax_contact(request):
    full_name = request.GET['full_name']
    email = request.GET['email']
    phone = request.GET['phone']
    subject = request.GET['subject']
    message = request.GET['message']

    contact = ContactUs.objects.create(
        full_name = full_name,
        email = email,
        phone = phone,
        subject = subject,
        message = message
    )

    content = {
        "bool":True,
        "message": "Message Sent Successfully."
    }

    return JsonResponse({"content":content})

@login_required
def profile_edit(request):
    return render(request, )


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def purchase_guide(request):
    return render(request, "core/purchase_guide.html")


def terms_of_service(request):
    return render(request, "core/terms_of_service.html")

def about_us(request):
    return render(request, "core/about_us.html")



