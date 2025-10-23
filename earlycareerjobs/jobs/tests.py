from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .forms import JobSearchForm
from .models import Job


class JobSearchFormTests(TestCase):
    def test_form_valid_without_filters(self):
        form = JobSearchForm({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["work_style"], "")

    def test_salary_range_validation_blocks_reversed_values(self):
        form = JobSearchForm({"salary_min": "100000", "salary_max": "50000"})
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Maximum salary must be greater than minimum salary.",
            form.errors["salary_max"],
        )

    def test_accepts_all_configured_work_styles(self):
        for value, _ in Job.WorkStyle.choices:
            form = JobSearchForm({"work_style": value})
            self.assertTrue(form.is_valid(), msg=f"Expected '{value}' to be accepted")
            self.assertEqual(form.cleaned_data["work_style"], value)

    def test_rejects_unknown_work_style_value(self):
        form = JobSearchForm({"work_style": "travel"})
        self.assertFalse(form.is_valid())
        self.assertIn("work_style", form.errors)


class JobListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.remote_job = Job.objects.create(
            title="Software Engineer",
            skills="Python, Django",
            city="Atlanta",
            state="GA",
            country="USA",
            salary_min=Decimal("85000"),
            salary_max=Decimal("120000"),
            work_style=Job.WorkStyle.REMOTE,
            visa_sponsorship=True,
        )
        cls.onsite_job = Job.objects.create(
            title="Data Analyst",
            skills="SQL, Tableau",
            city="Austin",
            state="TX",
            country="USA",
            salary_min=Decimal("65000"),
            salary_max=Decimal("88000"),
            work_style=Job.WorkStyle.ONSITE,
            visa_sponsorship=False,
        )
        cls.hybrid_job = Job.objects.create(
            title="Product Manager",
            skills="Agile, Communication",
            city="New York",
            state="NY",
            country="USA",
            salary_min=Decimal("95000"),
            salary_max=Decimal("125000"),
            work_style=Job.WorkStyle.HYBRID,
            visa_sponsorship=True,
        )

    def _job_ids(self, response):
        return {job.id for job in response.context["jobs"]}

    def test_view_returns_all_jobs_without_filters(self):
        response = self.client.get(reverse("home.index"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], JobSearchForm)
        self.assertSetEqual(
            self._job_ids(response),
            {self.remote_job.id, self.onsite_job.id, self.hybrid_job.id},
        )

    def test_filter_by_title_keyword(self):
        response = self.client.get(reverse("home.index"), {"title": "Engineer"})
        self.assertSetEqual(self._job_ids(response), {self.remote_job.id})

    def test_filter_by_skill_keyword(self):
        response = self.client.get(reverse("home.index"), {"skills": "SQL"})
        self.assertSetEqual(self._job_ids(response), {self.onsite_job.id})

    def test_filter_by_salary_range(self):
        response = self.client.get(
            reverse("home.index"),
            {"salary_min": "90000", "salary_max": "130000"},
        )
        self.assertSetEqual(
            self._job_ids(response),
            {self.hybrid_job.id},
        )

    def test_filter_by_visa_sponsorship(self):
        response = self.client.get(reverse("home.index"), {"visa_sponsorship": "on"})
        self.assertSetEqual(
            self._job_ids(response),
            {self.remote_job.id, self.hybrid_job.id},
        )

    def test_filter_by_work_style(self):
        response = self.client.get(
            reverse("home.index"),
            {"work_style": Job.WorkStyle.ONSITE},
        )
        self.assertSetEqual(self._job_ids(response), {self.onsite_job.id})

    def test_combined_filters(self):
        response = self.client.get(
            reverse("home.index"),
            {
                "title": "Manager",
                "work_style": Job.WorkStyle.HYBRID,
                "visa_sponsorship": "on",
            },
        )
        self.assertSetEqual(self._job_ids(response), {self.hybrid_job.id})
