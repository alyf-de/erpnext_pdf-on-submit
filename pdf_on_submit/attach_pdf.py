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

def attach_pdf(doc, event=None):
    args = {
        "doctype": doc.doctype,
        "name": doc.name,
        "party": getattr(doc, "customer", _("Unknown")),
        "lang": getattr(doc, "language", "en")
    }

    if doc.doctype == "Quotation":
        args["party"] = doc.party_name

    if doc.doctype == "Dunning":
        party = frappe.get_value("Sales Invoice", doc.sales_invoice, "customer")
        lang = frappe.get_value("Sales Invoice", doc.sales_invoice, "language")
        args["party"] = party
        args["lang"] = lang

    settings = frappe.get_single("PDF on Submit Settings")
    slug = "_".join(doc.doctype.lower().split(" ")) # "Sales Invoice" -> "sales_invoice"

    if settings.get(slug):
        if settings.create_pdf_in_background:
            enqueue(args)
        else:
            execute(**args)


def enqueue(args):
    """Add method `execute` with given args to the queue."""
    frappe.enqueue(method=execute, queue='long',
                   timeout=30, is_async=True, **args)


def execute(doctype, name, party, lang=None):
    """
    Queue calls this method, when it's ready.

    1. Create necessary folders
    2. Get raw PDF data
    3. Save PDF file and attach it to the document
    """
    settings = frappe.get_single("PDF on Submit Settings")
    show_progress = True if settings.create_pdf_in_background is "0" else False
    doc = {"doctype": doctype, "docname": name}

    if lang:
        frappe.local.lang = lang

    if show_progress:
        frappe.publish_progress(percent=0, title=_("Creating Folders ..."), **doc)
    
    doctype_folder = create_folder(_(doctype), "Home")
    party_folder = create_folder(party, doctype_folder)

    if show_progress:
        frappe.publish_progress(percent=33, title=_("Creating PDF ..."), **doc)
    
    pdf_data = get_pdf_data(doctype, name)
    
    if show_progress:
        frappe.publish_progress(percent=66, title=_("Saving PDF ..."), **doc)
    
    save_and_attach(pdf_data, doctype, name, party_folder)
    
    if show_progress:
        frappe.publish_progress(percent=100, title=_("Done"), **doc)


def create_folder(folder, parent):
    """Make sure the folder exists and return it's name."""
    from frappe.core.doctype.file.file import create_new_folder
    try:
        create_new_folder(folder, parent)
    except frappe.DuplicateEntryError:
        pass

    return "/".join([parent, folder])


def get_pdf_data(doctype, name):
    """Document -> HTML -> PDF."""
    html = frappe.get_print(doctype, name)
    return frappe.utils.pdf.get_pdf(html)


def save_and_attach(content, to_doctype, to_name, folder):
    """
    Save content to disk and create a File document.

    File document is linked to another document.
    """
    from frappe.utils.file_manager import save_file
    file_name = "{}.pdf".format(to_name.replace(" ", "-").replace("/", "-"))
    save_file(file_name, content, to_doctype,
              to_name, folder=folder, is_private=1)
