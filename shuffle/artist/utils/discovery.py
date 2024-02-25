from django.db import models
from shuffle.curator.models import Concept

from ..models import Opportunity, Subscriber

def discover_opportunities(concept: Concept):
    subscribers = Subscriber.objects\
        .filter(artist__is_active=True)\
        .filter(concept=concept)\
        .filter(concept__curator__organization__is_active=True)\
        .filter(is_subscribed=True)\
        .order_by('-created_at')

    for subscriber in subscribers:
        # Check if subscriber has any opportunities open
        open_opportunities = Opportunity.objects\
            .filter(subscriber=subscribers)\
            .filter(
                models.Q(invite_closed_at__isnull=True) | 
                models.Q(opportunity_closed_at__isnull=True)
            )
        
        if open_opportunities.exists():
            Opportunity\
                .objects\
                .create(
                    concept=subscriber.concept,
                    artist=subscriber.artist,
                    status=Opportunity.OpportunityStatus.POTENTIAL
                )
            
    