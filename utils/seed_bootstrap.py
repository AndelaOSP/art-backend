from django.apps import apps
from core.models.asset import Asset


def collection_bootstrap(collection, parent=None, **fields):
    if parent is not None:
        missing_parent = [a for a, b in parent.items() if not b]
        if len(missing_parent) > 0:
            return missing_parent, False
    collection = apps.get_model('core', collection)
    missing_fields = [a for a, b in fields.items() if not b]

    if missing_fields and collection is not Asset:
        return missing_fields, False

    if collection is Asset and len(missing_fields) > 1:
        return missing_fields, False
    return load_to_db(collection, parent, **fields)


def load_to_db(collection, parent=None, **fields):
    try:
        obj = collection.objects.get(**fields)
        if collection is Asset:
            return ['Asset already imported'], False
        return obj, True
    except Exception:
        try:
            if parent:
                return collection.objects.create(**fields, **parent), True
            else:
                return collection.objects.create(**fields), True
        except Exception as e:
            return [str(e)], False
    return 'error creating {}'.format(collection), False
