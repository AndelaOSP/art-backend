# Third-Party Imports
from django.db.models.signals import post_save
from django.dispatch import receiver

# App Imports
from core import constants
from core.models import AssetIncidentReport, AssetStatus, StateTransition


@receiver(post_save, sender=AssetStatus)
def update_transition_state(**kwargs):
    """
    update the transition state to CLOSED when an Asset status is changed from ALLOCATED to
    either (AVAILABLE,DAMAGED,LOST)
    :param kwargs:
    :return None:
    """
    instance = kwargs.get("instance")  # the instance of the incident report being saved
    valid_previous_asset_types = (constants.ALLOCATED,)
    valid_current_asset_types = (constants.DAMAGED, constants.LOST, constants.AVAILABLE)

    # previous_instance = AssetStatus.objects.filter(id=instance.id).latest('created_at')
    current_asset_status = instance.current_status
    previous_asset_status = instance.previous_status

    try:
        if previous_asset_status in valid_previous_asset_types:
            if current_asset_status in valid_current_asset_types:
                # get the latest incident report
                # filter out all results that dont have a recorded created_at date
                latest_incident_report = AssetIncidentReport.objects.filter(
                    asset=instance.asset, created_at__isnull=False
                ).latest('created_at')
                # get the transition state associated with the incident report
                transition_state = StateTransition.objects.get_or_create(
                    asset_incident_report=latest_incident_report
                )
                transition_state = transition_state[0]
                # update the transition state
                transition_state.incident_report_state = constants.CLOSED
                transition_state.save()
    except AssetIncidentReport.DoesNotExist:
        pass
