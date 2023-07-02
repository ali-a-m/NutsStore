from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='store'),
    path('store/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('store/create/', views.ProductCreateView.as_view(), name='product-create'),

    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('product/<int:pk>/change_product/', views.ChangePriceView.as_view(), name='change_product'),
    path('products/<int:product_id>/add-to-cart/', views.add_to_cart, name='add-to-cart'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/Removeupdate/<int:item_id>/', views.add_one_cart, name='add-one-cart'),
    path('cart/Addupdate/<int:item_id>/', views.remove_one_cart, name='remove-one-cart'),
    path("cart/removecart/<int:item_id>/", views.remove_from_cart, name='remove-from-cart'),

    path('seller/orders/', views.SellerOrderListView.as_view(), name='seller_orders'),

    path('warehouse/create/', views.WarehouseCreateView.as_view(), name='create-warehouse'),
    path('warehouse/list/', views.WarehouseListView.as_view(), name='warehouse-list'),
    path('warehouse/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse-detail'),
    path('warehouse/<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse-delete'),
]