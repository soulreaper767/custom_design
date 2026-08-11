app_name = "custom_design"
app_title = "Custom Design"
app_publisher = "Sibyl Technologies"
app_description = "No-code theme, branding, and navigation customization for ERPNext."
app_email = "hello@tijaratapp.com"
app_license = "MIT"

# Included on every Desk page load.
app_include_css = "/assets/custom_design/css/custom_design.css"
app_include_js = "/assets/custom_design/js/custom_design.js"

# Injects Design Settings into frappe.boot.custom_design so the theme is
# available client-side immediately on first paint, with no extra API call.
boot_session = "custom_design.boot.boot_session"

# Creates the default Design Settings record (already brand-colored via the
# DocType's own field defaults) and seeds the default chart color palette.
after_install = "custom_design.install.after_install"
