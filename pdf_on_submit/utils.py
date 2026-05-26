import frappe
from frappe import _
from frappe.utils import cint
from pdf_on_submit.attach_pdf import get_matching_enabled_doctype


def extend_boot_info(bootinfo):
	try:
		settings = frappe.get_single("PDF on Submit Settings")
	except frappe.PermissionError:
		return

	show_pdf_button = cint(settings.show_pdf_button)
	bootinfo.pdf_on_submit = frappe._dict(
		{
			"show_pdf_button": show_pdf_button,
			"enabled_doctypes": [row.document_type for row in settings.enabled_for if row.document_type]
			if show_pdf_button
			else [],
		}
	)


@frappe.whitelist(methods=["POST"])
def get_print_details(doctype: str, docname: str) -> tuple[str, str | None]:
	"""
	Get print format and letter head for a document based on PDF on Submit Settings.

	Returns: (print_format, letter_head)
	"""
	if not frappe.db.exists("DocType", doctype) or not frappe.has_permission(doctype, "print", docname):
		frappe.throw(_("No permission to print this document"))

	doc = frappe.get_doc(doctype, docname)
	print_format = doc.meta.default_print_format or "Standard"
	letter_head = getattr(doc, "letter_head", None) or None

	settings = frappe.get_single("PDF on Submit Settings")
	matched_config = get_matching_enabled_doctype(doc, settings)

	if matched_config:
		print_format = matched_config.print_format or print_format
		letter_head = matched_config.letter_head or letter_head

	return (print_format, letter_head)
