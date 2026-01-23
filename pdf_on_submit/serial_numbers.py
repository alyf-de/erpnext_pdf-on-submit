from typing import TYPE_CHECKING

import frappe

if TYPE_CHECKING:
	from frappe.model.document import Document


def get_serial_numbers(row: "Document") -> list[str]:
	"""Return a list of serial numbers for a transaction row.

	Row is expected to have either a `serial_no` or a `serial_and_batch_bundle` attribute.
	"""
	if getattr(row, "serial_no", None):
		return row.serial_no.split("\n")
	elif getattr(row, "serial_and_batch_bundle", None):
		return frappe.get_all(
			"Serial and Batch Entry",
			filters={"parent": row.serial_and_batch_bundle, "parenttype": "Serial and Batch Bundle"},
			pluck="serial_no",
		)
	else:
		return []
