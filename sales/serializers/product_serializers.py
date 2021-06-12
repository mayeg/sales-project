from rest_framework.serializers import ModelSerializer

from sales.models import Product


class ProductSerializers(ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'