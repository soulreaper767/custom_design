import frappe

from custom_design.branding import sync_brand_translations


def execute():
	"""BRAND_REPLACEMENTS now maps "ERPNext"-origin strings to plain
	Application Name (e.g. "Tijarat") and "Frappe"-origin strings to that
	name + "OS" (e.g. "TijaratOS") instead of both sharing one target -
	existing Translation rows from before this split still hold the old,
	single-target text and need re-upserting to the new values."""
	try:
		if not frappe.db.exists("DocType", "Design Settings"):
			return

		sync_brand_translations()
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="custom_design: resync_platform_vs_product_branding patch failed")
