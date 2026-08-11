import frappe

from custom_design.branding import seed_default_sidebar_override


def execute():
	"""Backfills the starter "Frappe HR" -> "<Application Name> Teams"
	sidebar override for sites that installed custom_design before this
	existed - same as after_install does for fresh installs. Only fires
	if the Sidebar Link Overrides table is still empty, so an admin's own
	overrides are never touched."""
	try:
		if not frappe.db.exists("DocType", "Design Settings"):
			return

		settings = frappe.get_single("Design Settings")
		if seed_default_sidebar_override(settings):
			settings.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception:
		frappe.log_error(title="custom_design: seed_default_sidebar_override patch failed")
