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
