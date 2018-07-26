# AssetMake -> AssetModelNumber -> Asset
# model_number, make_label
def collection_bootstrap(collection, **fields):
    object, _ = collection.objects.get_or_create(**fields)
    # import ipdb; ipdb.set_trace()
    return object

# 2 categories
# 6 sub categories
# 15 types
# 20 makes
# 22 model numbers
# 81 assets
#
# 15 missed rows

# asset_make = AssetMake.objects.get(make_label__iexact='makefromcsv')
# fields = {'make_label': asset_make, 'model_number': 'numberfromcsv'}
#
# collection_bootstrap(AssetModelNumber, asset_make, fields)
# collection_bootstrap(AssetMake, asset_type, fields)
