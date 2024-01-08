"""
PDF on Submit. Creates a PDF when a document is submitted.
Copyright (C) 2019  Raffael Meyer <raffael@alyf.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import frappe
from frappe import _
from frappe.core.api.file import create_new_folder
from frappe.model.naming import _format_autoname
from frappe.realtime import publish_realtime
from frappe.utils.weasyprint import PrintFormatGenerator


def attach_pdf(doc, event=None):
	settings = frappe.get_single("PDF on Submit Settings")

	if enabled_doctypes := settings.get("enabled_for", {"document_type": doc.doctype}):
		enabled_doctype = enabled_doctypes[0]
	else:
		return

	auto_name = enabled_doctype.auto_name
	print_format = (
		enabled_doctype.print_format or doc.meta.default_print_format or "Standard"
	)
	letter_head = enabled_doctype.letter_head or None

	fallback_language = (
		frappe.db.get_single_value("System Settings", "language") or "en"
	)
	args = {
		"doctype": doc.doctype,
		"name": doc.name,
		"title": doc.get_title(),
		"lang": getattr(doc, "language", fallback_language),
		"show_progress": not settings.create_pdf_in_background,
		"auto_name": auto_name,
		"print_format": print_format,
		"letter_head": letter_head,
	}

	frappe.enqueue(
		method=execute,
		timeout=30,
		now=bool(
			not settings.create_pdf_in_background
			or frappe.flags.in_test
			or frappe.conf.developer_mode
		),
		**args,
	)


def execute(
	doctype,
	name,
	title,
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

	if lang:
		frappe.local.lang = lang
		# unset lang and jenv to load new language
		frappe.local.lang_full_dict = None
		frappe.local.jenv = None

	if show_progress:
		publish_progress(0)

	doctype_folder = create_folder(doctype, "Home")
	title_folder = create_folder(title, doctype_folder)

	if show_progress:
		publish_progress(33)

	if frappe.db.get_value("Print Format", print_format, "print_format_builder_beta"):
		doc = frappe.get_doc(doctype, name)
		pdf_data = PrintFormatGenerator(print_format, doc, letter_head).render_pdf()
	else:
		pdf_data = get_pdf_data(doctype, name, print_format, letter_head)

	if show_progress:
		publish_progress(66)

	save_and_attach(pdf_data, doctype, name, title_folder, auto_name)

	if show_progress:
		publish_progress(100)


def create_folder(folder, parent):
	"""Make sure the folder exists and return it's name."""
	new_folder_name = "/".join([parent, folder])

	if not frappe.db.exists("File", new_folder_name):
		create_new_folder(folder, parent)

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
