// custom_design: applies Design Settings across the whole Desk.
// Three-layer approach:
//   1. CSS custom properties (--cd-*) are set here and consumed by
//      custom_design.css and, where names are known, Frappe's own
//      theme variables are remapped too so native components pick it up.
//   2. Sidebar/menu label-text overrides are DOM-level, re-applied on every
//      mutation, since v16's sidebar re-renders dynamically and a one-time
//      patch would get silently wiped out on the next render.
//   3. Frappe/ERPNext -> Application Name text substitution: mostly
//      server-side via Translation records (custom_design.branding), with
//      a narrowly-scoped DOM pass here (applyBrandText) as a safety net
//      for the handful of chrome elements that aren't routed through
//      Frappe's own __() translation layer, e.g. the "Powered by Frappe"
//      footer link.

(function () {
	function setVar(root, name, value) {
		if (value) root.style.setProperty(name, value);
	}

	const FONT_STACKS = {
		Inter: "'Inter', sans-serif",
		"Noto Sans": "'Noto Sans', sans-serif",
		Roboto: "'Roboto', sans-serif",
		"Open Sans": "'Open Sans', sans-serif",
		"System UI": "system-ui, sans-serif",
	};

	const RADIUS_MAP = {
		"Sharp (0px)": "0px",
		"Subtle (4px)": "4px",
		"Rounded (8px)": "8px",
		"Pill (999px)": "999px",
	};

	function injectStyleTag(id, css) {
		let tag = document.getElementById(id);
		if (!tag) {
			tag = document.createElement("style");
			tag.id = id;
			document.head.appendChild(tag);
		}
		tag.textContent = css || "";
	}

	function toggleVisibility(selector, hide) {
		document.querySelectorAll(selector).forEach((el) => {
			el.style.display = hide ? "none" : "";
		});
	}

	// Frappe marks dark mode with a data-theme="dark"/"light" attribute on
	// <html> (set via frappe.ui.set_theme(), which also persists the choice
	// server-side) - not a "dark" CSS class. custom_design.css's dark-mode
	// rules key off that same attribute, so this needs to set it the real
	// way, not invent a class Frappe doesn't read. Skips the call if the
	// attribute already matches, so a "Forced Dark/Light" site doesn't fire
	// a server round-trip on every single page load once it's already set.
	function enforceColorScheme(mode) {
		const root = document.documentElement;
		if (root.getAttribute("data-theme") === mode) return;
		if (window.frappe && frappe.ui && typeof frappe.ui.set_theme === "function") {
			frappe.ui.set_theme(mode);
		} else {
			root.setAttribute("data-theme", mode);
		}
	}

	function replaceBrandWords(text, title) {
		return text.replace(/\bFrappe\b|\bERPNext\b/g, title);
	}

	function applyBrandText() {
		const title = window.custom_design && window.custom_design._appTitle;
		if (!title) return;

		document.title = replaceBrandWords(document.title, title);

		// Two tiers of scope, both safe because they're structurally chrome -
		// neither can ever contain arbitrary document/record data:
		//   1. A curated list of specific known branding elements (footer
		//      links, the "powered by" badge) - narrow and precise.
		//   2. Whole containers that are chrome by construction - the
		//      navbar's own dropdown menus (user menu, help menu, app
		//      switcher) and any currently-open modal (About dialog, etc.),
		//      walked in full since nothing in a menu or dialog is ever a
		//      customer/record's own data the way a list view or form is.
		// Never a document-wide walk of document.body itself - that's the
		// one thing that would risk rewriting a business record that
		// happens to contain the word "Frappe"/"ERPNext". Anything already
		// routed through Frappe's own __() translation layer is handled
		// server-side instead (see custom_design.branding).
		const chromeSelectors = [
			"a[href*='frappe.io']",
			"a[href*='frappecloud.com']",
			"a[href*='erpnext.com']",
			".frappe-powered-by",
		].join(", ");

		const chromeContainers = [
			".navbar .dropdown-menu",
			"#help-menu",
			".modal.show",
			".modal.in",
		].join(", ");

		const targets = new Set([
			...document.querySelectorAll(chromeSelectors),
			...document.querySelectorAll(chromeContainers),
		]);

		targets.forEach((el) => {
			["data-original-title", "title", "aria-label"].forEach((attr) => {
				const val = el.getAttribute(attr);
				if (val) el.setAttribute(attr, replaceBrandWords(val, title));
			});

			const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
			let node;
			while ((node = walker.nextNode())) {
				if (node.textContent.trim()) {
					node.textContent = replaceBrandWords(node.textContent, title);
				}
			}
		});
	}

	function applySidebarOverrides() {
		const overrides = (window.custom_design && window.custom_design._overrides) || [];
		const hiddenModules = (window.custom_design && window.custom_design._hiddenModules) || [];
		if (!overrides.length && !hiddenModules.length) return;

		const candidates = document.querySelectorAll(
			"a, .sidebar-item, .standard-sidebar-item, .dropdown-item, .workspace-sidebar-item, [data-label]"
		);

		candidates.forEach((el) => {
			const text = (el.textContent || "").trim();
			if (!text) return;

			const override = overrides.find((o) => o.match_label && o.match_label.trim() === text);
			if (override) {
				if (override.hide_item) {
					el.style.display = "none";
					return;
				}
				if (override.new_label) {
					const textNode = Array.prototype.slice
						.call(el.childNodes)
						.find((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim());
					if (textNode) textNode.textContent = override.new_label;
				}
				if (override.new_link && el.tagName === "A") {
					el.setAttribute("href", override.new_link);
					if (override.open_in_new_tab) el.setAttribute("target", "_blank");
				}
				if (override.new_icon) {
					el.setAttribute("data-cd-icon-override", override.new_icon);
				}
			}

			hiddenModules.forEach((mod) => {
				if (text === mod) el.style.display = "none";
			});
		});
	}

	let debounceTimer = null;
	function watchForRerenders() {
		const observer = new MutationObserver(() => {
			clearTimeout(debounceTimer);
			debounceTimer = setTimeout(() => {
				applySidebarOverrides();
				applyBrandText();
			}, 150);
		});
		observer.observe(document.body, { childList: true, subtree: true });
	}

	function applyTheme(settings) {
		const root = document.documentElement;

		if (!settings || Number(settings.enabled) === 0) {
			root.removeAttribute("data-cd-theme");
			injectStyleTag("custom-design-custom-css", "");
			window.custom_design._overrides = [];
			window.custom_design._hiddenModules = [];
			window.custom_design._appTitle = null;
			return;
		}

		setVar(root, "--cd-primary", settings.primary_color);
		setVar(root, "--cd-accent", settings.accent_color);
		setVar(root, "--cd-bg", settings.background_color);
		setVar(root, "--cd-text", settings.text_color);
		setVar(root, "--cd-success", settings.success_color);
		setVar(root, "--cd-danger", settings.danger_color);
		setVar(root, "--cd-dark-bg", settings.dark_background_color);
		setVar(root, "--cd-dark-text", settings.dark_text_color);
		setVar(root, "--cd-dark-primary", settings.dark_primary_color);
		setVar(root, "--cd-dark-accent", settings.dark_accent_color);
		setVar(root, "--cd-dark-success", settings.dark_success_color);
		setVar(root, "--cd-dark-danger", settings.dark_danger_color);
		setVar(root, "--cd-sidebar-bg", settings.sidebar_background_color);
		setVar(root, "--cd-sidebar-text", settings.sidebar_text_color);
		setVar(root, "--cd-sidebar-active", settings.sidebar_active_color);
		setVar(root, "--cd-navbar-bg", settings.navbar_background_color);
		setVar(root, "--cd-navbar-text", settings.navbar_text_color);
		setVar(root, "--cd-dark-sidebar-bg", settings.dark_sidebar_background_color);
		setVar(root, "--cd-dark-sidebar-text", settings.dark_sidebar_text_color);
		setVar(root, "--cd-dark-navbar-bg", settings.dark_navbar_background_color);
		setVar(root, "--cd-dark-navbar-text", settings.dark_navbar_text_color);
		setVar(root, "--cd-card-bg", settings.number_card_background);
		setVar(root, "--cd-dark-card-bg", settings.dark_number_card_background);

		// Frappe's own theme variables (--primary, --bg-color, etc.) are
		// remapped from the --cd-* values above, but that remap lives in
		// custom_design.css, not here - it needs to swap between the light
		// and dark field values whenever html's data-theme attribute
		// changes, and a CSS cascade rule reacts to that automatically
		// while a one-time inline style set here would not (this function
		// only re-runs on save/preview, not on every native dark-mode
		// toggle).

		if (settings.font_family && FONT_STACKS[settings.font_family]) {
			setVar(root, "--cd-font", FONT_STACKS[settings.font_family]);
		}
		if (settings.border_radius && RADIUS_MAP[settings.border_radius]) {
			setVar(root, "--cd-radius", RADIUS_MAP[settings.border_radius]);
		}

		root.setAttribute("data-cd-theme", "on");

		if (settings.color_scheme_mode === "Dark") {
			enforceColorScheme("dark");
		} else if (settings.color_scheme_mode === "Light") {
			enforceColorScheme("light");
		}
		// "User Choice" modes intentionally leave Frappe's own light/dark
		// toggle alone rather than forcing a mode.

		window.custom_design._appTitle = settings.app_title || null;
		applyBrandText();

		if (settings.logo) {
			document.querySelectorAll(".navbar-brand img, .app-logo img, img.app-logo").forEach((img) => {
				img.src = settings.logo;
			});
		}
		if (settings.favicon) {
			const link = document.querySelector("link[rel~='icon']");
			if (link) link.href = settings.favicon;
		}

		toggleVisibility(
			".navbar [data-original-title='Help'], #help-menu, .help-dropdown",
			!!settings.hide_help_menu
		);
		toggleVisibility(".navbar .notifications-icon, #notification-icon", !!settings.hide_notifications);

		injectStyleTag(
			"custom-design-hide-branding",
			settings.hide_frappe_branding
				? ".frappe-powered-by, a[href*='frappe.io']:not(.app-logo-link) { display: none !important; }"
				: ""
		);

		injectStyleTag("custom-design-custom-css", settings.custom_css || "");

		window.custom_design._overrides = settings.sidebar_overrides_list || settings.sidebar_overrides || [];
		window.custom_design._hiddenModules = settings.hidden_modules_list || settings.hidden_modules || [];
		applySidebarOverrides();

		if (settings.custom_js) {
			try {
				// eslint-disable-next-line no-new-func
				new Function(settings.custom_js)();
			} catch (e) {
				console.error("[custom_design] Error running Custom JS:", e);
			}
		}
	}

	window.custom_design = window.custom_design || {};
	window.custom_design.applyTheme = applyTheme;

	function boot() {
		const settings = (window.frappe && frappe.boot && frappe.boot.custom_design) || null;
		if (settings) applyTheme(settings);
		watchForRerenders();
	}

	if (window.frappe && frappe.ready) {
		frappe.ready(boot);
	} else {
		document.addEventListener("DOMContentLoaded", boot);
	}
})();
