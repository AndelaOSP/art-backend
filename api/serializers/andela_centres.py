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
    country = serializers.SlugRelatedField(
        queryset=models.Country.objects.all(), slug_field='name'
    )

    class Meta:
        model = models.AndelaCentre
        fields = ("id", "centre_name", "country", "created_at", "last_modified")

    def to_internal_value(self, data):
        country_name = data.get('country')
        if not country_name:
            raise serializers.ValidationError(
                {'country': [self.error_messages['required']]}
            )
        try:
            query_data = {'id': int(country_name)}
        except ValueError:
            query_data = {'name': country_name}
        finally:
            try:
                country = models.Country.objects.get(**query_data)
            except Exception:
                raise serializers.ValidationError(
                    {
                        'country': [
                            f'Invalid country \"{country_name}\" - object does not exist.'
                        ]
                    }
                )
        data_ = data.copy()
        data_['country'] = country.name
        internal_value = super().to_internal_value(data_)
        return internal_value


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name", "created_at", "last_modified")
