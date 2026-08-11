from custom_design.branding import sync_brand_translations


def execute():
	"""Backfills brand-text translations for sites that installed
	custom_design before this feature existed. Fresh installs get the same
	call from after_install; this patch exists so `git pull` +
	`bench migrate` on an already-installed site picks it up too, without
	needing a reinstall."""
	sync_brand_translations()
