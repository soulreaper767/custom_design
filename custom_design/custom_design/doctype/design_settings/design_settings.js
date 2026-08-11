frappe.ui.form.on("Design Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Apply Live Preview"), () => {
			if (!window.custom_design || !window.custom_design.applyTheme) {
				frappe.msgprint(__("Custom Design app assets have not loaded yet. Refresh the page and try again."));
				return;
			}
			// Preview uses the current unsaved form values, not what's saved in
			// the database yet - lets an admin see a change before committing.
			const preview = frm.doc;
			preview.chart_colors_list = (frm.doc.chart_colors || []).map((d) => d.color);
			preview.hidden_modules_list = (frm.doc.hidden_modules || []).map((d) => d.module);
			preview.sidebar_overrides_list = frm.doc.sidebar_overrides || [];
			window.custom_design.applyTheme(preview);
			frappe.show_alert({ message: __("Preview applied to this session. Save to make it permanent."), indicator: "blue" });
		});

		frm.dashboard.set_headline(
			__("Changes take effect immediately for the whole system after saving. Use \"Apply Live Preview\" to check a change first without saving.")
		);
	},

	after_save(frm) {
		// Re-apply from the now-saved doc so the admin's own session reflects
		// the change instantly, without waiting for a full boot reload.
		if (window.custom_design && window.custom_design.applyTheme) {
			const saved = frm.doc;
			saved.chart_colors_list = (frm.doc.chart_colors || []).map((d) => d.color);
			saved.hidden_modules_list = (frm.doc.hidden_modules || []).map((d) => d.module);
			saved.sidebar_overrides_list = frm.doc.sidebar_overrides || [];
			window.custom_design.applyTheme(saved);
		}
	},
});
