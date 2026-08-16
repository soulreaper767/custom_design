// custom_design: webshop's product search only searches on the "input"
// event (see webshop's product_ui/search.js) - there's no Enter-key
// handling at all, so pressing Enter silently does nothing. This re-fires
// the same input event on Enter so pressing it to "confirm" a search
// actually does something, without touching webshop's own file (which
// would get wiped out on the next `bench update`).
document.addEventListener("keydown", function (e) {
	if (e.key !== "Enter") return;
	var target = e.target;
	if (!target || target.id !== "search-box") return;
	e.preventDefault();
	target.dispatchEvent(new Event("input", { bubbles: true }));
});
