import frappe
from frappe import scrub
from frappe.utils import cint


def execute():
	"""
	Change PDF on Submit Settings from checkboxes for some doctypes to a list
	of enabled doctypes.
	"""
	frappe.reload_doc("pdf_on_submit", "doctype", "enabled_doctype")
	frappe.reload_doc("pdf_on_submit", "doctype", "pdf_on_submit_settings")

	settings = frappe.get_single("PDF on Submit Settings")
	for dt in ("Quotation", "Sales Order", "Sales Invoice", "Dunning", "Delivery Note"):
		if cint(settings.get(scrub(dt))):
			settings.append("enabled_for", {"document_type": dt})

	settings.save()
