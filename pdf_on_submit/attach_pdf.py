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
from frappe import publish_progress
from frappe.core.doctype.file.file import create_new_folder
from frappe.utils.file_manager import save_file
from frappe.model.naming import _field_autoname, set_name_by_naming_series, _prompt_autoname, _format_autoname, make_autoname



def attach_pdf(doc, event=None):
    settings = frappe.get_single("PDF on Submit Settings")
    enabled, autoname = zip(*[(row.document_type, row.autoname) for row in settings.enabled_for])

    enabled = list(enabled)
    autoname = ''.join(map(str, autoname))

    if doc.doctype not in enabled:
        return

    fallback_language = frappe.db.get_single_value("System Settings", "language") or "en"
    args = {
        "doctype": doc.doctype,
        "name": doc.name,
        "title": doc.get_title(),
        "lang": getattr(doc, "language", fallback_language),
        "show_progress": not settings.create_pdf_in_background,
        "autoname": autoname
    }

    if settings.create_pdf_in_background:
        enqueue(args)
    else:
        execute(**args)


def enqueue(args):
    """Add method `execute` with given args to the queue."""
    frappe.enqueue(method=execute, queue='long',
                   timeout=30, is_async=True, **args)


def execute(doctype, name, title, lang=None, show_progress=True, autoname=None):
    """
    Queue calls this method, when it's ready.

    1. Create necessary folders
    2. Get raw PDF data
    3. Save PDF file and attach it to the document
    """
    progress = frappe._dict(title=_("Creating PDF ..."), percent=0, doctype=doctype, docname=name)

    if lang:
        frappe.local.lang = lang

    if show_progress:
        publish_progress(**progress)

    doctype_folder = create_folder(_(doctype), "Home")
    title_folder = create_folder(title, doctype_folder)

    if show_progress:
        progress.percent = 33
        publish_progress(**progress)

    pdf_data = get_pdf_data(doctype, name)

    if show_progress:
        progress.percent = 66
        publish_progress(**progress)

    save_and_attach(pdf_data, doctype, name, title_folder, autoname)

    if show_progress:
        progress.percent = 100
        publish_progress(**progress)


def create_folder(folder, parent):
    """Make sure the folder exists and return it's name."""
    new_folder_name = "/".join([parent, folder])
    
    if not frappe.db.exists("File", new_folder_name):
        create_new_folder(folder, parent)
    
    return new_folder_name


def get_pdf_data(doctype, name):
    """Document -> HTML -> PDF."""
    html = frappe.get_print(doctype, name)
    return frappe.utils.pdf.get_pdf(html)


def save_and_attach(content, to_doctype, to_name, folder, autoname):
    """
    Save content to disk and create a File document.

    File document is linked to another document.
    """
    # fetch file auto name format from doctype.
    file_autoname = autoname

    doc = frappe.get_doc(to_doctype, to_name)

    if file_autoname:
        # based on type of format used set_name_form_naming_option return result.
        pdf_name = set_name_from_naming_options(file_autoname, doc)
        file_name = "{pdf_name}.pdf".format(pdf_name=pdf_name.replace(" ", "-").replace("/", "-"))
    else:
        file_name = "{}.pdf".format(to_name.replace(" ", "-").replace("/", "-"))

    save_file(file_name, content, to_doctype,
              to_name, folder=folder, is_private=1)

def set_name_from_naming_options(autoname, doc):
    """
    Get a name based on the autoname field option
    """

    _autoname = autoname.lower()

    if _autoname.startswith("field:"):
        name = _field_autoname(autoname, doc)
    elif _autoname.startswith("naming_series:"):
        set_name_by_naming_series(doc)
    elif _autoname.startswith("prompt"):
        _prompt_autoname(autoname, doc)
    elif _autoname.startswith("format:"):
        name = _format_autoname(autoname, doc)
    elif "#" in autoname:
        name = make_autoname(autoname, doc=doc)
    return name
