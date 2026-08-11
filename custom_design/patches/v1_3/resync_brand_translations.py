import frappe

from custom_design.branding import sync_brand_translations

# These were in an earlier version of BRAND_REPLACEMENTS but were guessed
# rather than verified against Frappe's actual source, and have since been
# replaced with the real strings ("Open Source applications for the web.",
# "Frappe Framework Version") pulled directly from frappe/frappe's About
# dialog source. They almost certainly never matched anything real (hence
# never visibly changed anything), but clean them up regardless so a site
# doesn't carry stale Translation rows for strings this app no longer
# tracks.
STALE_SOURCE_STRINGS = [
	"Open Source Applications for the Enterprise",
	"100% Open Source",
	"The world's #1 open source ERP",
]


def execute():
	try:
		if not frappe.db.exists("DocType", "Design Settings"):
			return

		for source in STALE_SOURCE_STRINGS:
			for name in frappe.get_all("Translation", filters={"source_text": source}, pluck="name"):
				frappe.delete_doc("Translation", name, ignore_permissions=True, force=True)

		sync_brand_translations()
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="custom_design: resync_brand_translations patch failed")
