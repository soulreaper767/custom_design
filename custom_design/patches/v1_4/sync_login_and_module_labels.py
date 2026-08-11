import frappe

from custom_design.branding import sync_brand_translations


def execute():
	"""Backfills the login page / app-module-label features for sites that
	installed custom_design before they existed. Two things need doing:

	1. disable_email_link_login is a brand new field (default "1"), and
	   like every other field added after a site's first install, that
	   default only applies to brand-new installs - an existing site's row
	   has no value at all for it until explicitly set here. A falsy read
	   is unambiguous in this one-time-patch context specifically: the
	   field/checkbox didn't exist in anyone's form before this exact
	   update landed, so nobody could have deliberately set it to 0 yet -
	   falsy can only mean "never touched."
	2. sync_brand_translations() itself gained new behavior (module label
	   overrides, the login_with_email_link System Settings sync) that a
	   site which already ran the v1_0 patch won't pick up just because
	   the function changed - patches only run once, so this calls it
	   again."""
	try:
		if not frappe.db.exists("DocType", "Design Settings"):
			return

		settings = frappe.get_single("Design Settings")
		if not settings.get("disable_email_link_login"):
			settings.disable_email_link_login = 1
			settings.save(ignore_permissions=True)
			frappe.db.commit()

		sync_brand_translations()
	except Exception:
		frappe.log_error(title="custom_design: sync_login_and_module_labels patch failed")
