import frappe

from custom_design.branding import seed_default_sidebar_override, sync_brand_translations


def after_install():
	"""Runs once, right after the app is installed on a site. Design
	Settings' own field defaults already carry the brand colors (matching
	the frontend), so the rest of this just seeds the two things that
	can't carry JSON defaults the way simple fields can: the chart color
	palette (a Table field) and one starter sidebar link override."""
	settings = frappe.get_single("Design Settings")

	if not settings.chart_colors:
		# Same 500-weight swatches the frontend uses for its primary/success/
		# warning/danger/info scales (src/index.css) - keeps dashboard charts
		# on the same palette as the rest of the product.
		default_palette = [
			("#6366F1", "Primary"),
			("#10B981", "Success"),
			("#F59E0B", "Warning"),
			("#EF4444", "Danger"),
			("#0EA5E9", "Info"),
		]
		for color, label in default_palette:
			settings.append("chart_colors", {"color": color, "label": label})

	seed_default_sidebar_override(settings)

	settings.enabled = 1
	settings.save(ignore_permissions=True)

	sync_brand_translations(settings.app_title)

	frappe.db.commit()
