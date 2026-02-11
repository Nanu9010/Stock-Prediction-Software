from django import forms
from .models import ResearchCall

class ResearchCallForm(forms.ModelForm):
    class Meta:
        model = ResearchCall
        fields = [
            'symbol', 'exchange', 'company_name', 'sector', 'instrument_type',
            'call_type', 'action', 'entry_price', 'target_1', 'target_2', 'target_3', 'stop_loss',
            'timeframe_days', 'rationale', 'broker', 'expires_at'
        ]
        widgets = {
            'rationale': forms.Textarea(attrs={'rows': 5}),
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # The model's clean method handles most validation logic (price relationships)
        # We can trigger it here or let the model instance validation handle it during save,
        # but calling model.clean() explicitly is often good practice in forms if not using ModelForm's save() immediately 
        # or to catch errors early. ModelForm.clean() usually calls model.clean() unless overridden/customized.
        # However, for specific field interactions, we can rely on model.clean() which is called by ModelForm validation.
        return cleaned_data
