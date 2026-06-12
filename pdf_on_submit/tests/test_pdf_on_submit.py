# Copyright (c) 2023, Raffael Meyer and contributors
# For license information, please see license.txt

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from pdf_on_submit.utils import extend_boot_info, get_print_details

TEST_DOCTYPE = "Test Submittable DocType"


class TestPDFOnSubmit(FrappeTestCase):
	def setUp(self) -> None:
		create_submittable_doctype(TEST_DOCTYPE)

	def tearDown(self) -> None:
		frappe.db.rollback()

	def test_pdf_on_submit(self):
		settings = frappe.get_single("PDF on Submit Settings")
		settings.append("enabled_for", {"document_type": TEST_DOCTYPE})
		settings.create_pdf_in_background = 0
		settings.save()

		doc = frappe.new_doc(TEST_DOCTYPE)
		doc.title = "Test PDF on Submit"
		doc.save()
		doc.submit()

		attached_file = frappe.db.exists(
			"File", {"attached_to_doctype": TEST_DOCTYPE, "attached_to_name": doc.name}
		)

		self.assertIsNotNone(attached_file)

		file = frappe.get_doc("File", attached_file)
		file_name: str = file.get("file_name", "")

		self.assertIsNotNone(file_name)
		self.assertTrue(file_name.startswith(doc.name))
		self.assertTrue(file_name.endswith("pdf"))


def create_submittable_doctype(name: str):
	frappe.delete_doc_if_exists("DocType", name)

	submittable_doctype = frappe.new_doc("DocType")
	submittable_doctype.module = "Custom"
	submittable_doctype.custom = 1
	submittable_doctype.name = name
	submittable_doctype.is_submittable = 1
	submittable_doctype.append(
		"fields",
		{
			"fieldname": "title",
			"fieldtype": "Data",
			"label": "Title",
		},
	)
	submittable_doctype.append(
		"fields",
		{
			"fieldname": "letter_head",
			"fieldtype": "Data",
			"label": "Letter Head",
		},
	)
	submittable_doctype.save()


class TestGetPrintDetails(FrappeTestCase):
	def setUp(self) -> None:
		create_submittable_doctype(TEST_DOCTYPE)
		self.settings = frappe.get_single("PDF on Submit Settings")
		self.settings.save()

		self.doc = frappe.new_doc(TEST_DOCTYPE)
		self.doc.title = "Test Get Print Details"
		self.doc.save()

	def tearDown(self) -> None:
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_rejects_without_print_permission(self):
		with patch("frappe.has_permission", return_value=False):
			with self.assertRaises(frappe.ValidationError):
				get_print_details(TEST_DOCTYPE, self.doc.name)

	def test_returns_standard_when_no_match(self):
		results = get_print_details(TEST_DOCTYPE, self.doc.name)
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]["print_format"], "Standard")
		self.assertIsNone(results[0]["letter_head"])

	def test_returns_matched_config_print_format(self):
		# Use a non-default value so the assertion proves the override ran.
		self.settings.append(
			"enabled_for",
			{"document_type": TEST_DOCTYPE, "print_format": "Custom Format", "letter_head": ""},
		)
		self.settings.flags.ignore_links = True
		self.settings.save()
		results = get_print_details(TEST_DOCTYPE, self.doc.name)
		self.assertEqual(results[0]["print_format"], "Custom Format")

	def test_returns_matched_config_letter_head(self):
		self.settings.append(
			"enabled_for",
			{"document_type": TEST_DOCTYPE, "print_format": "", "letter_head": "Custom Letter Head"},
		)
		self.settings.flags.ignore_links = True
		self.settings.save()
		results = get_print_details(TEST_DOCTYPE, self.doc.name)
		self.assertEqual(results[0]["letter_head"], "Custom Letter Head")

	def test_letter_head_falls_back_to_doc(self):
		self.doc.letter_head = "Test Letter Head"
		self.doc.save()
		with patch("pdf_on_submit.utils.iter_matching_enabled_doctypes", return_value=iter([])):
			results = get_print_details(TEST_DOCTYPE, self.doc.name)
		self.assertEqual(results[0]["letter_head"], "Test Letter Head")

	def test_returns_one_entry_per_matching_row(self):
		self.settings.append(
			"enabled_for",
			{"document_type": TEST_DOCTYPE, "print_format": "Format A", "letter_head": ""},
		)
		self.settings.append(
			"enabled_for",
			{"document_type": TEST_DOCTYPE, "print_format": "Format B", "letter_head": ""},
		)
		self.settings.flags.ignore_links = True
		self.settings.save()
		results = get_print_details(TEST_DOCTYPE, self.doc.name)
		self.assertEqual([r["print_format"] for r in results], ["Format A", "Format B"])


class TestExtendBootInfo(FrappeTestCase):
	def setUp(self) -> None:
		create_submittable_doctype(TEST_DOCTYPE)
		self.settings = frappe.get_single("PDF on Submit Settings")
		self.settings.show_pdf_button = 1
		self.settings.append("enabled_for", {"document_type": TEST_DOCTYPE})
		self.settings.save()

	def tearDown(self) -> None:
		frappe.db.rollback()

	def test_boot_info_includes_enabled_doctype(self):
		bootinfo = frappe._dict()
		extend_boot_info(bootinfo)
		self.assertEqual(bootinfo.pdf_on_submit.show_pdf_button, 1)
		self.assertIn(TEST_DOCTYPE, bootinfo.pdf_on_submit.enabled_doctypes)

	def test_boot_info_show_pdf_button_reflects_setting(self):
		self.settings.show_pdf_button = 0
		self.settings.save()
		bootinfo = frappe._dict()
		extend_boot_info(bootinfo)
		self.assertEqual(bootinfo.pdf_on_submit.show_pdf_button, 0)
		self.assertEqual(bootinfo.pdf_on_submit.enabled_doctypes, [])
