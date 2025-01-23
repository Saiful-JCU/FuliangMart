# this file created for base.html file
from martApp.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, Address, Wishlist, ProductReview
from django.db.models import Min, Max
from django.contrib import messages

def default(request):
    categories = Category.objects.all()

    # it will bring the current user address
    vendors = Vendor.objects.all()

    # filter product in price range
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))

    # wishlist count
    try:
            wishlist = Wishlist.objects.filter(user = request.user)
    except:
            # messages.warning(request, "you need to login before wishlist.")
            wishlist= 0

    # address of user        
    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None   

    return{
        "categories":categories,
        "wishlist":wishlist,
        "address":address,
        "vendors":vendors,
        "min_max_price":min_max_price,
    }