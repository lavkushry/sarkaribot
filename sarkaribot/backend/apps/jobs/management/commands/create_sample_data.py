"""
Django management command to create sample data for testing.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.jobs.models import JobCategory, JobPosting
from apps.sources.models import GovernmentSource
import random


class Command(BaseCommand):
    help = 'Create sample data for testing SarkariBot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of job postings to create (default: 20)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Creating {count} sample job postings...')
        )
        
        # Create sample categories
        categories_data = [
            {'name': 'Latest Jobs', 'slug': 'latest-jobs', 'position': 1},
            {'name': 'Admit Card', 'slug': 'admit-card', 'position': 2},
            {'name': 'Answer Key', 'slug': 'answer-key', 'position': 3},
            {'name': 'Result', 'slug': 'result', 'position': 4},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = JobCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  ✅ Created category: {category.name}')
        
        # Create sample government sources
        sources_data = [
            {
                'name': 'SSC',
                'display_name': 'Staff Selection Commission',
                'base_url': 'https://ssc.nic.in',
                'description': 'Staff Selection Commission conducts recruitment for various Group B and Group C posts.'
            },
            {
                'name': 'UPSC',
                'display_name': 'Union Public Service Commission', 
                'base_url': 'https://upsc.gov.in',
                'description': 'Union Public Service Commission conducts Civil Services and other examinations.'
            },
            {
                'name': 'Railway',
                'display_name': 'Railway Recruitment Board',
                'base_url': 'https://www.rrbcdg.gov.in',
                'description': 'Railway Recruitment Boards conduct recruitment for Indian Railways.'
            },
            {
                'name': 'Bank',
                'display_name': 'Banking Recruitment',
                'base_url': 'https://www.ibps.in',
                'description': 'Various banking recruitment through IBPS and individual banks.'
            },
        ]
        
        sources = []
        for source_data in sources_data:
            source, created = GovernmentSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            sources.append(source)
            if created:
                self.stdout.write(f'  ✅ Created source: {source.display_name}')
        
        # Sample job titles and descriptions
        job_templates = [
            {
                'title': 'Junior Engineer (Civil) Recruitment 2025',
                'department': 'Ministry of Railways',
                'qualification': 'Diploma in Civil Engineering',
                'posts': 500
            },
            {
                'title': 'Staff Selection Commission Multi Tasking Staff 2025',
                'department': 'Staff Selection Commission',
                'qualification': '10th Pass',
                'posts': 10000
            },
            {
                'title': 'Bank Probationary Officer Recruitment 2025',
                'department': 'State Bank of India',
                'qualification': 'Graduate in any discipline',
                'posts': 2000
            },
            {
                'title': 'UPSC Civil Services Examination 2025',
                'department': 'Union Public Service Commission',
                'qualification': 'Graduate degree from recognized university',
                'posts': 1000
            },
            {
                'title': 'Junior Hindi Translator Recruitment',
                'department': 'Ministry of Home Affairs',
                'qualification': 'Master Degree in Hindi with English as subject',
                'posts': 50
            },
            {
                'title': 'Constable General Duty Recruitment 2025',
                'department': 'Central Armed Police Forces',
                'qualification': '12th Pass',
                'posts': 5000
            },
            {
                'title': 'Assistant Commandant CRPF Recruitment',
                'department': 'Central Reserve Police Force',
                'qualification': 'Bachelor Degree',
                'posts': 100
            },
            {
                'title': 'Income Tax Inspector Recruitment 2025',
                'department': 'Central Board of Direct Taxes',
                'qualification': 'Graduate with 60% marks',
                'posts': 300
            },
        ]
        
        # Create sample job postings
        created_jobs = 0
        statuses = ['announced', 'admit_card', 'answer_key', 'result']
        
        for i in range(count):
            template = random.choice(job_templates)
            source = random.choice(sources)
            status = random.choice(statuses)
            
            # Find appropriate category based on status
            category = None
            for cat in categories:
                if status in cat.slug or status.replace('_', '-') in cat.slug:
                    category = cat
                    break
            if not category:
                category = categories[0]  # Default to first category
            
            # Generate dates
            notification_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
            application_end_date = notification_date + timedelta(days=random.randint(15, 45))
            
            # Create job posting
            job_title = f"{template['title']} - {source.name}"
            if i > 0:
                job_title += f" ({i+1})"
            
            job = JobPosting.objects.create(
                title=job_title,
                description=f"""
                <p>Applications are invited for the post of {template['title']} in {template['department']}.</p>
                
                <h3>Post Details:</h3>
                <ul>
                    <li>Total Posts: {template['posts']}</li>
                    <li>Department: {template['department']}</li>
                    <li>Qualification: {template['qualification']}</li>
                </ul>
                
                <h3>Important Dates:</h3>
                <ul>
                    <li>Notification Date: {notification_date.strftime('%d-%m-%Y')}</li>
                    <li>Last Date to Apply: {application_end_date.strftime('%d-%m-%Y')}</li>
                </ul>
                
                <h3>Age Limit:</h3>
                <p>18 to 27 years (relaxation as per government rules)</p>
                
                <h3>Application Fee:</h3>
                <p>General/OBC: Rs. 100, SC/ST/PWD: No Fee</p>
                """,
                short_description=f"Apply for {template['title']} - {template['posts']} posts. Last date: {application_end_date.strftime('%d %b %Y')}",
                source=source,
                category=category,
                status=status,
                department=template['department'],
                total_posts=template['posts'],
                qualification=template['qualification'],
                notification_date=notification_date,
                application_end_date=application_end_date,
                min_age=18,
                max_age=27,
                application_fee='100',
                application_link=f'https://{source.name.lower()}.nic.in/apply',
                notification_pdf=f'https://{source.name.lower()}.nic.in/notification.pdf',
                source_url=f'https://{source.name.lower()}.nic.in/jobs/{i+1}',
            )
            
            created_jobs += 1
            
            if created_jobs % 5 == 0:
                self.stdout.write(f'  📝 Created {created_jobs} jobs...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully created {created_jobs} sample job postings!'
            )
        )
        
        # Print summary
        self.stdout.write('\n📊 SUMMARY:')
        self.stdout.write(f'  • Categories: {JobCategory.objects.count()}')
        self.stdout.write(f'  • Sources: {GovernmentSource.objects.count()}')
        self.stdout.write(f'  • Job Postings: {JobPosting.objects.count()}')
        
        # Print status distribution
        self.stdout.write('\n📈 Status Distribution:')
        for status_code, status_name in JobPosting.STATUS_CHOICES:
            count = JobPosting.objects.filter(status=status_code).count()
            self.stdout.write(f'  • {status_name}: {count}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Sample data creation completed!')
        )
