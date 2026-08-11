# Custom Design

No-code theme, branding, and navigation customization for ERPNext — one
settings screen controls colors, fonts, corner roundness, sidebar/navbar
colors, dashboard chart colors, logo/favicon, and menu item overrides
(rename, relink, or hide any sidebar/menu item by matching its text).

Ships with defaults already matching the Tijarat frontend's brand palette
(ink-blue, brass, parchment) so backend and frontend look consistent from
the moment it's installed — no configuration required to get that baseline.

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

In the **Sidebar Link Overrides** table: `Match Label` must be the *exact*
visible text of the item as it currently appears (case and spacing
sensitive). Leave `New Label`/`New Link` blank to only change one of them.
Check `Hide This Item Instead` to hide it entirely rather than relabel it.

**Modules** (e.g. hiding entire sections like "CRM" or "Assets" from the
sidebar/app switcher): use the **Hidden Modules** table instead — pick the
module by name, not by matching visible text.

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
