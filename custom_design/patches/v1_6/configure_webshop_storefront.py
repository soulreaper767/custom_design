import frappe


def execute():
	"""Turns on the storefront's actual e-commerce functionality - every
	toggle on Webshop Settings ships off by default (Enable Shopping Cart,
	Enable Checkout, Show Price, Show Stock Availability, sidebar filters),
	so /all-products and item pages render essentially empty/broken until
	someone flips them. Picks whatever Company/Price List/Customer Group
	already exist on the site rather than inventing new ones; if none can
	be resolved, the toggles are still turned on and a log entry flags that
	checkout needs those three fields filled in by hand."""
	try:
		if not frappe.db.exists("DocType", "Webshop Settings"):
			return

		settings = frappe.get_single("Webshop Settings")

		company = (
			settings.company
			or frappe.defaults.get_global_default("company")
			or frappe.db.get_value("Company", {}, "name")
		)
		price_list = settings.price_list or (
			"Standard Selling"
			if frappe.db.exists("Price List", "Standard Selling")
			else frappe.db.get_value("Price List", {"selling": 1}, "name")
		)
		customer_group = settings.default_customer_group or (
			"Retailer"
			if frappe.db.exists("Customer Group", "Retailer")
			else frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		)

		if company:
			settings.company = company
		if price_list:
			settings.price_list = price_list
		if customer_group:
			settings.default_customer_group = customer_group

		if not (company and price_list and customer_group):
			frappe.log_error(
				title="custom_design: Webshop Settings needs manual completion",
				message=(
					f"Resolved company={company}, price_list={price_list}, "
					f"customer_group={customer_group} - fill in whichever is blank "
					f"under Website > E Commerce Settings, or checkout won't work."
				),
			)

		settings.enabled = 1
		settings.enable_checkout = 1
		settings.enable_field_filters = 1
		settings.enable_attribute_filters = 1
		settings.show_price = 1
		settings.show_stock_availability = 1
		settings.enable_wishlist = 1
		settings.enable_recommendations = 1
		if not settings.products_per_page:
			settings.products_per_page = 12

		settings.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		frappe.log_error(title="custom_design: configure_webshop_storefront patch failed")
