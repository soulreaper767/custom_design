import frappe


def boot_session(bootinfo):
	"""Runs on every session boot (page load). Attaches the current Design
	Settings to frappe.boot so the theme applies on first paint, without an
	extra round-trip API call from the client.

	Everything below is defensive on purpose: this runs on EVERY page load
	for EVERY user, including the initial desk/login boot - an unhandled
	exception here doesn't just skip the theme, it takes down the whole
	site (frappe.SessionBootFailed). That's exactly what happened when a
	site's DocType schema was briefly behind this app's code (git pull
	landed before `bench migrate` ran, so a newly-added field like
	dark_primary_color didn't exist on the Design Settings doctype yet).
	getattr(..., None) on every field means a missing column degrades to
	"no value for that field" instead of crashing boot, and the whole
	block is additionally wrapped in try/except as a last resort so a
	failure mode nobody anticipated still fails safe rather than taking
	the Desk down."""
	try:
		settings = frappe.get_cached_doc("Design Settings")
		if not settings.enabled:
			bootinfo.custom_design = {"enabled": 0}
			return

		def field(name):
			return getattr(settings, name, None)

		bootinfo.custom_design = {
			"enabled": 1,
			"app_title": field("app_title"),
			"logo": field("logo"),
			"logo_dark": field("logo_dark"),
			"favicon": field("favicon"),
			"login_tagline": field("login_tagline"),
			"login_background": field("login_background"),
			"color_scheme_mode": field("color_scheme_mode"),
			"font_family": field("font_family"),
			"border_radius": field("border_radius"),
			"primary_color": field("primary_color"),
			"accent_color": field("accent_color"),
			"background_color": field("background_color"),
			"text_color": field("text_color"),
			"success_color": field("success_color"),
			"danger_color": field("danger_color"),
			"dark_background_color": field("dark_background_color"),
			"dark_text_color": field("dark_text_color"),
			"dark_primary_color": field("dark_primary_color"),
			"dark_accent_color": field("dark_accent_color"),
			"dark_success_color": field("dark_success_color"),
			"dark_danger_color": field("dark_danger_color"),
			"sidebar_background_color": field("sidebar_background_color"),
			"sidebar_text_color": field("sidebar_text_color"),
			"sidebar_active_color": field("sidebar_active_color"),
			"navbar_background_color": field("navbar_background_color"),
			"navbar_text_color": field("navbar_text_color"),
			"dark_sidebar_background_color": field("dark_sidebar_background_color"),
			"dark_sidebar_text_color": field("dark_sidebar_text_color"),
			"dark_navbar_background_color": field("dark_navbar_background_color"),
			"dark_navbar_text_color": field("dark_navbar_text_color"),
			"number_card_background": field("number_card_background"),
			"dark_number_card_background": field("dark_number_card_background"),
			"chart_colors_list": [d.color for d in (field("chart_colors") or [])],
			"hide_help_menu": field("hide_help_menu"),
			"hide_notifications": field("hide_notifications"),
			"hide_frappe_branding": field("hide_frappe_branding"),
			"hidden_modules_list": [d.module for d in (field("hidden_modules") or [])],
			"sidebar_overrides_list": [
				{
					"match_label": d.match_label,
					"new_label": d.new_label,
					"new_link": d.new_link,
					"new_icon": d.new_icon,
					"hide_item": d.hide_item,
					"open_in_new_tab": d.open_in_new_tab,
				}
				for d in (field("sidebar_overrides") or [])
			],
			"custom_css": field("custom_css"),
			"custom_js": field("custom_js"),
		}
	except Exception:
		# DocType not migrated yet, schema mismatch, or anything else
		# unanticipated - fail safe with no theme rather than break boot
		# for every user on the site.
		frappe.log_error(title="custom_design: boot_session failed")
		bootinfo.custom_design = {"enabled": 0}
