import frappe
from frappe import _
from frappe.utils import cint
from pdf_on_submit.attach_pdf import iter_matching_enabled_doctypes


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
def get_print_details(doctype: str, docname: str) -> list[dict]:
	"""
	Get print format / letter head combinations for a document based on
	PDF on Submit Settings. Returns one entry per matching enabled_doctype row,
	in table order. Falls back to a single default entry when no row matches.
	"""
	if not frappe.db.exists("DocType", doctype) or not frappe.has_permission(doctype, "print", docname):
		frappe.throw(_("No permission to print this document"))

	doc = frappe.get_doc(doctype, docname)
	default_print_format = doc.meta.default_print_format or "Standard"
	default_letter_head = getattr(doc, "letter_head", None) or None

	results = [
		{
			"print_format": row.print_format or default_print_format,
			"letter_head": row.letter_head or default_letter_head,
		}
		for row in iter_matching_enabled_doctypes(doc)
	]

	if not results:
		results.append({"print_format": default_print_format, "letter_head": default_letter_head})

	return results
