from api.models import User, Store, Item, Association, History_of_Item
from rest_framework import serializers


class ItemHistorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = History_of_Item
        fields = [
            "before_name",
            "after_name",
            "before_price",
            "after_price",
            "before_stock",
            "after_stock",
            "before_description",
            "after_description",
            "datetime",
        ]


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    history = ItemHistorySerializer(many=True)

    class Meta:
        model = Item
        fields = ["image", "name", "stock", "price", "description", "history"]


class StoreSerializer(serializers.HyperlinkedModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Store
        fields = ["address", "name", "category", "items","id"]


class AssociationSerializer(serializers.ModelSerializer):
    store_address = serializers.ReadOnlyField(source="store.address")
    store_name = serializers.ReadOnlyField(source="store.name")
    store_category = serializers.ReadOnlyField(source="store.category")
    store_id = serializers.ReadOnlyField(source="store.id")
    class Meta:
        model = Association
        fields = ["store_address", "store_name", "store_category", "membership", "role", "store_id"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    stores = AssociationSerializer(source="association_set", many=True)

    class Meta:
        model = User
        fields = ["email", "active", "staff", "admin", "stores", "id"]
