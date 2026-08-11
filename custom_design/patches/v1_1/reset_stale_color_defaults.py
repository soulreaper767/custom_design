import frappe

# (field, old_default, new_default) - covers the v1 -> v2 palette overhaul
# (ink/brass/parchment -> the frontend's actual indigo/slate tokens).
# Updating the DocType JSON's own "default" only affects brand-new
# installs; a site installed before that change has the old value
# permanently saved in its Design Settings row, which is why light mode
# kept showing the old palette (and old/new fields ended up mismatched,
# e.g. an old accent_color paired against new badge logic) even after
# pulling the update and migrating. This backfills already-installed
# sites once. Only overwrites a field if it's still exactly the old
# shipped default (or empty) - if an admin deliberately customized it,
# including to something that happens to collide with the check some
# other way, this leaves it alone.
COLOR_RESETS = [
	("primary_color", "#16324F", "#4F46E5"),
	("accent_color", "#C68A2E", "#4338CA"),
	("background_color", "#F6F1E7", "#F8FAFC"),
	("text_color", "#23201B", "#0F172A"),
	("success_color", "#3E7A5A", "#047857"),
	("danger_color", "#B84A3E", "#B91C1C"),
	("dark_background_color", "#0D1E30", "#020617"),
	("dark_text_color", "#F6F1E7", "#F1F5F9"),
	("sidebar_background_color", "#16324F", "#FFFFFF"),
	("sidebar_text_color", "#F6F1E7", "#475569"),
	("sidebar_active_color", "#C68A2E", "#EEF2FF"),
	("navbar_background_color", "#16324F", "#FFFFFF"),
	("navbar_text_color", "#F6F1E7", "#0F172A"),
	("number_card_background", "#FBF3E4", "#FFFFFF"),
]

# Brand new fields as of the same change - no "old" value to detect against,
# just fill them in if the column exists (post-migrate) but is still blank
# (a brand new column on an existing Single row has no stored value, and
# migrate doesn't auto-populate JSON defaults for those).
NEW_FIELD_DEFAULTS = [
	("dark_primary_color", "#6366F1"),
	("dark_accent_color", "#A5B4FC"),
	("dark_success_color", "#10B981"),
	("dark_danger_color", "#EF4444"),
	("dark_sidebar_background_color", "#0F172A"),
	("dark_sidebar_text_color", "#CBD5E1"),
	("dark_navbar_background_color", "#0F172A"),
	("dark_navbar_text_color", "#F1F5F9"),
	("dark_number_card_background", "#0F172A"),
]

BORDER_RADIUS_RESET = ("border_radius", "Subtle (4px)", "Rounded (8px)")


def execute():
	# Defensive on purpose - a patch that raises halts `bench migrate` for
	# the whole site, which is worse than boot_session's failure mode.
	try:
		if not frappe.db.exists("DocType", "Design Settings"):
			return

		settings = frappe.get_single("Design Settings")
		changed = False

		for fieldname, old_default, new_default in COLOR_RESETS:
			current = (settings.get(fieldname) or "").strip()
			if not current or current.upper() == old_default.upper():
				settings.set(fieldname, new_default)
				changed = True

		for fieldname, new_default in NEW_FIELD_DEFAULTS:
			if not (settings.get(fieldname) or "").strip():
				settings.set(fieldname, new_default)
				changed = True

		field, old_default, new_default = BORDER_RADIUS_RESET
		if settings.get(field) == old_default:
			settings.set(field, new_default)
			changed = True

		if changed:
			settings.save(ignore_permissions=True)
			frappe.db.commit()
	except Exception:
		frappe.log_error(title="custom_design: reset_stale_color_defaults patch failed")
