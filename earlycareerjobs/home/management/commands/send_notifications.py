from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from home.models import SavedSearch, Profile
from users.models import CustomUser
from django.db.models import Q

class Command(BaseCommand):
    help = 'Sends email notifications to recruiters about new candidates matching their saved searches.'

    def handle(self, *args, **options):
        self.stdout.write("Starting to process saved searches for notifications...")

        active_searches = SavedSearch.objects.filter(is_notification_active=True)

        for search in active_searches:
            recruiter = search.recruiter
            
            # Determine the cutoff time for "new" candidates
            # If never notified, check all candidates. Otherwise, check since last notification.
            cutoff_time = search.last_notified or recruiter.date_joined

            # Find new candidates created after the cutoff time
            new_profiles_query = Profile.objects.filter(
                user__role=CustomUser.Role.JOB_SEEKER,
                user__date_joined__gt=cutoff_time,
                privacy__is_profile_visible=True
            )

            # Apply search filters to the new candidates
            matching_new_candidates = self.filter_profiles(new_profiles_query, search)

            if matching_new_candidates.exists():
                self.stdout.write(self.style.SUCCESS(
                    f"Found {matching_new_candidates.count()} new candidates for search '{search.name}' by {recruiter.username}."
                ))
                
                # Send email notification
                self.send_notification_email(recruiter, search, matching_new_candidates)

                # Update the last_notified timestamp
                search.last_notified = timezone.now()
                search.save()
            else:
                self.stdout.write(
                    f"No new candidates for search '{search.name}' by {recruiter.username}."
                )

        self.stdout.write(self.style.SUCCESS("Finished processing all active saved searches."))

    def filter_profiles(self, profiles, search):
        # Skills filter
        if search.skills:
            skills_list = [s.strip() for s in search.skills.split(',') if s.strip()]
            if skills_list:
                if search.skills_mode == 'AND':
                    for skill in skills_list:
                        profiles = profiles.filter(skills__icontains=skill)
                else: # OR
                    skill_query = Q()
                    for skill in skills_list:
                        skill_query |= Q(skills__icontains=skill)
                    profiles = profiles.filter(skill_query)

        # Experience filter
        if search.experience:
            profiles = profiles.filter(experience__icontains=search.experience)

        # Work style filter
        if search.work_style:
            profiles = profiles.filter(work_style_preference=search.work_style)

        # Location/Distance filter is more complex and might require a different approach
        # For simplicity, this example will not re-implement the distance filter.
        # A full implementation would require geocoding and Haversine distance calculation.

        return profiles

    def send_notification_email(self, recruiter, search, candidates):
        subject = f"New Candidates Match Your Saved Search: '{search.name}'"
        
        context = {
            'recruiter_name': recruiter.get_full_name() or recruiter.username,
            'search_name': search.name,
            'candidates': candidates,
            'search_url': search.query_params, # This needs to be a full URL
        }
        
        html_message = render_to_string('home/email/new_candidates_notification.html', context)
        
        send_mail(
            subject,
            '', # Plain text version (can be generated from HTML)
            'from@example.com', # Sender's email
            [recruiter.email],
            html_message=html_message,
            fail_silently=False,
        )
