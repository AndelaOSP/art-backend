from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from crequest.middleware import CrequestMiddleware
from core.models import History


@receiver(post_save)
@receiver(post_delete)
def track_application_actions(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    if sender._meta.db_table != 'core_history' and current_request:
        data=instance.__dict__.copy()
        data.__delitem__('_state')
        try:
            history=History(
            table_name = str(instance._meta.db_table),
            user = current_request.user,
            item_id = instance.id,
            action = current_request.method,
            body=data
            )
            history.save()
        except ValueError:
            pass
