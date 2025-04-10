from django.contrib import admin
from martApp.models import Product, Coupon, Category, Vendor, CartOrder, CartOrderItems, ProductImages, Address, Wishlist, ProductReview

# Register your models here.

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = [ 'title', 'user','product_image', 'price','category', 'vendor','featured', 'product_status']   


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']   

class VendorAdmin(admin.ModelAdmin):
    list_display = ['user', 'title']

class CartOrderAdmin(admin.ModelAdmin):
    list_display = ['user','price', 'paid_status', 'order_date']   


class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order','invoice_no', 'items','image', 'qty', 'total']   

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user','product', 'review','rating']   

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user','product']   

class AddressAdmin(admin.ModelAdmin):
    list_editable = ['address', 'status']
    list_display = ['user','address', 'status']   

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code','discount', 'active']   


# admin.site.register(ProductImages, ProductImagesAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Coupon, CouponAdmin)
