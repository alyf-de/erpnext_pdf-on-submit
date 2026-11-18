# Copyright (c) 2019, Raffael Meyer and contributors
# For license information, please see license.txt
from collections import Counter

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

		self.validate_attach_to_fields()

	def validate_attach_to_fields(self):
		"""
		Validates:
		1) that the `attach_to_field` is a valid field in the DocType.
		2) warns if an `attach_to_field` is used in multiple rows. Their filters must be mutually exclusive,
		   otherwise submitting a matching document fails (see `attach_pdf`).
		Note: The 1st validation would be more robust (but less performant), if done for each transaction.
		"""
		attach_to_fields = [
			(enabled_doctype.document_type, enabled_doctype.attach_to_field)
			for enabled_doctype in self.enabled_for
			if enabled_doctype.attach_to_field
		]
		if attach_to_fields:
			_check_if_attach_to_fields_are_valid(attach_to_fields)
			_warn_about_duplicate_fieldnames(attach_to_fields)


def _warn_about_duplicate_fieldnames(attach_to_fields):
	for (doctype, fieldname), count in Counter(attach_to_fields).items():
		if count > 1:
			frappe.msgprint(
				_(
					"The attach field {0} is used in multiple rows for DocType {1}. Please make sure that the filters of these rows are mutually exclusive. Otherwise, submitting a document that matches more than one of these rows will fail."
				).format(_(frappe.get_meta(doctype).get_label(fieldname)), _(doctype)),
				title=_("Duplicate Attach Field"),
				indicator="orange",
			)


def _check_if_attach_to_fields_are_valid(attach_to_fields):
	for doctype, fieldname in attach_to_fields:
		meta = frappe.get_meta(doctype)
		if not meta.get("fields", {"fieldtype": "Attach", "fieldname": fieldname}):
			frappe.throw(_("{0} is not a valid field for DocType {1}.").format(fieldname, _(doctype)))
