from django.db.models.signals import post_save, pre_delete, pre_save, post_delete
from django.dispatch import receiver
from .models import *
import requests
import urllib.parse


@receiver(post_save, sender=Task)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
	if instance.assigned_to and instance.assigned_to.email and instance.business.is_premium:
		message = f"""<p>Hello {instance.assigned_to.first_name},</p>

	<p>You have been assigned a new task: <strong>{instance.name}</strong>.</p>

	<ul>
	<li><strong>Deadline:</strong> {instance.deadline if instance.deadline else "No deadline"}</li>
	<li><strong>Priority:</strong> {instance.priority}</li>
	</ul>

	<p>Please check your task list for more details.</p>

	<p>Regards,<br>{instance.business.name} Team</p>
	"""

		encoded_message = urllib.parse.quote(message)

		url = f"https://salesprogrow.com/api/msg/?msg={encoded_message}&email={instance.assigned_to.email}"
		response = requests.get(url)
