from core.models.asset import Asset


def collection_bootstrap(collection, parent=None, **fields):
    missing_fields = [a for a, b in fields.items() if not b]

    for field in missing_fields:
        fields[field] = None

    if missing_fields and collection is not Asset:
        return 'Missing fields: {}'.format(missing_fields), False

    if collection is Asset and len(missing_fields) > 1:
        return 'Missing fields: {}'.format(missing_fields), False

    try:
        obj = collection.objects.get(**fields)
        if collection is Asset:
            return 'Asset already imported', False
        return obj, True
    except Exception:
        if parent:
            return collection.objects.create(**fields, **parent), True
        else:
            return collection.objects.create(**fields), True
    return 'error creating {}'.format(collection), False
