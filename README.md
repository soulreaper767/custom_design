# Custom Design

No-code theme, branding, and navigation customization for ERPNext — one
settings screen controls colors, fonts, corner roundness, sidebar/navbar
colors, dashboard chart colors, logo/favicon, and menu item overrides
(rename, relink, or hide any sidebar/menu item by matching its text).

Ships with defaults already matching the Tijarat frontend's actual design
tokens (`dev/frontend/src/index.css`: indigo primary, slate neutrals,
emerald/red/amber/sky semantic colors) so backend and frontend look
consistent from the moment it's installed — no configuration required to
get that baseline.

**Theme Mode is one setting for the whole system, not a per-user toggle.**
Pick **Light** or **Dark** at the top of Design Settings, and the form
below only shows the color fields for whichever you picked - the other
mode's fields are hidden entirely (via `depends_on`), so there's no way to
end up editing a dark-mode color while looking at a light-mode preview, or
vice versa. Every color pair was verified with real WCAG contrast math
(computed, not eyeballed) against its actual background before shipping -
worst case across all sixteen light/dark pairs is 4.52:1 (dark mode's
primary color, matching the frontend's own verified choice), every other
pair clears 5:1 or higher. This also drives Frappe's own "Toggle Theme"
menu item directly (`frappe.ui.set_theme()`), so the two can never
disagree - there's no third "let the user's own toggle decide" option
anymore, which is what let colors from one mode leak into the other in
earlier versions of this app.

## Already Installed This Before? Read This After Every `git pull`

**Every update needs both of these, every time — never just one:**

```bash
bench --site tijarat.local migrate       # DocType/data changes
bench --site tijarat.local build --app custom_design   # CSS/JS changes
bench --site tijarat.local clear-cache
```

`git pull` only updates the source files inside `apps/custom_design/`. It
does not touch the site's database (so a new DocType field or a patch
never runs until `migrate` does), and it does not touch the copy of
`custom_design.css`/`custom_design.js` actually served to the browser at
`/assets/custom_design/...` (`bench build` is what copies `public/` into
`sites/assets/`). Skipping either step means the browser keeps loading
old CSS/JS or the database keeps old data even though the repo is
up to date - **this is the single most common source of "I pulled the
fix and nothing changed."**

### Postmortem: why dark mode broke even though only colors should have changed

Frappe marks dark mode with a `data-theme="dark"` **attribute** on
`<html>` (set by `frappe.ui.set_theme()` - confirmed against
`frappe/frappe`'s own `theme_switcher.js`), not a `dark` CSS **class**.
An earlier version of this app's CSS/JS assumed the class. Every
dark-mode-specific rule was silently dead — never matching anything —
which is *also* why dark mode looked fine at first: nothing here was
overriding it, so Frappe's own native dark theme (plus this file's
light-mode rules, which weren't scoped to exclude dark mode) painted
through untouched. Once a later patch corrected the light-mode sidebar
color from the original dark navy to white, that white started forcing
itself into real dark-mode sessions too, since the light-mode rule fires
whenever this app is enabled, full stop - the intended dark-mode override
never engaged to stop it. Fixed by switching every dark-mode selector to
`[data-theme="dark"]`; also corrected icon coloring (Frappe icons pick up
`color` via inheritance - forcing `fill` directly, which an earlier
version did, is ineffective at best and can add an unwanted solid fill
to outline-style icons at worst) and added real, verified Frappe class
names (`.body-sidebar`, `.es-icon`, etc.) alongside the defensive
guesses, cross-checked against Frappe's own source and a working
third-party Frappe theming app rather than assumed.

A doctype JSON change (new field, new default) only ever affects **brand
new** installs automatically — Frappe never retroactively rewrites values
already saved in an existing site's database just because a shipped
default changed. `bench migrate` runs this app's patches
(`custom_design/patches.txt`), which backfill already-installed sites to
match what a fresh install would get — stale color values reset to the
current defaults (only if they're still exactly the old shipped default,
never if you've customized them), new dark-mode fields filled in, brand
text synced, and the starter sidebar override seeded.

### Postmortem: the oversized blank "footer"

Traced to the "Cards, widgets, number cards" CSS rule matching `.widget` -
Frappe's generic workspace-widget wrapper class, used for far more than
visible cards, including empty spacer/placeholder containers reserved for
layout during workspace edit/load. Forcing a visible `background-color` +
`border` onto every `.widget` turned an otherwise-invisible empty one into
a large blank colored box. Fixed by targeting `.widget-body` (the actual
content pane) instead of the outer `.widget` wrapper, plus a `:not(:empty)`
guard kept on every card selector as a second line of defense.

### If theme changes still don't stick after a refresh

Client-side, `custom_design.js` now self-heals: a `MutationObserver`
watches `<html>`'s own attributes and re-asserts `data-cd-theme="on"`
whenever it's missing, rather than depending on having been set correctly
exactly once at boot. Server-side, `boot_session` (which supplies the
theme to every page) is wrapped end-to-end in `try/except` with
`frappe.log_error()` - if theme settings intermittently fail to apply,
check **Desk > Error Log** for entries titled "custom_design: boot_session
failed" to confirm whether that's actually happening, since it's the kind
of thing (a transient Redis hiccup, for instance) that's easy to suspect
without a way to verify it currently is or isn't the cause. If refreshes
still revert after `migrate` + `build` + `clear-cache`, add
`bench restart` to that sequence too - it's the one step of the four that
actually restarts every worker process, and is worth ruling out on
principle even though Frappe's own document cache is Redis-backed (shared
across workers, not per-process) and should auto-invalidate on save.

## What Gets Installed Automatically

Nothing manual is needed after `bench install-app` — this is intentional:

- **Design Settings** (single, System Manager only) — the control panel
- **Design Settings Chart Color**, **Hidden Module**, **Sidebar Link
  Override** — child tables used inside Design Settings
- **Custom Design** workspace — sidebar entry point with a shortcut to
  Design Settings
- Default chart color palette (5 colors, matching the brand) — seeded by
  `after_install`
- Brand colors as the DocType's own field defaults — no seeding needed for
  those, Frappe applies field defaults automatically to Single DocTypes

## Install

```bash
cd ~/backend/frappe-bench
bench get-app https://github.com/YOUR_ORG/custom_design.git
bench --site tijarat.local install-app custom_design
```

(Swap in whichever git remote you push this to — matches your local-folder
→ git → VPS pull workflow.)

**Test immediately after install:**
```bash
bench --site tijarat.local list-apps
```
Confirm `custom_design` appears. Then log into the Desk — the sidebar/navbar
colors should already reflect the brand palette with zero configuration.

## Using It

Open **Design Settings** (search for it, or use the Custom Design workspace
shortcut in the sidebar). Every field is editable through the normal Frappe
form UI — colors use a color picker, images use the standard file
attachment control, nothing requires touching code.

- **Apply Live Preview** button — see a change on your own session before
  saving, without affecting other users yet
- Saving applies the change system-wide immediately (cache is cleared
  automatically on save — no bench restart needed)
- **Enable Custom Design** checkbox — master off switch, instantly reverts
  to unmodified ERPNext styling if something looks wrong

### Menu / Sidebar Overrides

A reference box above the **Sidebar Link Overrides** table lists common
Help/User menu labels (About, Documentation, Keyboard Shortcuts, Frappe
Support, etc.) as a starting point for `Match Label` - exact text varies a
little by Frappe version, so treat it as a hint, not a guarantee, and
verify against what you actually see. `Match Label` must be the *exact*
visible text of the item as it currently appears (case and spacing
sensitive). Leave `New Label`/`New Link` blank to only change one of them.
Check `Hide This Item Instead` to hide it entirely rather than relabel it -
this is how you show/hide individual menu items (About, Support, whatever
else appears in the Help/User dropdowns), the same mechanism as sidebar
renames, since both are just DOM elements matched by their visible text.

`New Icon` accepts either a built-in Frappe icon name or a full image URL
(paste an uploaded file's URL) - applied through whichever icon mechanism
the matched element actually uses, best-effort since there's no reliable
way to know which one without inspecting the live element.

**Modules** (e.g. hiding entire sections like "CRM" or "Assets" from the
sidebar/app switcher): use the **Hidden Modules** table instead — pick the
module by name, not by matching visible text.

A starter row is seeded automatically (once, only if the table is still
empty, so it's edit/delete-able like any override you'd add yourself):
renames "Frappe HR" to "*Application Name* Teams" if a site has the HRMS
app installed and that label is visible somewhere the override matcher
can reach. Doesn't do anything if HRMS isn't installed. Edit or delete it
like any other row - it's just data, not a rule this app enforces.

### Frappe/ERPNext Branding Text

Setting **Application Name** replaces the words "Frappe" and "ERPNext"
with that name across the Desk — page titles, tooltips, the "Powered by"
footer link, and outgoing system emails — the moment you save. No separate
button or step: saving the form is the trigger, same as every other field
here.

Two mechanisms do this, both reversible by unchecking **Enable Custom
Design**:

- **Server-side (does most of the work):** `Translation` records for a
  curated list of known Frappe/ERPNext strings ("Frappe", "ERPNext",
  "Powered by Frappe", etc.), which Frappe's own `__()` translation layer
  then substitutes everywhere it's used — most Desk chrome, tooltips, and
  system messages. Plus `System Settings.disable_standard_email_footer`
  so outgoing emails stop appending Frappe's own footer, replaced with
  one naming your app instead (only touched if you haven't already set a
  custom email footer yourself).
- **Client-side (safety net):** a DOM pass for chrome that isn't routed
  through `__()` — the "Powered by Frappe" footer link specifically, plus
  the navbar's own dropdown menus (user menu, help menu, app switcher) and
  any currently-open modal (About dialog, etc.), walked in full. Scoped to
  those structurally-chrome containers only, never a whole-page walk — a
  menu or dialog can't contain arbitrary document data the way a list
  view or form can, so this never touches a customer name or note that
  happens to contain the word "ERPNext".

This is best-effort, not exhaustive: the exact literal strings Frappe
ships vary a little by version, and a handful of hard-coded email
templates aren't routed through `__()` at all. If you spot one that
didn't get replaced, add it yourself the normal way — Desk >
Translation — no code change needed, this app's own Translation records
work exactly the same way.

Already-installed sites pick this up automatically too: pulling this
update and running `bench migrate` runs the same sync via a patch (see
`custom_design/patches.txt`), it isn't limited to fresh installs.

### Icons

- **This app's own icons** — the Custom Design workspace and its Design
  Settings shortcut now use Frappe's "Purple" indicator color instead of
  plain grey/blue, closer to the brand's indigo.
- **Sidebar module icons** — Selling, Buying, Stock, Accounts, CRM,
  Assets, Projects, and Support each get their own color from a
  colorblind-safe 8-hue categorical palette (validated with the dataviz
  skill's contrast/CVD checker against this app's actual sidebar
  background, not just eyeballed). Deliberately capped at 8 — any module
  past those isn't recolored rather than reusing a hue or guessing a 9th
  one, since that would undermine the whole point of a validated set.
  Targeted by each module's public route (`/app/selling`, etc.) rather
  than sidebar DOM/class names, since routes are far more stable across
  Frappe versions. Sets `color` (verified mechanism — Frappe icons pick up
  inherited `color` via `currentColor`, either as an SVG fill/stroke or as
  the tint behind a `mask-image` on the newer icon system; there's no
  `fill` to force) on the link and on the verified icon-bearing
  descendants (`.icon`, `.es-icon`, `svg`, `.sidebar-item-icon`),
  `!important` since Frappe's own icon styling is reasonably specific —
  if a given site's icons still don't pick up color, it's a harmless
  no-op, not a broken layout, and the module's text label is unaffected
  either way.

### App / Module Label Overrides

A separate table from Sidebar Link Overrides, for a different job: pick
any installed app/module by its actual `Module Def` record and give it a
custom display label, applied globally (sidebar, app switcher, workspace
list) via a `Translation` record - the exact same non-hard-coded mechanism
as the Frappe/ERPNext text replacement, just driven by this table instead
of a fixed word list. This only ever changes the *label* - nothing about
the module's real name, routes, permissions, or reports is touched, so
nothing that depends on those breaks.

### Login Page

Everything here needed its own delivery mechanism (`web_include_css`/
`web_include_js`, a new `login.css`/`login.js`) since Desk's
`app_include_css`/`app_include_js` never reach the login page at all - a
gap this app had for every earlier release. `login.js` only activates once
it confirms it's actually looking at the login page (Frappe's own
`.for-login` wrapper class), so loading it on every website page is
harmless. Config reaches it through a small guest-allowed API endpoint
(`custom_design.api.get_login_settings`) - the login page is
unauthenticated, so there's no session yet to read settings from the way
the Desk-side script does, and that endpoint deliberately returns only
display fields, never `Custom CSS`/`Custom JS`/sidebar overrides or
anything else scoped to the authenticated Desk.

- **Disable "Login with Email Link"** (default: on) - turns off Frappe's
  built-in passwordless login button through its own real System Settings
  field (`login_with_email_link`, confirmed against
  `frappe/www/login.html`'s actual gating condition), not CSS
  `display:none` - so the option is actually disabled, not just hidden
  while still reachable by a direct link.
- **Matches the frontend's design** - white/near-black card
  (`.page-card`, Frappe's own real class) on a neutral canvas, indigo
  primary button, rounded corners, dark mode included - the same tokens
  the rest of this app uses, not a separate palette.
- **Application Name** now shows properly on the login page itself - a
  small title (+ **Login Page Tagline**, if set) injected just above the
  existing "Sign In" heading, never replacing it, since "Sign In" is a
  functional instruction, not a brand string.
- **Login Footer Content** - free HTML, replaces the (nonexistent by
  default - Frappe's login page doesn't ship one) footer. **Login Footer
  Size** sets a minimum height (Compact/Normal/Spacious) without clipping
  longer content, since a footer should size to its content, not the
  other way around.

### Advanced / Escape Hatch

`Custom CSS` and `Custom JS` fields exist for anything the structured
fields above don't cover. CSS is injected as a `<style>` tag after the
generated theme CSS, so it can override anything. JS runs once per page
load, after the theme applies.

## Known Risk Area — Please Verify This One Specifically

The **Custom Design workspace** (the sidebar entry point) was hand-written
against Frappe's Workspace JSON schema, but ERPNext v16 changed the
sidebar/workspace rendering significantly (new grouped, persistent
sidebar). If the workspace doesn't show up correctly or looks visually
off after install, **it's a cosmetic issue only** — Design Settings itself
is fully functional and reachable regardless, just search for "Design
Settings" in the awesomebar (top search bar) instead of clicking a sidebar
shortcut. Let me know what you actually see after installing and I'll
adjust the workspace JSON to match v16's real rendering rather than
guessing further blind.

Similarly, the **sidebar link override** feature works by matching visible
text in the rendered DOM and re-applying on every mutation (since v16's
sidebar re-renders dynamically) — this is a best-effort approach given
v16's sidebar internals are new. Test it with one simple rename first
(e.g. rename "Help" to something else) before relying on it for anything
important, and report back what does/doesn't work so it can be refined
against your actual v16 instance rather than assumptions.

## Uninstall

```bash
bench --site tijarat.local uninstall-app custom_design
```
