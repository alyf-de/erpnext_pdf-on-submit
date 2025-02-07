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
});

frappe.ui.form.on("Enabled DocType", {
	edit_filters(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const filters = row.filters ? JSON.parse(row.filters) : [];
		const container = {};
		const dialog = new frappe.ui.Dialog({
			title: __("Set Filters"),
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "filter_area",
				},
			],
			primary_action: function () {
				frappe.model.set_value(
					cdt,
					cdn,
					"filters",
					JSON.stringify(container.filter_group.get_filters(), null, 2)
				);
				dialog.hide(); // TODO: for some reason this also hides the child row
			},
			primary_action_label: "Set",
		});

		frappe.model.with_doctype(row.document_type, () => {
			container.filter_group = new frappe.ui.FilterGroup({
				parent: dialog.get_field("filter_area").$wrapper,
				doctype: row.document_type,
				on_change: () => {},
			});
			filters && container.filter_group.add_filters_to_filter_group(filters);

			dialog.show();
		});
	},
});
