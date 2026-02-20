import frappe
from frappe import _
from pdf_on_submit.attach_pdf import get_matching_enabled_doctype


ALLOWED_DOCTYPES = [
	"Quotation",
	"Sales Order",
	"Sales Invoice",
	"Delivery Note",
	"Dunning",
	"Request for Quotation",
	"Supplier Quotation",
	"Purchase Order",
	"Purchase Invoice",
	"Purchase Receipt",
]


@frappe.whitelist()
def get_print_details(doctype: str, docname: str) -> tuple:
	"""
	Get print format and letter head for a document based on PDF on Submit Settings.

	Returns: (print_format, letter_head)
	"""
	if doctype not in ALLOWED_DOCTYPES:
		frappe.throw(_("Print details not available for this document type"))

	if not frappe.has_permission(doctype, "print", docname):
		frappe.throw(_("No permission to print this document"))

	doc = frappe.get_doc(doctype, docname)
	print_format = doc.meta.default_print_format or "Standard"
	letter_head = doc.letter_head or None

	if "pdf_on_submit" not in frappe.get_installed_apps():
		return (print_format, letter_head)

	settings = frappe.get_single("PDF on Submit Settings")
	matched_config = get_matching_enabled_doctype(doc, settings)

	if matched_config:
		print_format = matched_config.print_format or print_format
		letter_head = matched_config.letter_head or letter_head

	return (print_format, letter_head)
