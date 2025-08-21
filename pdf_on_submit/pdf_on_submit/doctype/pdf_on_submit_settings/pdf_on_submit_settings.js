// Copyright (c) 2019, Raffael Meyer and contributors
// For license information, please see license.txt

frappe.ui.form.on("PDF on Submit Settings", {
	refresh(frm) {
		frm.set_query("print_format", "enabled_for", function (doc, cdt, cdn) {
			return {
				filters: {
					doc_type: locals[cdt][cdn].document_type,
				},
			};
		});

		frm.set_query("document_type", "enabled_for", function (doc, cdt, cdn) {
			return {
				filters: {
					is_submittable: 1,
				},
			};
		});

		frm.doc.enabled_for.forEach((row) => {
			set_attach_to_field_options(frm, row.doctype, row.name);
		});
	},
	enabled_for_on_form_rendered(frm) {
		const row = frm.cur_grid.doc;
		const parent = frm.cur_grid.wrapper.find("[data-fieldname='filter_area']");
		parent.empty();

		if (!row.document_type) {
			return;
		}

		const filters = row.filters && row.filters !== "[]" ? JSON.parse(row.filters) : [];

		frappe.model.with_doctype(row.document_type, () => {
			const filter_group = new frappe.ui.FilterGroup({
				parent: parent,
				doctype: row.document_type,
				on_change: () => {
					frappe.model.set_value(
						row.doctype,
						row.name,
						"filters",
						JSON.stringify(filter_group.get_filters())
					);
				},
			});

			filter_group.add_filters_to_filter_group(filters);
		});
	},
});

frappe.ui.form.on("Enabled DocType", {
	document_type(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(row.doctype, row.name, "filters", "[]");
		frappe.model.set_value(row.doctype, row.name, "attach_to_field", "");

		if (row.print_format) {
			// Check if the print format is valid for the document type
			// If not, set the print format to an empty string
			frappe.db.get_value("Print Format", row.print_format, "doc_type").then((r) => {
				if (r.message.doc_type !== row.document_type) {
					frappe.model.set_value(row.doctype, row.name, "print_format", "");
				}
			});
		}

		if (frm.cur_grid) {
			frm.events.enabled_for_on_form_rendered(frm);
		}

		set_attach_to_field_options(frm, cdt, cdn);
	},
});


function set_attach_to_field_options(frm, cdt, cdn) {
	const doc = frappe.get_doc(cdt, cdn);
	const document_type = doc.document_type;
	const grid = frm.fields_dict.enabled_for.grid;

	if (!document_type) {
		set_field_options(grid, cdn, "attach_to_field", [""]);
		return;
	}

	// set options for `attach_to_field`
	frappe.model.with_doctype(document_type, () => {
		const meta = frappe.get_meta(document_type);
		const fields = [
			"",
			...meta.fields
				.filter(
					(field) =>
						field.fieldtype === "Attach" &&
						field.is_virtual === 0 &&
						field.read_only === 1 &&
						field.no_copy === 1
				)
				.map((field) => {
					return {
						value: field.fieldname,
						label: __(field.label),
					};
				})
				.sort((a, b) => a.label.localeCompare(b.label)),
		];

		set_field_options(grid, cdn, "attach_to_field", fields);
		grid.debounced_refresh();
	});
}

/**
 * Set the options for a field in a specific grid row
 * @param {frappe.ui.form.Grid} grid - frm.fields_dict.[child_table_name].grid
 * @param {string} row_name - The name of the grid row
 * @param {string} fieldname - The fieldname to set the options for
 * @param {any[]} options - The options to set for the field
 */
function set_field_options(grid, row_name, fieldname, options) {
	for (const row of grid.grid_rows) {
		if (row.doc.name !== row_name) {
			continue;
		}

		let docfield = row?.docfields?.find((d) => d.fieldname === fieldname);
		if (docfield) {
			docfield.options = options;
		} else {
			throw `field ${fieldname} not found`;
		}
	}
}
