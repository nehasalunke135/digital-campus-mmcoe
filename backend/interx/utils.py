from django.utils import timezone
from datetime import timedelta
from .models import Internship, Hackathon, OpportunityStatus


def update_expired_opportunities():
    """
    Lazy expiry handling:
    Transitions PUBLISHED -> EXPIRED when deadline or registration_deadline has passed.
    Uses timezone.now() against project configured TIME_ZONE.
    """
    now = timezone.now()

    # Update expired internships
    Internship.objects.filter(
        status=OpportunityStatus.PUBLISHED,
        deadline__lte=now,
    ).update(status=OpportunityStatus.EXPIRED)

    # Update expired hackathons
    Hackathon.objects.filter(
        status=OpportunityStatus.PUBLISHED,
        registration_deadline__lte=now,
    ).update(status=OpportunityStatus.EXPIRED)


def is_closing_soon(deadline_dt, hours=48):
    """
    Returns True if deadline is in the future but within `hours` from now.
    Display concern only — does not alter database status.
    """
    if not deadline_dt:
        return False
    now = timezone.now()
    return now < deadline_dt <= (now + timedelta(hours=hours))
