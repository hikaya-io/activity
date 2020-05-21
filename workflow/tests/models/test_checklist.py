
from django.test import TestCase
from workflow.models import (
    ActivityUser,
    Checklist,
    ChecklistItem,
    Country,
    Office,
    Program,
    ProjectAgreement,
    ProjectType,
    Sector,
)


class ChecklistItemTest(TestCase):

    fixtures = [
        'fixtures/tests/activity-users.json',
        'fixtures/tests/offices.json',
        'fixtures/tests/organization.json',
        'fixtures/tests/programs.json',
        'fixtures/tests/projecttype.json',
        'fixtures/tests/sectors.json',
        'fixtures/tests/users.json',
        'fixtures/countries.json',
    ]

    def setUp(self):
        ProjectAgreement.objects.create(
            project_name="testproject",
            activity_code="111222",
            program=Program.objects.first(),
            project_type=ProjectType.objects.first(),
            office=Office.objects.first(),
            sector=Sector.objects.first(),
        )
        Checklist.objects.create(
            name="test checklist created",
            country=Country.objects.first(),
            agreement=ProjectAgreement.objects.first(),
        )
        ChecklistItem.objects.create(
            item="checklistitem",
            checklist=Checklist.objects.first(),
            owner=ActivityUser.objects.first(),
        )

    def test_checklistitem_creation(self):
        """Check for ChecklistItem Object creation"""
        checklistItem = ChecklistItem.objects.get(item="checklistitem")
        self.assertIsInstance(checklistItem, ChecklistItem)
        self.assertEqual(checklistItem.item, checklistItem.__str__())
        self.assertEqual(ChecklistItem.objects.filter(
            item=checklistItem.item).count(), 1)
        self.assertFalse(checklistItem.in_file)
        self.assertFalse(checklistItem.not_applicable)
        self.assertFalse(checklistItem.global_item)
        self.assertIsInstance(checklistItem.owner, ActivityUser)
