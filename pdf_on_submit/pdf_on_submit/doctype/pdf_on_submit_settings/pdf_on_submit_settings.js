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
	},
	enabled_for_on_form_rendered(frm, dt, a, b, c) {
		const row = frm.cur_grid.doc;
		const filters = row.filters ? JSON.parse(row.filters) : [];

		frappe.model.with_doctype(row.document_type, () => {
			const filter_group = new frappe.ui.FilterGroup({
				parent: frm.cur_grid.wrapper.find("[data-fieldname='filter_area']"),
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
