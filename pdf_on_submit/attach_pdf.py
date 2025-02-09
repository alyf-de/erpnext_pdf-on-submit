# Copyright (c) 2019, Raffael Meyer and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.core.api.file import create_new_folder
from frappe.model.naming import _format_autoname
from frappe.realtime import publish_realtime
from frappe.translate import print_language
from frappe.utils.data import evaluate_filters
from frappe.utils.weasyprint import PrintFormatGenerator


def attach_pdf(doc, event=None):
	settings = frappe.get_single("PDF on Submit Settings")
	enabled_doctypes = settings.get("enabled_for", {"document_type": doc.doctype})

	if not enabled_doctypes:
		return

	for dt_settings in enabled_doctypes:
		process_enabled_doctype(doc, dt_settings, settings.create_pdf_in_background)


def process_enabled_doctype(doc, settings, in_background):
	if settings.filters:
		filters = json.loads(settings.filters)
		if filters:
			condition_met = evaluate_filters(doc, filters)
			if not condition_met:
				return

	auto_name = settings.auto_name
	print_format = (
		settings.print_format or doc.meta.default_print_format or "Standard"
	)
	letter_head = settings.letter_head or None
	fallback_language = (
		frappe.db.get_single_value("System Settings", "language") or "en"
	)
	args = {
		"doctype": doc.doctype,
		"name": doc.name,
		"title": doc.get_title() if doc.meta.title_field else None,
		"lang": getattr(doc, "language", fallback_language),
		"show_progress": not in_background,
		"auto_name": auto_name,
		"print_format": print_format,
		"letter_head": letter_head,
	}

	frappe.enqueue(
		method=execute,
		timeout=30,
		now=bool(
			not in_background
			or frappe.flags.in_test
			or frappe.conf.developer_mode
		),
		enqueue_after_commit=True,
		**args,
	)


def execute(
	doctype,
	name,
	title=None,
	lang=None,
	show_progress=True,
	auto_name=None,
	print_format=None,
	letter_head=None,
):
	"""
	Queue calls this method, when it's ready.

	1. Create necessary folders
	2. Get raw PDF data
	3. Save PDF file and attach it to the document
	"""

	def publish_progress(percent):
		publish_realtime(
			"progress",
			{"percent": percent, "title": _("Creating PDF ..."), "description": None},
			doctype=doctype,
			docname=name,
		)

	if show_progress:
		publish_progress(0)

	doctype_folder = create_folder(doctype, "Home")
	title_folder = create_folder(title, doctype_folder) if title else None
	target_folder = title_folder or doctype_folder

	if show_progress:
		publish_progress(33)

	with print_language(lang):
		if frappe.db.get_value("Print Format", print_format, "print_format_builder_beta"):
			doc = frappe.get_doc(doctype, name)
			pdf_data = PrintFormatGenerator(print_format, doc, letter_head).render_pdf()
		else:
			pdf_data = get_pdf_data(doctype, name, print_format, letter_head)

	if doctype == "Sales Invoice" and "eu_einvoice" in frappe.get_installed_apps():
		try:
			from eu_einvoice.european_e_invoice.custom.sales_invoice import attach_xml_to_pdf
			pdf_data = attach_xml_to_pdf(name, pdf_data)
		except Exception:
			msg = _("Failed to attach XML to PDF for Sales Invoice {0}").format(name)
			if show_progress:
				frappe.msgprint(msg, indicator="red", alert=True)
			frappe.log_error(title=msg, reference_doctype=doctype, reference_name=name)

	if show_progress:
		publish_progress(66)

	save_and_attach(pdf_data, doctype, name, target_folder, auto_name)

	if show_progress:
		publish_progress(100)


def create_folder(folder, parent):
	"""Make sure the folder exists and return it's name."""
	_folder = folder.replace("/", "-")
	new_folder_name = "/".join([parent, _folder])

	if not frappe.db.exists("File", new_folder_name):
		create_new_folder(_folder, parent)

	return new_folder_name


def get_pdf_data(doctype, name, print_format: None, letterhead: None):
	"""Document -> HTML -> PDF."""
	html = frappe.get_print(doctype, name, print_format, letterhead=letterhead)
	return frappe.utils.pdf.get_pdf(html)


def save_and_attach(content, to_doctype, to_name, folder, auto_name=None):
	"""
	Save content to disk and create a File document.

	File document is linked to another document.
	"""
	if auto_name:
		doc = frappe.get_doc(to_doctype, to_name)
		# based on type of format used set_name_form_naming_option return result.
		pdf_name = set_name_from_naming_options(auto_name, doc)
		file_name = "{pdf_name}.pdf".format(pdf_name=pdf_name.replace("/", "-"))
	else:
		file_name = "{to_name}.pdf".format(to_name=to_name.replace("/", "-"))

	file = frappe.new_doc("File")
	file.file_name = file_name
	file.content = content
	file.folder = folder
	file.is_private = 1
	file.attached_to_doctype = to_doctype
	file.attached_to_name = to_name
	file.save()


def set_name_from_naming_options(autoname, doc):
	"""
	Get a name based on the autoname field option
	"""
	_autoname = autoname.lower()

	if _autoname.startswith("format:"):
		return _format_autoname(autoname, doc)

	return doc.name
