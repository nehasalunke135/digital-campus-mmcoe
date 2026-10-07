from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core_auth.models import User, UserRole
from core_auth.views import ensure_seed_accounts
from interx.models import Internship, Hackathon, OpportunityStatus, WorkMode


class Command(BaseCommand):
    help = "Seeds development accounts and legitimate sample opportunities for InterX testing."

    def handle(self, *args, **options):
        ensure_seed_accounts()
        admin_user = User.objects.get(email="admin@mmcoe.edu.in")
        now = timezone.now()

        # 1. Published Internship
        Internship.objects.get_or_create(
            role_title="Research & Development Intern",
            company_name="Tata Consultancy Services (TCS Research)",
            defaults={
                "description": "Work with researchers and engineers on cutting-edge computer vision and natural language processing applications for enterprise domains.",
                "location": "Pune, Maharashtra",
                "work_mode": WorkMode.HYBRID,
                "duration": "6 Months",
                "stipend": "₹25,000 / month",
                "eligibility": "B.E. / B.Tech Computer, IT, AI&DS (3rd and 4th year) with min 7.5 CGPA.",
                "eligible_branches": ["COMP", "IT", "AIDS"],
                "eligible_years": [3, 4],
                "required_skills": ["Python", "PyTorch", "Data Structures", "Machine Learning"],
                "deadline": now + timedelta(days=20),
                "application_url": "https://www.tcs.com/careers/india/entry-level-hiring",
                "status": OpportunityStatus.PUBLISHED,
                "created_by": admin_user,
            },
        )

        # 2. Published Internship Closing Soon (< 48h)
        Internship.objects.get_or_create(
            role_title="Embedded Firmware Intern",
            company_name="KPIT Technologies",
            defaults={
                "description": "Hands-on project developing micro-controller firmware and AUTOSAR drivers for electric vehicle powertrain modules.",
                "location": "Hinjawadi, Pune",
                "work_mode": WorkMode.ONSITE,
                "duration": "3 Months",
                "stipend": "₹18,000 / month",
                "eligibility": "E&TC and Electrical Engineering students with knowledge of C/C++ and microcontrollers.",
                "eligible_branches": ["ENTC", "ELEC"],
                "eligible_years": [3, 4],
                "required_skills": ["Embedded C", "Microcontrollers", "RTOS", "CAN Protocol"],
                "deadline": now + timedelta(hours=36),
                "application_url": "https://www.kpit.com/careers/",
                "status": OpportunityStatus.PUBLISHED,
                "created_by": admin_user,
            },
        )

        # 3. Pending Internship (for Admin Pending Queue review)
        Internship.objects.get_or_create(
            role_title="Full Stack Software Development Intern",
            company_name="Persistent Systems",
            defaults={
                "description": "Design and implement scalable microservices using Django REST Framework and React for banking client applications.",
                "location": "Pune, Maharashtra",
                "work_mode": WorkMode.HYBRID,
                "duration": "6 Months",
                "stipend": "₹20,000 / month",
                "eligibility": "Open to all engineering branches with strong programming skills.",
                "eligible_branches": ["COMP", "IT", "AIDS", "ENTC"],
                "eligible_years": [3, 4],
                "required_skills": ["Python", "Django", "React", "TypeScript", "PostgreSQL"],
                "deadline": now + timedelta(days=25),
                "application_url": "https://www.persistent.com/careers/",
                "status": OpportunityStatus.PENDING,
                "created_by": admin_user,
            },
        )

        # 4. Published Hackathon
        Hackathon.objects.get_or_create(
            name="Smart India Hackathon 2026",
            organizer="Ministry of Education & AICTE",
            defaults={
                "description": "Nationwide initiative to provide students with a platform to solve pressing problems of society, ministries, and industries.",
                "location": "New Delhi / Nodal Centers across India",
                "mode": WorkMode.HYBRID,
                "registration_deadline": now + timedelta(days=15),
                "event_date": now + timedelta(days=35),
                "team_size": "6 Members",
                "prize_pool": "₹1,00,000 per problem statement",
                "eligibility": "Regular engineering undergraduate students.",
                "required_skills_themes": ["Smart Automation", "Clean Energy", "Heritage & Culture", "Disaster Management"],
                "registration_url": "https://www.sih.gov.in/",
                "status": OpportunityStatus.PUBLISHED,
                "created_by": admin_user,
            },
        )

        # 5. Pending Hackathon (for Admin Pending Queue review)
        Hackathon.objects.get_or_create(
            name="Maharashtra State Innovation Challenge",
            organizer="Maharashtra State Innovation Society (MSInS)",
            defaults={
                "description": "State-level hackathon for developing digital solutions for urban local governance and smart transit.",
                "location": "Mumbai / Pune",
                "mode": WorkMode.HYBRID,
                "registration_deadline": now + timedelta(days=18),
                "event_date": now + timedelta(days=40),
                "team_size": "2-4 Members",
                "prize_pool": "₹5,00,000 Total Cash Prizes",
                "eligibility": "Students studying in Maharashtra state colleges.",
                "required_skills_themes": ["Smart Cities", "GovTech", "Open Data", "IoT"],
                "registration_url": "https://msins.in/",
                "status": OpportunityStatus.PENDING,
                "created_by": admin_user,
            },
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded development accounts and opportunities."))
