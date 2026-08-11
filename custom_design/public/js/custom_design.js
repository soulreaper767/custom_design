// custom_design: applies Design Settings across the whole Desk.
// Two-layer approach:
//   1. CSS custom properties (--cd-*) are set here and consumed by
//      custom_design.css and, where names are known, Frappe's own
//      theme variables are remapped too so native components pick it up.
//   2. Sidebar/menu label-text overrides are DOM-level, re-applied on every
//      mutation, since v16's sidebar re-renders dynamically and a one-time
//      patch would get silently wiped out on the next render.

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
			debounceTimer = setTimeout(applySidebarOverrides, 150);
		});
		observer.observe(document.body, { childList: true, subtree: true });
	}

	function applyTheme(settings) {
		const root = document.documentElement;

		if (!settings || Number(settings.enabled) === 0) {
			root.removeAttribute("data-cd-theme");
			injectStyleTag("custom-design-custom-css", "");
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
		setVar(root, "--cd-sidebar-bg", settings.sidebar_background_color);
		setVar(root, "--cd-sidebar-text", settings.sidebar_text_color);
		setVar(root, "--cd-sidebar-active", settings.sidebar_active_color);
		setVar(root, "--cd-navbar-bg", settings.navbar_background_color);
		setVar(root, "--cd-navbar-text", settings.navbar_text_color);
		setVar(root, "--cd-card-bg", settings.number_card_background);

		// Best-effort remap of Frappe's own theme variables, where Frappe
		// already threads CSS custom properties through native components.
		// If a given Frappe release doesn't use one of these names, it's a
		// harmless no-op - the --cd-* variables above and the explicit
		// selectors in custom_design.css still carry the visual weight.
		setVar(root, "--primary", settings.primary_color);
		setVar(root, "--primary-color", settings.primary_color);
		setVar(root, "--dt-primary-color", settings.primary_color);
		setVar(root, "--bg-color", settings.background_color);
		setVar(root, "--text-color", settings.text_color);

		if (settings.font_family && FONT_STACKS[settings.font_family]) {
			setVar(root, "--cd-font", FONT_STACKS[settings.font_family]);
		}
		if (settings.border_radius && RADIUS_MAP[settings.border_radius]) {
			setVar(root, "--cd-radius", RADIUS_MAP[settings.border_radius]);
		}

		root.setAttribute("data-cd-theme", "on");

		if (settings.color_scheme_mode === "Dark") {
			root.classList.add("dark");
		} else if (settings.color_scheme_mode === "Light") {
			root.classList.remove("dark");
		}
		// "User Choice" modes intentionally leave Frappe's own light/dark
		// toggle alone rather than forcing a mode.

		if (settings.app_title) {
			try {
				document.title = document.title.replace(/Frappe|ERPNext/, settings.app_title);
			} catch (e) {
				/* non-fatal */
			}
		}

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
