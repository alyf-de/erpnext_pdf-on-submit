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

def sales_invoice(doc, event=None):
    if frappe.get_single("PDF on Submit Settings").sales_invoice:
        execute("Sales Invoice", doc.name, doc.customer)

def delivery_note(doc, event=None):
    if frappe.get_single("PDF on Submit Settings").delivery_note:
        execute("Delivery Note", doc.name, doc.customer)

def quotation(doc, event=None):
    if frappe.get_single("PDF on Submit Settings").quotation:
        execute("Quotation", doc.name, doc.party_name)

def sales_order(doc, event=None):
    if frappe.get_single("PDF on Submit Settings").sales_order:
        execute("Sales Order", doc.name, doc.customer)

def execute(doctype, name, party):
    doctype_folder = create_folder(_(doctype), "Home")
    party_folder = create_folder(party, doctype_folder)
    pdf_data = get_pdf_data(doctype, name)
    save_and_attach(pdf_data, doctype, name, party_folder)

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
    save_file(file_name, content, to_doctype, to_name, folder=folder, is_private=1)

