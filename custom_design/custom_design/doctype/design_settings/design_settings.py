import frappe
from frappe.model.document import Document


class DesignSettings(Document):
	def on_update(self):
		# Boot session data is cached per session; clearing the website/desk
		# cache here means the very next page load anywhere picks up changes
		# without requiring a bench restart.
		frappe.clear_cache()


def clear_cache_on_update(doc, method=None):
	frappe.clear_cache()
