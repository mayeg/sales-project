from django.urls import path
from .views import ClientView, ClientDetailView, BillView, BillDetailView, ProductView, ProductDetailView, \
    ClientExportView, ClientImportView

urlpatterns = [
    path('clients', ClientView.as_view()),
    path('client/<int:id>/', ClientDetailView.as_view(), name='client'),
    path('clients/export/', ClientExportView.as_view()),
    path('clients/import/', ClientImportView.as_view()),
    path('bills', BillView.as_view()),
    path('bill/<int:id>/', BillDetailView.as_view(), name='bill'),
    path('products', ProductView.as_view()),
    path('product/<int:id>/', ProductDetailView.as_view(), name='product'),

]
