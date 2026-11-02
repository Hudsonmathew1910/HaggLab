"""Refresh Haggi's knowledge as soon as anything it reads from is saved or deleted in the admin."""
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from apps.content.models import FAQ, FiverrGig, Product, Project, SiteSetting, Solution

from . import knowledge

WATCHED = (Solution, Project, FAQ, FiverrGig, SiteSetting, Product)


@receiver(post_save)
@receiver(post_delete)
def content_changed(sender, **kwargs):
    if sender in WATCHED:
        knowledge.clear()


@receiver(m2m_changed)
def links_changed(sender, **kwargs):
    # Project <-> service and gig <-> project/service links
    if sender in (Project.solutions.through, FiverrGig.projects.through, FiverrGig.services.through):
        knowledge.clear()
