import frappe

# The exact literal strings Frappe/ERPNext use for their own branding vary
# a little by version, and not all of them are routed through the same
# __() call Frappe's Translation records can target (see _sync_email_footer
# below for the one significant exception - outgoing email footers). This
# list is a mix of the stable ("Frappe", "ERPNext" alone) and a handful
# verified directly against frappe/frappe's source (the About dialog,
# frappe/public/js/frappe/ui/theme_switcher.js's sibling
# ui/toolbar/about.js) rather than guessed - "Open Source applications for
# the web." and "Frappe Framework Version" are both quoted verbatim from
# there. Anything a specific site's version phrases differently can be
# added the normal way, via Desk > Translation, without touching this app
# at all.
#
# Deliberately NOT included: the About dialog's copyright line ("Frappe
# Technologies Pvt. Ltd. and contributors"). That's a legal attribution
# naming who actually holds copyright on the underlying framework code,
# not a cosmetic brand string - rebranding it would misrepresent
# authorship, which is a different thing entirely from repainting "Powered
# by" chrome. Leave it alone even if extending this list later.
BRAND_REPLACEMENTS = {
	"Frappe": "{title}",
	"ERPNext": "{title}",
	"Frappe Framework": "{title}",
	"Frappe Technologies": "{title}",
	"Frappe Cloud": "{title}",
	"Frappe School": "{title} School",
	"Frappe Forum": "{title} Forum",
	"Frappe Support": "{title} Support",
	"Frappe Framework Version": "{title} Version",
	"About Frappe": "About {title}",
	"Powered by Frappe": "Powered by {title}",
	"Built on Frappe Framework": "Built on {title}",
	"Open Source applications for the web.": "{title}",
}


def sync_brand_translations(app_title=None):
	"""Creates/updates (or removes) `Translation` records so the words
	"Frappe"/"ERPNext" read as the custom app name wherever Frappe's own
	__() translation layer is used. Gated by Design Settings' own enable
	switch, so turning that off reverts this along with everything else -
	same "instant revert" contract the rest of the app already has.

	Runs from three places: after_install (fresh installs), the
	sync_brand_translations patch (sites that were already on an older
	version of this app before this feature existed), and
	DesignSettings.on_update (so editing Application Name or toggling
	Enable Custom Design and saving re-applies it immediately, without a
	separate button).

	Wrapped defensively at both call sites and internally - the two halves
	(Translation records, email footer) fail independently, since a
	System Settings field name mismatch on a given Frappe version
	shouldn't take down Translation syncing too, or vice versa."""
	settings = frappe.get_single("Design Settings")
	enabled = bool(settings.enabled)
	title = (app_title or settings.app_title or "").strip()

	if enabled and not title:
		enabled = False  # nothing sensible to substitute brand text with

	try:
		_sync_translations(enabled, title)
	except Exception:
		frappe.log_error(title="custom_design: brand translation sync failed")

	try:
		_sync_email_footer(enabled, title)
	except Exception:
		frappe.log_error(title="custom_design: email footer sync failed")

	try:
		_sync_module_labels(enabled, settings)
	except Exception:
		frappe.log_error(title="custom_design: module label sync failed")

	try:
		_sync_login_settings(enabled, settings)
	except Exception:
		frappe.log_error(title="custom_design: login settings sync failed")


def _sync_translations(enabled, title):
	languages = frappe.get_all("Language", filters={"enabled": 1}, pluck="name") or []
	if "en" not in languages:
		languages.append("en")

	for source, template in BRAND_REPLACEMENTS.items():
		translated = template.format(title=title) if enabled else None
		for lang in languages:
			existing = frappe.db.get_value(
				"Translation", {"source_text": source, "language": lang}, "name"
			)
			if enabled:
				if existing:
					frappe.db.set_value("Translation", existing, "translated_text", translated)
				else:
					frappe.get_doc(
						{
							"doctype": "Translation",
							"language": lang,
							"source_text": source,
							"translated_text": translated,
						}
					).insert(ignore_permissions=True)
			elif existing:
				frappe.delete_doc("Translation", existing, ignore_permissions=True, force=True)

	# frappe.clear_cache() (already called by DesignSettings.on_update /
	# after_install elsewhere in this app) busts the cached per-language
	# translation dict too, so a dedicated cache-clear call isn't needed
	# here specifically.


def _sync_module_labels(enabled, settings):
	"""Same exact-string Translation upsert as _sync_translations, driven
	by the admin-editable Module Label Overrides table instead of a fixed
	word list - lets an admin pick any installed app/module and relabel it
	globally (sidebar, app switcher, workspace list) without touching the
	module's actual name, since nothing about routing/permissions/reports
	depends on the *translated* label, only the real one.

	Doesn't track/clean up rows that were removed from the table between
	syncs (no stored "previous state" to diff against) - same limitation
	BRAND_REPLACEMENTS has when an entry is retired, documented there.
	Deleting the row's Translation record by hand via Desk > Translation
	fully reverts it if that ever matters."""
	languages = frappe.get_all("Language", filters={"enabled": 1}, pluck="name") or []
	if "en" not in languages:
		languages.append("en")

	for row in settings.module_label_overrides or []:
		if not row.module or not row.custom_label:
			continue
		for lang in languages:
			existing = frappe.db.get_value(
				"Translation", {"source_text": row.module, "language": lang}, "name"
			)
			if enabled:
				if existing:
					frappe.db.set_value("Translation", existing, "translated_text", row.custom_label)
				else:
					frappe.get_doc(
						{
							"doctype": "Translation",
							"language": lang,
							"source_text": row.module,
							"translated_text": row.custom_label,
						}
					).insert(ignore_permissions=True)
			elif existing:
				frappe.delete_doc("Translation", existing, ignore_permissions=True, force=True)


def _sync_login_settings(enabled, settings):
	"""Hides Frappe's passwordless "Login with Email Link" button through
	its own real System Settings field (login_with_email_link - confirmed
	against frappe/www/login.html, which gates that button on exactly this
	context variable), not CSS display:none. A direct on/off mapping, not
	a "only touch if unset" guard like the email footer - this field's
	entire job is controlling that one System Settings value, so there's
	no ambiguity about ownership the way there is for a freeform text
	field an admin might set for unrelated reasons."""
	system_settings = frappe.get_single("System Settings")
	should_disable = enabled and bool(settings.get("disable_email_link_login"))
	system_settings.login_with_email_link = 0 if should_disable else 1
	system_settings.save(ignore_permissions=True)


def seed_default_sidebar_override(settings=None, app_title=None):
	"""Adds one starter Sidebar Link Override - renaming "Frappe HR" to
	"<Application Name> Teams" - if the table is still empty. This is a
	helpful starting point, not a rule this app enforces: it's a normal,
	admin-editable/deletable row like any other, seeded once via
	after_install / the seed_default_sidebar_override patch, never
	re-applied afterwards (unlike the Translation sync, which is only
	safe to redo because it's an exact upsert - this would otherwise
	re-add itself after an admin deletes it). Silently does nothing if a
	site has no item with that exact visible label (e.g. no HRMS app
	installed) - the override matcher just never finds it.

	Returns True if a row was appended (caller decides when to save,
	since after_install already saves the same settings doc once for
	chart_colors too)."""
	settings = settings or frappe.get_single("Design Settings")
	if settings.sidebar_overrides:
		return False

	title = (app_title or settings.app_title or "").strip()
	if not title:
		return False

	settings.append("sidebar_overrides", {"match_label": "Frappe HR", "new_label": f"{title} Teams"})
	return True


def _sync_email_footer(enabled, title):
	"""Frappe appends its own "Powered by Frappe"-style footer to outgoing
	system emails unless disable_standard_email_footer is set - that
	footer text isn't a standalone __() source string this app can target
	via Translation records, so it's suppressed and replaced directly via
	System Settings instead. Only touches email_footer_address if it's
	empty or was previously set by this same function, so an admin's own
	custom footer is never clobbered."""
	our_marker = "Sent by "
	system_settings = frappe.get_single("System Settings")
	current_footer = system_settings.get("email_footer_address") or ""

	if enabled:
		system_settings.disable_standard_email_footer = 1
		if not current_footer or current_footer.startswith(our_marker):
			system_settings.email_footer_address = f"{our_marker}{title}"
	else:
		if current_footer.startswith(our_marker):
			system_settings.email_footer_address = ""
		system_settings.disable_standard_email_footer = 0

	system_settings.save(ignore_permissions=True)
