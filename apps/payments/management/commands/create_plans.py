"""
Management command to create default subscription plans
"""
from django.core.management.base import BaseCommand
from apps.payments.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create default subscription plans'
    
    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Basic',
                'plan_type': 'BASIC',
                'price_monthly': 499,
                'price_yearly': 4990,
                'features': [
                    '10 research calls per month',
                    'Basic market insights',
                    'Email support',
                    'Mobile app access',
                    'Portfolio tracking'
                ],
                'max_calls_per_month': 10,
                'display_order': 1
            },
            {
                'name': 'PRO',
                'plan_type': 'PRO',
                'price_monthly': 999,
                'price_yearly': 9990,
                'features': [
                    'Unlimited research calls',
                    'Advanced analytics',
                    'Priority support',
                    'Portfolio tracking',
                    'Real-time alerts',
                    'Expert webinars',
                    'All trade categories',
                    'Performance reports'
                ],
                'max_calls_per_month': -1,
                'display_order': 2
            },
            {
                'name': 'Premium',
                'plan_type': 'PREMIUM',
                'price_monthly': 1999,
                'price_yearly': 19990,
                'features': [
                    'Everything in PRO',
                    'Dedicated analyst',
                    '1-on-1 consultations',
                    'Custom strategies',
                    'API access',
                    '24/7 phone support',
                    'Priority call execution',
                    'Exclusive research reports'
                ],
                'max_calls_per_month': -1,
                'display_order': 3
            }
        ]
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.update_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created plan: {plan.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'↻ Updated plan: {plan.name}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Successfully created/updated all subscription plans!'))
