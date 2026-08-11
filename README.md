# Custom Design

No-code theme, branding, and navigation customization for ERPNext — one
settings screen controls colors, fonts, corner roundness, sidebar/navbar
colors, dashboard chart colors, logo/favicon, and menu item overrides
(rename, relink, or hide any sidebar/menu item by matching its text).

Ships with defaults already matching the Tijarat frontend's actual design
tokens (`dev/frontend/src/index.css`: indigo primary, slate neutrals,
emerald/red/amber/sky semantic colors) so backend and frontend look
consistent from the moment it's installed — no configuration required to
get that baseline. Every color that would otherwise read as near-invisible
against a dark background (a light-mode indigo sits at roughly 1:1
contrast on a near-black page) has its own literal dark-mode default,
mirroring the frontend's own separate light/dark shade choices rather than
computing one from the other — see the "Core Colors (Dark Mode)" and
"Sidebar & Navbar (Dark Mode)" sections on the Design Settings form.

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
- **Client-side (safety net):** a narrowly-scoped DOM pass for the
  handful of chrome elements that aren't routed through `__()`, like the
  "Powered by Frappe" footer link specifically. Scoped to known
  branding/footer elements only — it never touches document data, so a
  customer name or note that happens to contain the word "ERPNext" is
  never rewritten.

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
  than sidebar DOM/class names, since those are far more likely to change
  between Frappe versions (see the sidebar caveat below) — if a given
  site's icons don't pick up color, it's a harmless no-op, not a broken
  layout, and the module's text label is unaffected either way.

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
