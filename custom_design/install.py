import frappe


def after_install():
	"""Runs once, right after the app is installed on a site. Design
	Settings' own field defaults already carry the brand colors (matching
	the frontend), so the only thing left to seed programmatically is the
	chart color palette, since Table field rows can't carry JSON defaults
	the way simple fields can."""
	settings = frappe.get_single("Design Settings")

	if not settings.chart_colors:
		default_palette = [
			("#16324F", "Ink"),
			("#C68A2E", "Brass"),
			("#3E7A5A", "Verified Green"),
			("#6E93AC", "Ink Light"),
			("#B84A3E", "Alert"),
		]
		for color, label in default_palette:
			settings.append("chart_colors", {"color": color, "label": label})

	settings.enabled = 1
	settings.save(ignore_permissions=True)
	frappe.db.commit()
