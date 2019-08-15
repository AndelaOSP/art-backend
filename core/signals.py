# Third-Party Imports
from django.db.models.signals import pre_save
from django.dispatch import receiver

# App Imports
from core import constants
from core.models import AssetIncidentReport, AssetStatus, StateTransition


@receiver(pre_save, sender=AssetStatus)
def update_transition_state(**kwargs):
    """
    update the transition state to CLOSED when an Asset status is changed from (DAMAGED,LOST) to
    either (AVAILABLE,ALLOCATED)
    :param kwargs:
    :return None:
    """
    instance = kwargs.get("instance")  # the instance of the incident report being saved
    valid_previous_asset_types = (constants.DAMAGED, constants.LOST)
    valid_current_asset_types = (constants.AVAILABLE, constants.ALLOCATED)

    try:
        previous_instance = AssetStatus.objects.get(id=instance.id)
        current_asset_status = instance.current_status
        previous_asset_status = previous_instance.current_status

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

    except AssetStatus.DoesNotExist:
        pass

    # current_incident_type = instance.incident_type
    # transition_state = StateTransition.objects.get_or_create(
    #     asset_incident_report=instance
    # )
    # transition_state = transition_state[0]
    # current_transition_state = transition_state.incident_report_state
    #
    # # tuples of states for which the logic of this signal is triggered
    # valid_incident_types = (constants.LOSS, constants.DAMAGE)
    # valid_transition_states = (
    #     constants.INTERNAL_ASSESSMENT,
    #     constants.EXTERNAL_ASSESSMENT,
    #     constants.OUT_FOR_REPAIR,
    # )
    # # if the current incident type and transition state are valid, update the state
    # if (
    #         current_incident_type in valid_incident_types
    #         and current_transition_state in valid_transition_states
    # ):
    #     transition_state.incident_report_state = constants.CLOSED
    #     transition_state.save()
