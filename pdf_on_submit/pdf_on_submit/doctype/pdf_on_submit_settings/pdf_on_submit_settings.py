# Copyright (c) 2019, Raffael Meyer and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.model.document import Document


class PDFonSubmitSettings(Document):
	def validate(self):
		for enabled_doctype in self.enabled_for:
			try:
				enabled_doctype.validate_filters()
			except Exception as e:
				frappe.clear_messages()
				frappe.throw(
					_("Row #{0}: invalid filters for <b>{1}</b>: {2}").format(
						enabled_doctype.idx, enabled_doctype.document_type, e
					)
				)
