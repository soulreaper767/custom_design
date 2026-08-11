import frappe


@frappe.whitelist(allow_guest=True)
def get_login_settings():
	"""Public/guest-allowed on purpose - the login page is unauthenticated,
	so login.js needs a way to fetch display config before any session
	exists. Only returns non-sensitive branding/display fields, never
	anything from an authenticated area of Design Settings (custom_css/
	custom_js, sidebar_overrides, hidden_modules, etc. are deliberately
	left out - those apply to the authenticated Desk only, via boot_session,
	and have no business being guest-readable)."""
	try:
		settings = frappe.get_cached_doc("Design Settings")
	except Exception:
		return {"enabled": 0}

	if not settings.enabled:
		return {"enabled": 0}

	return {
		"enabled": 1,
		"app_title": settings.app_title,
		"login_tagline": settings.login_tagline,
		"login_background": settings.login_background,
		"logo": settings.logo,
		"logo_dark": settings.logo_dark,
		"favicon": settings.favicon,
		"font_family": settings.font_family,
		"border_radius": settings.border_radius,
		"primary_color": settings.primary_color,
		"dark_primary_color": settings.dark_primary_color,
		"background_color": settings.background_color,
		"dark_background_color": settings.dark_background_color,
		"text_color": settings.text_color,
		"dark_text_color": settings.dark_text_color,
		"login_footer_html": settings.login_footer_html,
		"login_footer_size": settings.login_footer_size,
	}
