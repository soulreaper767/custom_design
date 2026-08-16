app_name = "custom_design"
app_title = "Custom Design"
app_publisher = "Sibyl Technologies"
app_description = "No-code theme, branding, and navigation customization for ERPNext."
app_email = "hello@tijaratapp.com"
app_license = "MIT"

# Included on every Desk page load.
app_include_css = "/assets/custom_design/css/custom_design.css"
app_include_js = "/assets/custom_design/js/custom_design.js"

# Included on every website/portal page load (login included) - a
# separate hook from app_include_*, which never reaches these pages at
# all. login.js/login.css no-op on anything that isn't actually the login
# page (detected via Frappe's own .for-login wrapper class), so loading
# them site-wide for website pages is harmless. webshop.css is scoped the
# same way, by CSS selector rather than a JS guard - its rules only match
# elements that exist on webshop's own pages (#product-filters, .item-card,
# .product-container, etc.), so it's equally inert everywhere else.
web_include_css = ["/assets/custom_design/css/login.css", "/assets/custom_design/css/webshop.css"]
web_include_js = "/assets/custom_design/js/login.js"

# Injects Design Settings into frappe.boot.custom_design so the theme is
# available client-side immediately on first paint, with no extra API call.
boot_session = "custom_design.boot.boot_session"

# Creates the default Design Settings record (already brand-colored via the
# DocType's own field defaults) and seeds the default chart color palette.
after_install = "custom_design.install.after_install"
