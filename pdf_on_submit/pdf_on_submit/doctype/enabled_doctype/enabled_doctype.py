# Copyright (c) 2021, Raffael Meyer and contributors
# For license information, please see license.txt
import json

import frappe
from frappe.model.document import Document
from frappe.utils.data import evaluate_filters


class EnabledDocType(Document):
	def validate_filters(self):
		if not self.filters:
			return

		filters = json.loads(self.filters)
		dummy_doc = frappe.new_doc(self.document_type)
		evaluate_filters(dummy_doc, filters)
