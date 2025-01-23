from django.urls import path, include
from martApp.views import index, remove_wishlist, add_to_wishlist, wishlist_view, make_address_default, place_order, order_success, order_detail, customer_dashboard, checkout_view, update_cart, delete_item_from_cart, cart_view, add_to_cart, search_view, filter_product, product_list_view, ajax_add_review, tag_list, categories_list, category_product_list_view, vendor_list_view, vendor_detail_view, product_detail_view
app_name = "martApp"

urlpatterns = [
    path("", index, name="index"),
    path("products/", product_list_view, name="product_list"),

    path("product/<pid>/", product_detail_view, name="product_detail"),
    path("category/", categories_list, name="categories"),

    path("category/<cid>/", category_product_list_view, name="category-product-list"),
    path("vendor/", vendor_list_view, name="vendor_list"),
    
    path("vendors/<vid>/", vendor_detail_view, name="vendor_detail"),
    path("tag/<slug:tag_slug>/", tag_list, name="tag_list"),
    # add review
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),
    
    path("search/", search_view, name="search"),
    # product filter
    path("filter-products/", filter_product, name="filter-product"),
    # add to cart link
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    path("cart/", cart_view, name="cart"),

    path("update-cart/", update_cart, name="update-cart"),
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),


    path("wishlist/", wishlist_view, name="wishlist"),
    path("add-to-wishlist/", add_to_wishlist, name="add-to-wishlist"),

    path("remove-from-wishlist/", remove_wishlist, name="remove-from-wishlist"),

    path("checkout/", checkout_view, name="checkout"),
    path('place-order/', place_order, name="place_order"),

    path('order-success/', order_success, name="order_success"),
    path("dashboard/order/<int:id>", order_detail, name="order-detail"),

    path("dashboard/", customer_dashboard, name="dashboard"),

     # paypal integrations url
    path('paypal/', include('paypal.standard.ipn.urls')),
    # path('payment-completed/', payment_completed_view, name="payment-completed"),
    # path('payment-failed/', payment_failed_view, name="payment-failed"),    


    # making address default
    path('make-default-address/', make_address_default, name="make-address-default"),
]