"""
Django management command to create a demo exam.
Usage: python manage.py create_demo_exam [--teacher-email EMAIL]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from exams.models import Teacher, Question


DEMO_TEST_ID = "DEMO001"
DEMO_PASSWORD = "demo123"
DEMO_QUESTIONS = [
    {
        "q": "What does CPU stand for?",
        "a": "Central Processing Unit",
        "b": "Computer Personal Unit",
        "c": "Central Program Utility",
        "d": "Computer Processing Unit",
        "ans": "a",
    },
    {
        "q": "Which of the following is a programming language?",
        "a": "HTML",
        "b": "Python",
        "c": "CSS",
        "d": "XML",
        "ans": "b",
    },
    {
        "q": "What is the main purpose of an operating system?",
        "a": "To run applications",
        "b": "To manage hardware and software resources",
        "c": "To display graphics",
        "d": "To connect to the internet",
        "ans": "b",
    },
    {
        "q": "Which data structure uses LIFO (Last In, First Out)?",
        "a": "Queue",
        "b": "Array",
        "c": "Stack",
        "d": "Linked List",
        "ans": "c",
    },
    {
        "q": "What does HTTP stand for?",
        "a": "HyperText Transfer Protocol",
        "b": "High Transfer Text Protocol",
        "c": "HyperText Transmission Protocol",
        "d": "High Tech Transfer Process",
        "ans": "a",
    },
]


class Command(BaseCommand):
    help = "Create a demo exam (Test ID: DEMO001, Password: demo123) with sample questions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--teacher-email",
            type=str,
            default=None,
            help="Email of the teacher who will own the demo exam. Uses first teacher if not provided.",
        )

    def handle(self, *args, **options):
        teacher_email = options.get("teacher_email")

        # Get or find teacher user
        if teacher_email:
            try:
                teacher_user = User.objects.get(email=teacher_email, user_type="teacher")
            except User.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"No teacher found with email: {teacher_email}")
                )
                return
        else:
            teacher_user = User.objects.filter(user_type="teacher").first()
            if not teacher_user:
                self.stderr.write(
                    self.style.ERROR(
                        "No teacher user found. Create a teacher account first or use --teacher-email."
                    )
                )
                return

        # Check if demo exam already exists
        if Teacher.objects.filter(test_id=DEMO_TEST_ID).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Demo exam '{DEMO_TEST_ID}' already exists. Skipping creation."
                )
            )
            self.stdout.write(
                f"  Test ID: {DEMO_TEST_ID}\n  Password: {DEMO_PASSWORD}\n  Students can login at: /give-test/"
            )
            return

        # Create Teacher (exam) record
        end_date = timezone.now() + timedelta(days=30)
        teacher = Teacher.objects.create(
            email=teacher_user.email,
            test_id=DEMO_TEST_ID,
            test_type="objective",
            end=end_date,
            duration=10,  # 10 minutes
            show_ans=1,
            password=DEMO_PASSWORD,
            subject="Demo",
            topic="Sample Exam",
            neg_marks=0,
            calc=0,
            proctoring_type=0,
            uid=teacher_user,
        )
        self.stdout.write(self.style.SUCCESS(f"Created exam: {DEMO_TEST_ID}"))

        # Create questions
        for i, qdata in enumerate(DEMO_QUESTIONS, start=1):
            Question.objects.create(
                test_id=DEMO_TEST_ID,
                qid=str(i),
                q=qdata["q"],
                a=qdata["a"],
                b=qdata["b"],
                c=qdata["c"],
                d=qdata["d"],
                ans=qdata["ans"],
                marks=2,
                uid=teacher_user,
            )
        self.stdout.write(self.style.SUCCESS(f"Added {len(DEMO_QUESTIONS)} questions."))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo exam created successfully!"))
        self.stdout.write(f"  Test ID:  {DEMO_TEST_ID}")
        self.stdout.write(f"  Password: {DEMO_PASSWORD}")
        self.stdout.write(f"  Duration: 10 minutes")
        self.stdout.write("")
        self.stdout.write("Students can take the exam at: /give-test/")
