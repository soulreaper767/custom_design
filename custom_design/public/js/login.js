// custom_design: login page branding. Loaded on every website/portal page
// via web_include_js (app_include_js only reaches Desk - see README), so
// this only does anything once it confirms it's actually on the login
// page, via the presence of .for-login (Frappe's real wrapper class from
// frappe/www/login.html, not a pathname guess). Fetches its own config
// through a guest-allowed API call since there's no authenticated session
// yet to read frappe.boot.custom_design from the way the Desk-side script
// does.

(function () {
	function setVar(root, name, value) {
		if (value) root.style.setProperty(name, value);
	}

	const FOOTER_HEIGHTS = {
		"Compact (32px)": "32px",
		"Normal (48px)": "48px",
		"Spacious (64px)": "64px",
	};

	function applyLoginTheme(settings, forLogin) {
		if (!settings || Number(settings.enabled) === 0) return;

		document.body.classList.add("cd-login-active");
		const root = document.documentElement;

		setVar(root, "--cd-login-bg", settings.background_color);
		setVar(root, "--cd-login-text", settings.text_color);
		setVar(root, "--cd-login-primary", settings.primary_color);
		setVar(root, "--cd-login-card-bg", "#ffffff");
		setVar(root, "--cd-login-dark-bg", settings.dark_background_color);
		setVar(root, "--cd-login-dark-text", settings.dark_text_color);
		setVar(root, "--cd-login-dark-primary", settings.dark_primary_color);
		if (settings.border_radius) {
			const radiusMap = {
				"Sharp (0px)": "0px",
				"Subtle (4px)": "4px",
				"Rounded (8px)": "8px",
				"Pill (999px)": "999px",
			};
			setVar(root, "--cd-login-radius", radiusMap[settings.border_radius] || "8px");
		}

		if (settings.favicon) {
			const link = document.querySelector("link[rel~='icon']");
			if (link) link.href = settings.favicon;
		}

		if (settings.logo) {
			document.querySelectorAll(".app-logo, .app-logo img").forEach((img) => {
				if (img.tagName === "IMG") img.src = settings.logo;
			});
		}

		if (document.title) {
			document.title = document.title.replace(/Frappe|ERPNext/g, settings.app_title || document.title);
		}

		// Brand block: app title + tagline, injected just above the
		// existing "Sign In" heading rather than replacing it - that text
		// is a functional instruction (what this form does), not a brand
		// string, same reasoning applied to the About dialog's copyright
		// line in branding.py.
		if (settings.app_title && forLogin && !forLogin.querySelector(".cd-login-brand")) {
			const brand = document.createElement("div");
			brand.className = "cd-login-brand";
			const title = document.createElement("p");
			title.className = "cd-login-brand-title";
			title.textContent = settings.app_title;
			brand.appendChild(title);
			if (settings.login_tagline) {
				const tagline = document.createElement("p");
				tagline.className = "cd-login-brand-tagline";
				tagline.textContent = settings.login_tagline;
				brand.appendChild(tagline);
			}
			forLogin.insertBefore(brand, forLogin.firstChild);
		}

		if (settings.login_background) {
			forLogin.style.backgroundImage = `url("${settings.login_background}")`;
			forLogin.style.backgroundSize = "cover";
			forLogin.style.backgroundPosition = "center";
		}

		if (settings.login_footer_html && !document.querySelector(".cd-login-footer")) {
			const footer = document.createElement("footer");
			footer.className = "cd-login-footer";
			footer.style.minHeight = FOOTER_HEIGHTS[settings.login_footer_size] || "48px";
			footer.innerHTML = settings.login_footer_html;
			document.body.appendChild(footer);
		}
	}

	function boot() {
		const forLogin = document.querySelector(".for-login");
		if (!forLogin) return; // not the login page - nothing to do

		fetch("/api/method/custom_design.api.get_login_settings")
			.then((r) => (r.ok ? r.json() : null))
			.then((data) => {
				if (data && data.message) applyLoginTheme(data.message, forLogin);
			})
			.catch(() => {
				/* non-fatal - login page still fully works unstyled */
			});
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", boot);
	} else {
		boot();
	}
})();
