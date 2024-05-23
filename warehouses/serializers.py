from rest_framework import serializers

from .models import *
from products.serializers import ProductSerializer
from products.models import Product

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class WarehouseProductSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    warehouse = serializers.UUIDField()
    amount = serializers.IntegerField()
    invalids_amount = serializers.IntegerField(required=False)
    archived = serializers.BooleanField(required=False)
    comment = serializers.CharField(required=False)

class WarehouseProductGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseProduct
        fields = ['id', 'product', 'warehouse', 'amount', 'invalids_amount']

    def to_representation(self, instance):
        data = super(WarehouseProductGetSerializer, self).to_representation(instance)
        if instance.warehouse:
            warehouse = WarehouseSerializer(Warehouse.objects.get(id=instance.warehouse.id))
            data.update({"warehouse": warehouse.data})
        if instance.product:
            product = ProductSerializer(Product.objects.get(id=instance.product.id))
            data.update({"product": product.data})
        return data
