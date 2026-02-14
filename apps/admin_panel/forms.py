"""
Forms for Admin Panel
"""
from django import forms
from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker
from apps.authentication.models import User
from apps.subscriptions.models import SubscriptionPlan


class ResearchCallForm(forms.ModelForm):
    """Form for creating and editing research calls"""
    
    class Meta:
        model = ResearchCall
        fields = [
            'symbol', 'exchange', 'company_name', 'sector', 'instrument_type',
            'call_type', 'action', 'entry_price', 'target_1', 'target_2', 'target_3',
            'stop_loss', 'timeframe_days', 'rationale', 'broker', 'status'
        ]
        widgets = {
            'rationale': forms.Textarea(attrs={'rows': 4}),
            'entry_price': forms.NumberInput(attrs={'step': '0.05'}),
            'target_1': forms.NumberInput(attrs={'step': '0.05'}),
            'target_2': forms.NumberInput(attrs={'step': '0.05'}),
            'target_3': forms.NumberInput(attrs={'step': '0.05'}),
            'stop_loss': forms.NumberInput(attrs={'step': '0.05'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            field.widget.attrs.pop('required', None)
        
        self.fields['exchange'].required = False
        self.fields['company_name'].required = False
        self.fields['sector'].required = False
        self.fields['target_2'].required = False
        self.fields['target_3'].required = False
        self.fields['timeframe_days'].required = False
        self.fields['rationale'].required = False

    def clean(self):
        cleaned_data = super().clean()
        instrument_type = cleaned_data.get('instrument_type')
        exchange = cleaned_data.get('exchange')

        # Set default exchange if not provided
        if not exchange:
            if instrument_type == 'COMMODITY':
                cleaned_data['exchange'] = 'MCX'
            else:
                cleaned_data['exchange'] = 'NSE'
        
        return cleaned_data


class BrokerForm(forms.ModelForm):
    """Form for creating and editing brokers"""
    
    class Meta:
        model = Broker
        fields = [
            'name', 'description', 'website_url', 'sebi_registration_no',
            'is_active', 'is_verified'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class UserForm(forms.ModelForm):
    """Form for admin editing of users"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class SubscriptionPlanForm(forms.ModelForm):
    """Form for creating/editing subscription plans"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'slug', 'description', 'price_monthly', 'price_yearly',
            'access_intraday', 'access_swing', 'access_shortterm', 'access_longterm',
            'access_futures', 'access_options', 'display_order', 'is_active', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price_monthly': forms.NumberInput(attrs={'step': '0.01'}),
            'price_yearly': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# PortfolioForm and WatchlistForm are not needed since admin only views/deletes them
# These are user-created entities, but admin may need to create for testing
class PortfolioForm(forms.Form):
    """Placeholder — portfolios are created by users"""
    pass


class WatchlistForm(forms.Form):
    """Placeholder — watchlists are created by users"""
    pass
