from django.db import models
from shortuuid.django_fields import ShortUUIDField #pip install shortuuid
from django.utils.html import mark_safe 
from userauths.models import User
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField


STATUS_CHOICE = {
    ("process", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
}

STATUS = {
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
}

RATINGS = {
    (1, "⭐☆☆☆☆"),
    (2, "⭐⭐★☆☆"),
    (3, "⭐⭐⭐★☆"),
    (4, "⭐⭐⭐⭐☆"),
    (5, "⭐⭐⭐⭐⭐"),
}


def user_directroy_path(instance, filename):
    return "user_{0}/{1}".format(instance.user.id, filename)

# Create your models here.
class Category(models.Model):
    cid = ShortUUIDField(unique = True, length = 10, max_length = 30, prefix = "cat", alphabet = "abcdefgh12345")
    title = models.CharField(max_length = 100, default = "Grocery")
    image = models.ImageField(upload_to="category")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width = "50" height = "50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
class Tags(models.Model):
    # tags = TaggableManager(blank=True)
    pass
    # TO USE tags i have to install (>> pip install django-taggit)

class Vendor(models.Model):
    vid = ShortUUIDField(unique = True, length = 10, max_length = 30, prefix = "ven", alphabet = "abcdefgh12345")
    title = models.CharField(max_length = 100, default = "FuliangMart")

    image = models.ImageField(upload_to="user_directroy_path", default= "vendor.jpg")
    cover_image = models.ImageField(upload_to="user_directroy_path", default= "vendor.jpg")
    # description = models.TextField(null=True, blank=True, default = "I am a Honest vendor.")
    description = RichTextUploadingField(null=True, blank=True, default = "I am a Honest vendor.")

    address = models.CharField(max_length = 100, default = "123, Mirpur-11, Dhaka.")
    contact = models.CharField(max_length = 100, default = "+880 0000000000")


    chat_resp_time = models.CharField(max_length = 100, default = "100")
    shiping_on_time = models.CharField(max_length = 100, default = "100")

    authentic_rating = models.CharField(max_length = 100, default = "100")
    days_return = models.CharField(max_length = 100, default = "100")

    warrenty_period = models.CharField(max_length = 100, default = "100")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    date = models.DateTimeField(auto_now_add = True, null=True, blank=True)
 
    class Meta:
        verbose_name_plural = "vendors"

    def vendor_image(self):
        return mark_safe('<img src="%s" width = "50" height = "50" />' % (self.image.url))
        
    def __str__(self):
        return self.title   

class Product(models.Model):
    pid = ShortUUIDField(unique = True, length = 10, max_length = 30, alphabet = "abcdefgh12345")
    title = models.CharField(max_length = 100, default = "LifeBook S Series")

    image = models.ImageField(upload_to="user_directroy_path", default= "product.jpg")
    # description = models.TextField(null=True, blank=True, default = "this a very good product")
    description = RichTextUploadingField(null=True, blank=True, default = "this a very good product")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name = "product")

    price = models.DecimalField(max_digits=12, decimal_places=2, default = "1.00")
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default = "2.00")

    type = models.CharField(max_length=100, default = "Organic", null=True, blank=True)
    stock_count = models.CharField(max_length=100, default = "10", null=True, blank=True)

    valid = models.CharField(max_length=100, default = "100 Days", null=True, blank=True)
    mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    # specifications= models.TextField(null=True, blank= True)
    specifications= RichTextUploadingField(null=True, blank= True)

    # tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager(blank=True)

    product_status = models.CharField(choices = STATUS, max_length = 10, default = "in_review")
    status = models.BooleanField(default=True)

    stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    digital = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True, length = 4, max_length = 10, prefix="sku", alphabet = "1234567890")
    
    date = models.DateField(auto_now_add = True)
    updated = models.DateField(null = True, blank = True)
   
    class Meta:
        verbose_name_plural = "products"

    def product_image(self):
        return mark_safe('<img src="%s" width = "50" height = "50" />' % (self.image.url))
        
    def __str__(self):
        return self.title
    
    def get_precentage(self):
        new_price = ((self.old_price - self.price) / self.old_price) * 100
        return new_price
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images",default="product.jpg")
    product = models.ForeignKey(Product,related_name = "p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Product Images"

###################################### Cart, Order, OrderItems  ###########################

class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, default = "1.99")

    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)

    product_status = models.CharField(choices = STATUS_CHOICE, max_length = 10, default = "Processing")
    sku = ShortUUIDField(null=True, blank=True, length=5, prefix = "SKU", max_length=20, alphabet="1234567890")
    oid = ShortUUIDField(null=True, blank=True, length=5, prefix = "OID", max_length=20, alphabet="1234567890")

    # billing details fields
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    house_address = models.CharField(max_length=255, null=True, blank=True)
    road_name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    saved = models.DecimalField(max_digits=12, decimal_places=2, default = "0.00")
    shipping_method = models.CharField(max_length=100, null=True, blank=True)

    traking_id = models.CharField(max_length=100, null=True, blank=True)
    traking_website_address = models.CharField(max_length=100, null=True, blank=True)

    stripe_payment_intent = models.CharField(max_length=100, null=True, blank=True)
    coupons = models.ManyToManyField("martApp.Coupon", blank=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length = 200)
    product_status = models.CharField(max_length = 200)

    items = models.CharField(max_length = 200)
    image = models.CharField(max_length = 200)

    qty = models.IntegerField(default = 0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default = "1.99")
   
    total = models.DecimalField(max_digits=12, decimal_places=2, default = "1.99")
    
    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width = "50" height = "50" />' % (self.image.url))
    

###################################### product review, wishlists, address  ###########################

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name = "reviews")

    review = models.TextField()
    rating = models.IntegerField(choices=RATINGS, default=None)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"
   
    def __str__(self):
        return self.product.title
    
    def get_rating(self):
        return self.rating
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"
   
    def __str__(self):
        return self.product.title


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mobail = models.CharField(max_length = 100, null=True)
    address= models.CharField(max_length = 100, null=True)

    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"    


class Coupon(models.Model):
    code = models.CharField(max_length = 50)
    discount = models.IntegerField(default = 1)
    active = models.BooleanField(default = True)

    def __str__(self):
        return self.code



