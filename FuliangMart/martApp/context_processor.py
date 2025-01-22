# this file created for base.html file
from martApp.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, Address, Wishlist, ProductReview
from django.db.models import Min, Max

def default(request):
    categories = Category.objects.all()

    # it will bring the current user address
    vendors = Vendor.objects.all()

    # filter product in price range
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))

    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None   

    return{
        "categories":categories,
        "address":address,
        "vendors":vendors,
        "min_max_price":min_max_price
    }