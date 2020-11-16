from api.models import User, Store, Item, Association
from rest_framework import serializers


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = ["image", "name", "stock", "price", "description"]


class StoreSerializer(serializers.HyperlinkedModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Store
        fields = ["address", "name", "category", "items"]


class AssociationSerializer(serializers.ModelSerializer):
    store_address = serializers.ReadOnlyField(source='store.address')
    store_name = serializers.ReadOnlyField(source='store.name')
    store_category = serializers.ReadOnlyField(source='store.category')

    class Meta:
        model = Association
        fields = ["store_address", "store_name", "store_category", "membership", "role"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    stores = AssociationSerializer(source="association_set", many=True)

    class Meta:
        model = User
        fields = ["email", "active", "staff", "admin", "stores"]
