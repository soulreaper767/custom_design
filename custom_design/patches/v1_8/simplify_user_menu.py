import frappe

# The top-right user-avatar dropdown (not the "?" help menu, a separate
# icon) - hide everything except "View Website", which gets relabeled
# into the one surviving entry.
HIDE_LABELS = ["My Settings", "Toggle Theme", "Toggle Full Width", "Session Defaults", "Reload", "Log out"]
RELABEL = {"match_label": "View Website", "new_label": "Switch to Portal"}


def execute():
	try:
		if not frappe.db.exists("DocType", "Design Settings"):
			return

		settings = frappe.get_single("Design Settings")
		existing_labels = {row.match_label for row in settings.sidebar_overrides or []}
		changed = False

		for label in HIDE_LABELS:
			if label not in existing_labels:
				settings.append("sidebar_overrides", {"match_label": label, "hide_item": 1})
				changed = True

		if RELABEL["match_label"] not in existing_labels:
			settings.append("sidebar_overrides", dict(RELABEL))
			changed = True

		if changed:
			settings.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception:
		frappe.log_error(title="custom_design: simplify_user_menu patch failed")
