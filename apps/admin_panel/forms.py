"""
Forms for Admin Panel
"""
from django import forms
from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker
from apps.authentication.models import User

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
        # Style all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            # Remove HTML5 required attribute to avoid conflicts with dynamic form sections
            # Django model validation will handle required field checking
            field.widget.attrs.pop('required', None)
        
        # Make optional fields not required in Django form validation
        self.fields['company_name'].required = False
        self.fields['sector'].required = False
        self.fields['target_2'].required = False
        self.fields['target_3'].required = False
        self.fields['timeframe_days'].required = False
        self.fields['rationale'].required = False



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
        # Style all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

