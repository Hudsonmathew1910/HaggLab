from django.test import override_settings
from django.test import TestCase
from apps.content.models import Solution, Project, FAQ, SiteSetting

class ContentModelsTest(TestCase):
    def setUp(self):
        self.sol = Solution.objects.create(
            title="Answer faster",
            slug="answer-faster",
            headline="Stop answering repeat questions",
            problem="Questions repeat all day.",
            cost_today="Manual search.",
            step1_desc="Upload docs",
            step2_desc="Assistant retrieves",
            step3_desc="Human reviews",
            expected_outcome="Faster reply",
            metrics="reply time"
        )
        self.proj = Project.objects.create(
            title="DocuMind",
            slug="documind",
            headline="Answers from docs",
            status="Concept",
            problem="Staff repeats questions",
            cost_today="Manual lookup",
            step1_desc="Upload",
            step2_desc="Query",
            step3_desc="Verify"
        )
        self.proj.solutions.add(self.sol)

    def test_project_status_honesty(self):
        # Badge text comes strictly from status field
        self.assertEqual(self.proj.status, "Concept")
        self.assertEqual(self.proj.status_slug, "concept")

    def test_measured_text_empty_by_default(self):
        # Result block must hide if measured_text is empty
        self.assertEqual(self.proj.measured_text, "")

    def test_site_setting_creation(self):
        setting = SiteSetting.objects.create(key="test_key", label="Test Setting", value="")
        self.assertEqual(setting.value, "")


@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
                            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class ProjectAdminTest(TestCase):
    def test_project_with_old_demo_path_saves_in_admin(self):
        from django.contrib.auth.models import User
        from django.urls import reverse as r
        admin_user = User.objects.create_superuser('boss', 'boss@example.com', 'pw-12345-long')
        self.client.force_login(admin_user)
        from apps.content.models import Project
        project = Project.objects.create(title='DocuMind', slug='documind', headline='h', problem='p',
                                         cost_today='c', step1_desc='a', step2_desc='b', step3_desc='c',
                                         demo_url='/demos/documind/')
        page = self.client.get(r('admin:content_app_project_changelist'))
        self.assertContains(page, 'Try ready')
        form = self.client.get(r('admin:content_app_project_change', args=[project.pk]))
        self.assertNotContains(form, 'name="demo_url"')
