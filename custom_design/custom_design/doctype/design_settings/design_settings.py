import frappe
from frappe.model.document import Document

from custom_design.branding import sync_brand_translations


class DesignSettings(Document):
	def on_update(self):
		# Boot session data is cached per session; clearing the website/desk
		# cache here means the very next page load anywhere picks up changes
		# without requiring a bench restart.
		frappe.clear_cache()

		# Re-applies (or, if Enable Custom Design was just turned off,
		# reverts) the Frappe/ERPNext -> Application Name text substitution.
		# No separate "sync" button - saving after changing Application Name
		# or the enable switch is the trigger, same as every other field.
		sync_brand_translations(self.app_title)
