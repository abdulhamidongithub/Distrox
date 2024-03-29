from rest_framework import serializers

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', "role", "username", "address",
            "birth_date", "status", "warehouse"
            ]

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        car = Car.objects.filter(driver=instance)
        if car.exists():
            serializer = CarSerializer(car.first())
            data.update({"car": serializer.data})
        return data


class SalaryPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryPayment
        fields = '__all__'

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.number = validated_data.get('number', instance.number)
        instance.driver = validated_data.get('driver', instance.driver)

        instance.save()
        return instance

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    re_new_password = serializers.CharField(required=True, write_only=True)

    def update(self, instance, validated_data):

        instance.password = validated_data.get('password', instance.password)

        if not validated_data['new_password']:
              raise serializers.ValidationError({'new_password': 'not found'})

        if not validated_data['old_password']:
              raise serializers.ValidationError({'old_password': 'not found'})

        if not instance.check_password(validated_data['old_password']):
              raise serializers.ValidationError({'old_password': 'wrong password'})

        if validated_data['new_password'] != validated_data['re_new_password']:
            raise serializers.ValidationError({'passwords': 'passwords do not match'})

        if validated_data['new_password'] == validated_data['re_new_password'] and instance.check_password(validated_data['old_password']):
            instance.set_password(validated_data['new_password'])
            instance.save()
            return instance

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password','re_new_password']
