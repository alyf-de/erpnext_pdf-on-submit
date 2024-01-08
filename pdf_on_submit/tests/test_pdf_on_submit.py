import frappe
from frappe.tests.utils import FrappeTestCase

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
	submittable_doctype.save()
