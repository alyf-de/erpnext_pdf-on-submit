// Shared PDF button utility for sales/purchase doctypes

window.pdf_on_submit = window.pdf_on_submit || {};

// Common doctypes with PDF button enabled by default
// To enable for other doctypes, add a Client Script:
//   frappe.ui.form.on("Your DocType", { refresh: pdf_on_submit.add_pdf_button });
pdf_on_submit.ALLOWED_DOCTYPES = [
	"Quotation",
	"Sales Order",
	"Sales Invoice",
	"Delivery Note",
	"Dunning",
	"Request for Quotation",
	"Supplier Quotation",
	"Purchase Order",
	"Purchase Invoice",
	"Purchase Receipt",
];

// Register handler for all allowed doctypes
$(document).on("app_ready", function () {
	pdf_on_submit.ALLOWED_DOCTYPES.forEach((doctype) => {
		frappe.ui.form.on(doctype, {
			refresh: pdf_on_submit.add_pdf_button,
		});
	});
});

pdf_on_submit.add_pdf_button = async function (frm) {
	// Don't show button for new/unsaved documents
	if (frm.is_new()) {
		return;
	}

	const show_button = await frappe.db.get_single_value("PDF on Submit Settings", "show_pdf_button");

	if (!show_button) {
		return;
	}

	frm.remove_custom_button(__("PDF"));

	frm.add_custom_button(__("PDF"), async () => {
		try {
			const response = await frappe.call({
				method: "pdf_on_submit.utils.get_print_details",
				args: {
					doctype: frm.doc.doctype,
					docname: frm.doc.name,
				},
			});

			const [print_format, letter_head] = response.message;

			const params = new URLSearchParams({
				doctype: frm.doc.doctype,
				name: frm.doc.name,
				format: print_format,
				no_letterhead: 0,
				letterhead: letter_head || "",
				...(frm.doc.language && { _lang: frm.doc.language }),
			}).toString();

			const url = frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" + params);

			window.open(url, "_blank");
		} catch (error) {
			console.error("PDF generation failed:", error);
			frappe.msgprint({
				title: __("Error"),
				indicator: "red",
				message: __("Failed to generate PDF. {0}", [
					error.message || "Please check your permissions and try again.",
				]),
			});
		}
	});
};
