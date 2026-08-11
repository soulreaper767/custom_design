import frappe


def boot_session(bootinfo):
	"""Runs on every session boot (page load). Attaches the current Design
	Settings to frappe.boot so the theme applies on first paint, without an
	extra round-trip API call from the client."""
	try:
		settings = frappe.get_cached_doc("Design Settings")
	except Exception:
		# DocType not migrated yet (e.g. mid-install) - fail safe, no theme.
		bootinfo.custom_design = {"enabled": 0}
		return

	if not settings.enabled:
		bootinfo.custom_design = {"enabled": 0}
		return

	bootinfo.custom_design = {
		"enabled": 1,
		"app_title": settings.app_title,
		"logo": settings.logo,
		"logo_dark": settings.logo_dark,
		"favicon": settings.favicon,
		"login_tagline": settings.login_tagline,
		"login_background": settings.login_background,
		"color_scheme_mode": settings.color_scheme_mode,
		"font_family": settings.font_family,
		"border_radius": settings.border_radius,
		"primary_color": settings.primary_color,
		"accent_color": settings.accent_color,
		"background_color": settings.background_color,
		"text_color": settings.text_color,
		"success_color": settings.success_color,
		"danger_color": settings.danger_color,
		"dark_background_color": settings.dark_background_color,
		"dark_text_color": settings.dark_text_color,
		"sidebar_background_color": settings.sidebar_background_color,
		"sidebar_text_color": settings.sidebar_text_color,
		"sidebar_active_color": settings.sidebar_active_color,
		"navbar_background_color": settings.navbar_background_color,
		"navbar_text_color": settings.navbar_text_color,
		"number_card_background": settings.number_card_background,
		"chart_colors_list": [d.color for d in settings.chart_colors],
		"hide_help_menu": settings.hide_help_menu,
		"hide_notifications": settings.hide_notifications,
		"hide_frappe_branding": settings.hide_frappe_branding,
		"hidden_modules_list": [d.module for d in settings.hidden_modules],
		"sidebar_overrides_list": [
			{
				"match_label": d.match_label,
				"new_label": d.new_label,
				"new_link": d.new_link,
				"new_icon": d.new_icon,
				"hide_item": d.hide_item,
				"open_in_new_tab": d.open_in_new_tab,
			}
			for d in settings.sidebar_overrides
		],
		"custom_css": settings.custom_css,
		"custom_js": settings.custom_js,
	}
