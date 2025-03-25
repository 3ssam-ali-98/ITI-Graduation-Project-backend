from django.db.models.signals import post_save, pre_delete, pre_save, post_delete
from django.dispatch import receiver
from .models import *
import requests


@receiver(post_save, sender=Task)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
	msg = 'You have been assigned to a new task'
	if instance.assigned_to:
		requests.get(url=f"https://salesprogrow.com/api/msg/?msg={msg}&email={instance.assigned_to.email}")
