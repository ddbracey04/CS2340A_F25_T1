from django import forms
from .models import Job


# class JobForm(forms.ModelForm):
#     class Meta:
#         model = Job
#         fields = ("title", "description", "image", "lat", "lon")
#         widgets = {
#             "description": forms.Textarea(attrs={"rows": 4}),
#         }

class JobSearchForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ("title", 
                  "description", 
                  "image", 
                  "lat", 
                  "lon",
                  "skills",
                  "city",
                  "state",
                  "country",
                  "salary_min",
                  "salary_max",
                  "work_style",
                  "visa_sponsorship")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "title": "Job title or keywords",
            "skills": "Key skills (comma separated)",
            "city": "City",
            "state": "State",
            "country": "Country",
            "salary_min": "Min salary",
            "salary_max": "Max salary",
        }

        for field_name, field in self.fields.items():
            widget = field.widget
            widget.attrs.setdefault("class", "")
            classes = widget.attrs["class"].split()

            widget_type = getattr(widget, "input_type", None)
            widget_name = widget.__class__.__name__

            if widget_type in ("text", "number") or widget_name in ("Textarea", "TextInput", "NumberInput"):
                classes.append("form-control")
            elif widget_name in ("Select", "SelectMultiple"):
                classes.append("form-select")
            elif widget_name == "CheckboxInput":
                classes.append("form-check-input")

            widget.attrs["class"] = " ".join(filter(None, classes))

        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("placeholder", text)
        

    # skills = forms.CharField(required=False, label="Skills (comma separated)")
    # city = forms.CharField(required=False)
    # state = forms.CharField(required=False)
    # country = forms.CharField(required=False)
    # salary_min = forms.DecimalField(required=False, min_value=0, label="Minimum salary")
    # salary_max = forms.DecimalField(required=False, min_value=0, label="Maximum salary")
    # work_style = forms.ChoiceField(
    #     required=False,
    #     choices=[("", "Any")] + list(Job.WorkStyle.choices),
    #     label="Remote / On-site",
    # )
    # visa_sponsorship = forms.BooleanField(required=False, label="Visa sponsorship")

    def clean(self):
        data = super().clean()
        min_salary = data.get("salary_min")
        max_salary = data.get("salary_max")
        if min_salary and max_salary and min_salary > max_salary:
            self.add_error("salary_max", "Maximum salary must be greater than minimum salary.")
        return data
