# Third-Party Imports
from rest_framework import serializers

# App Imports
from core import models


class OfficeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeBlock
        fields = ("name", "id", "location")


class OfficeFloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeFloor
        fields = ("number", "block", "id")


class OfficeFloorSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeFloorSection
        fields = ("name", "floor", "id")


class OfficeWorkspaceSerializer(serializers.ModelSerializer):
    floor = serializers.SerializerMethodField()
    block = serializers.SerializerMethodField()

    class Meta:
        model = models.OfficeWorkspace
        fields = ("id", "name", "section", "floor", "block")

    def get_floor(self, obj):
        return obj.section.floor.number

    def get_block(self, obj):
        return obj.section.floor.block.name


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ("name", "id")


class AndelaCentreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AndelaCentre
        fields = ("id", "name", "country", "created_at", "last_modified")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name", "created_at", "last_modified")
