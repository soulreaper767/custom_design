import frappe


def execute():
	"""Theme Mode dropped "User Choice (Light Default)" / "User Choice
	(Dark Default)" down to a plain "Light"/"Dark" choice - one mode for
	the whole system, always enforced through frappe.ui.set_theme(),
	instead of an in-between option that left Frappe's own toggle alone
	and this app's colors misapplying depending on whatever a given
	session's dark/light state happened to be. An existing site's stored
	value needs converting to a value the new two-option Select actually
	recognizes."""
	try:
		if not frappe.db.exists("DocType", "Design Settings"):
			return

		settings = frappe.get_single("Design Settings")
		current = settings.get("color_scheme_mode")

		if current == "User Choice (Dark Default)":
			settings.color_scheme_mode = "Dark"
		elif current not in ("Light", "Dark"):
			settings.color_scheme_mode = "Light"
		else:
			return  # already a valid value, nothing to do

		settings.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="custom_design: migrate_color_scheme_mode patch failed")
