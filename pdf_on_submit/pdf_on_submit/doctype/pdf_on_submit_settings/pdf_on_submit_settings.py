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

		self.validate_attach_to_fields()

	def validate_attach_to_fields(self):
		"""
		Validates:
		1) attach_to_field is not processed multiple times in one document
		2) that the `attach_to_field` is a valid field in the DocType.
		Note: The 2nd validation would be more robust (but less performant), if done for each transaction.
		"""
		attach_to_fields = [
			(enabled_doctype.document_type, enabled_doctype.attach_to_field) for enabled_doctype in self.enabled_for
			if enabled_doctype.attach_to_field
		]
		if attach_to_fields:
			_check_for_duplicate_fieldnames(attach_to_fields)
			_check_if_attach_to_fields_are_valid(attach_to_fields)


def _check_for_duplicate_fieldnames(attach_to_fields):
	"""Ensure only one PDF file will be attached to a specific field."""
	seen_fields = set()
	for pair in attach_to_fields:
		if pair in seen_fields:
			frappe.throw(
				_("It is not allowed to set the attach field {0} in the DocType {1} multiple times.").format(pair[1], pair[0])
			)
		seen_fields.add(pair)


def _check_if_attach_to_fields_are_valid(attach_to_fields):
	for doctype, fieldname in attach_to_fields:
		meta = frappe.get_meta(doctype)
		if not meta.get("fields", {"fieldtype": "Attach", "fieldname": fieldname}):
			frappe.throw(
				_("{0} is not a valid field for DocType {1}.").format(fieldname, _(doctype))
			)
