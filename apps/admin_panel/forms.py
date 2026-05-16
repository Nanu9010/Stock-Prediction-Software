"""
Forms for Admin Panel
"""
import json

from django import forms
from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker
from apps.authentication.models import User
from apps.payments.models import SubscriptionPlan
from apps.market_data.models import IPO, Commodity, ETF, SIP


class CommodityForm(forms.ModelForm):
    """Form for creating and editing Commodities"""
    
    class Meta:
        model = Commodity
        fields = [
            'name', 'symbol', 'unit', 'icon', 'is_global', 
            'mcx_multiplier', 'is_active', 'display_order'
        ]
        widgets = {
            'mcx_multiplier': forms.NumberInput(attrs={'step': '0.0001'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})


class ETFForm(forms.ModelForm):
    """Form for creating and editing ETFs"""
    
    class Meta:
        model = ETF
        fields = [
            'name', 'symbol', 'short_name', 'category', 
            'is_active', 'display_order'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})


class SIPForm(forms.ModelForm):
    """Form for creating and editing SIPs"""
    
    class Meta:
        model = SIP
        fields = [
            'name', 'category', 'min_sip', 'returns_1y', 
            'returns_3y', 'returns_5y', 'popularity', 
            'is_active', 'display_order'
        ]
        widgets = {
            'returns_1y': forms.NumberInput(attrs={'step': '0.01'}),
            'returns_3y': forms.NumberInput(attrs={'step': '0.01'}),
            'returns_5y': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})


class IPOForm(forms.ModelForm):
    """Form for creating and editing IPOs"""
    
    class Meta:
        model = IPO
        fields = [
            'company_name', 'symbol', 'sector', 'price_band', 'issue_price',
            'issue_size', 'lot_size', 'open_date', 'close_date', 'listing_date',
            'gmp', 'listing_price', 'is_listed'
        ]
        widgets = {
            'open_date': forms.DateInput(attrs={'type': 'date'}),
            'close_date': forms.DateInput(attrs={'type': 'date'}),
            'listing_date': forms.DateInput(attrs={'type': 'date'}),
            'issue_price': forms.NumberInput(attrs={'step': '0.01'}),
            'listing_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})


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

    features_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Enter one feature per line.',
        label='Plan Features',
    )
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'plan_type', 'price_monthly', 'price_yearly',
            'max_calls_per_month', 'display_order', 'is_active'
        ]
        widgets = {
            'price_monthly': forms.NumberInput(attrs={'step': '0.01'}),
            'price_yearly': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['features_text'].initial = '\n'.join(self.instance.features or [])
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_features_text(self):
        raw_value = self.cleaned_data.get('features_text', '')
        if not raw_value:
            return []
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [line.strip() for line in raw_value.splitlines() if line.strip()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.features = self.cleaned_data['features_text']
        if commit:
            instance.save()
        return instance


# PortfolioForm and WatchlistForm are not needed since admin only views/deletes them
# These are user-created entities, but admin may need to create for testing
class PortfolioForm(forms.Form):
    """Placeholder — portfolios are created by users"""
    pass


class WatchlistForm(forms.Form):
    """Placeholder — watchlists are created by users"""
    pass
