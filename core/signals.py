# Third-Party Imports
from django.db.models.signals import post_save
from django.dispatch import receiver

# App Imports
from core import constants
from core.models import AssetIncidentReport, StateTransition

# TODO add functionality to close incident report when asset statuses are changed. story clarification being awaited
# @receiver(post_save, sender=AssetStatus)
# def close_incident_report(**kwargs):
#     """
#     close an incident report if asset status is updated to [`damaged`,`lost`,'available]
#     :param kwargs:
#     :return:
#     """
#     instance = kwargs.get("instance")
#     current_asset_status = instance.current_status
#
#     valid_asset_states = [constants.DAMAGED, constants.LOST, constants.AVAILABLE]
#
#     if current_asset_status in valid_asset_states:
#         if current_asset_status == constants.AVAILABLE:
#             # if an incident report already exists, update the transitional state to closed
#             try:
#                 incident_report = AssetIncidentReport.objects.get(asset=instance.asset)
#                 transition_state = StateTransition.objects.get_or_create(asset_incident_report=incident_report)
#                 transition_state.incident_report_state = constants.CLOSED
#                 transition_state.save()
#             except AssetIncidentReport.DoesNotExist:
#                 pass
#         else:
#             # incident_report =
#             pass


@receiver(post_save, sender=AssetIncidentReport)
def update_transition_state(**kwargs):
    """
    update the transition state when an Asset incident report is filed
    :param kwargs:
    :return None:
    """
    instance = kwargs.get("instance")  # the instance of the incident report being saved
    current_incident_type = instance.incident_type
    transition_state = StateTransition.objects.get_or_create(
        asset_incident_report=instance
    )
    transition_state = transition_state[0]
    current_transition_state = transition_state.incident_report_state

    # tuples of states for which the logic of this signal is triggered
    valid_incident_types = (constants.LOSS, constants.DAMAGE)
    valid_transition_states = (
        constants.INTERNAL_ASSESSMENT,
        constants.EXTERNAL_ASSESSMENT,
        constants.OUT_FOR_REPAIR,
    )
    # if the current incident type and transition state are valid, update the state
    if (
        current_incident_type in valid_incident_types
        and current_transition_state in valid_transition_states
    ):
        transition_state.incident_report_state = constants.CLOSED
        transition_state.save()
