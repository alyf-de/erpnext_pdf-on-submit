// Shared PDF button utility.
// Auto-registers for every doctype listed in PDF on Submit Settings > enabled_for
// when the global "Show PDF Button" toggle is on (loaded from boot info).

window.pdf_on_submit = window.pdf_on_submit || {};

$(document).on("app_ready", function () {
	const boot = frappe.boot.pdf_on_submit || {};
	if (!boot.show_pdf_button) return;

	(boot.enabled_doctypes || []).forEach((doctype) => {
		frappe.ui.form.on(doctype, {
			refresh: pdf_on_submit.add_pdf_button,
		});
	});
});

pdf_on_submit.build_pdf_url = function (frm, { print_format, letter_head }) {
	const params = new URLSearchParams({
		doctype: frm.doc.doctype,
		name: frm.doc.name,
		format: print_format,
		no_letterhead: 0,
		letterhead: letter_head || "",
		...(frm.doc.language && { _lang: frm.doc.language }),
	}).toString();
	return frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?" + params);
};

pdf_on_submit.add_pdf_button = async function (frm) {
	if (frm.is_new()) return;

	frm.remove_custom_button(__("PDF"));

	frm.add_custom_button(__("PDF"), async () => {
		// Open the popup synchronously while still in the user-gesture context,
		// before any await, to avoid browser popup blockers.
		const popup = window.open("", "_blank");
		if (!popup) {
			frappe.msgprint({
				title: __("Popup Blocked"),
				indicator: "orange",
				message: __("Please allow popups for this site and try again."),
			});
			return;
		}
		try {
			const matches = await frappe.xcall("pdf_on_submit.utils.get_print_details", {
				doctype: frm.doc.doctype,
				docname: frm.doc.name,
			});

			if (!matches || !matches.length) {
				popup.close();
				return;
			}

			const [first, ...rest] = matches;
			popup.location.href = pdf_on_submit.build_pdf_url(frm, first);

			if (rest.length) {
				const items = rest
					.map((m) => {
						const label = m.letter_head
							? `${frappe.utils.escape_html(m.print_format)} – ${frappe.utils.escape_html(m.letter_head)}`
							: frappe.utils.escape_html(m.print_format);
						const href = frappe.utils.escape_html(pdf_on_submit.build_pdf_url(frm, m));
						return `<li><a href="${href}" target="_blank" rel="noopener">${label}</a></li>`;
					})
					.join("");
				frappe.msgprint({
					title: __("Additional print formats"),
					indicator: "blue",
					message: __("More formats are configured for this document. Click to open:") + `<ul>${items}</ul>`,
				});
			}
		} catch (error) {
			popup.close();
			console.error("PDF generation failed:", error);
			frappe.msgprint({
				title: __("Error"),
				indicator: "red",
				message: __("Failed to generate PDF. {0}", [
					error.message || __("Please check your permissions and try again."),
				]),
			});
		}
	});
};
