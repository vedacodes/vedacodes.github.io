/* Itineraries for each city live in data/itineraries.json.
   Add a city by giving its page data-city="slug" and a matching key
   in that file. Day buttons are only the recommended lengths listed
   there — not a free-form range. */
(function () {
    var script = document.currentScript;
    var mount = document.querySelector("[data-itineraries]");
    if (!mount || !script) return;

    var lead = mount.querySelector("[data-itinerary-lead]");
    var tabs = mount.querySelector("[data-itinerary-tabs]");
    var panels = mount.querySelector("[data-itinerary-panels]");
    var city = mount.getAttribute("data-city");
    var dataUrl = new URL("data/itineraries.json", script.src);

    function fail(message) {
        if (lead) lead.textContent = message;
        if (tabs) tabs.replaceChildren();
        if (panels) panels.replaceChildren();
    }

    function label(days) {
        return days === 1 ? "1 day" : days + " days";
    }

    function render(entry) {
        if (!entry || !Array.isArray(entry.plans) || !entry.plans.length) {
            fail("Itineraries for this city show up here once a recommended length is added.");
            return;
        }

        if (lead) lead.textContent = entry.lead || "Pick a recommended length. The days show up underneath.";

        var plans = entry.plans.slice().sort(function (a, b) { return a.days - b.days; });
        var active = 0;
        plans.forEach(function (plan, index) {
            if (plan.recommended) active = index;
        });

        var buttons = [];
        var panelEls = [];

        plans.forEach(function (plan, index) {
            var tabId = "itinerary-tab-" + plan.days;
            var panelId = "itinerary-panel-" + plan.days;
            var on = index === active;

            var button = document.createElement("button");
            button.type = "button";
            button.className = "itinerary-tab";
            button.setAttribute("role", "tab");
            button.id = tabId;
            button.setAttribute("aria-controls", panelId);
            button.setAttribute("aria-selected", String(on));
            button.tabIndex = on ? 0 : -1;
            button.dataset.days = String(plan.days);
            button.textContent = label(plan.days);

            var panel = document.createElement("div");
            panel.className = "panel" + (on ? " is-on" : "");
            panel.id = panelId;
            panel.setAttribute("role", "tabpanel");
            panel.setAttribute("aria-labelledby", tabId);
            panel.hidden = !on;

            if (plan.summary) {
                var summary = document.createElement("p");
                summary.className = "plan-summary";
                summary.textContent = plan.summary;
                panel.appendChild(summary);
            }

            (plan.itinerary || []).forEach(function (day, dayIndex) {
                var card = document.createElement("article");
                card.className = "card";
                var heading = document.createElement("h3");
                heading.textContent = "Day " + (dayIndex + 1) + " · " + day.title;
                var copy = document.createElement("p");
                copy.textContent = day.text;
                card.append(heading, copy);
                panel.appendChild(card);
            });

            buttons.push(button);
            panelEls.push(panel);
        });

        function select(index, focus) {
            buttons.forEach(function (button, i) {
                var on = i === index;
                button.setAttribute("aria-selected", String(on));
                button.tabIndex = on ? 0 : -1;
            });
            panelEls.forEach(function (panel, i) {
                var on = i === index;
                panel.classList.toggle("is-on", on);
                panel.hidden = !on;
            });
            if (focus) buttons[index].focus();
        }

        buttons.forEach(function (button, index) {
            button.addEventListener("click", function () {
                select(index, false);
            });
            button.addEventListener("keydown", function (event) {
                if (event.key !== "ArrowRight" && event.key !== "ArrowLeft" && event.key !== "Home" && event.key !== "End") return;
                event.preventDefault();
                var next = index;
                if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
                if (event.key === "ArrowLeft") next = (index - 1 + buttons.length) % buttons.length;
                if (event.key === "Home") next = 0;
                if (event.key === "End") next = buttons.length - 1;
                select(next, true);
            });
        });

        tabs.replaceChildren.apply(tabs, buttons);
        panels.replaceChildren.apply(panels, panelEls);
    }

    if (!document.getElementById("itinerary-styles")) {
        var style = document.createElement("style");
        style.id = "itinerary-styles";
        style.textContent = [
            "#itineraries .plan-summary { color: var(--mute); margin: 0 0 16px; max-width: 42rem; }",
            "#itineraries .panel.is-on { grid-template-columns: 1fr; max-width: 46rem; }",
            "#itineraries .tabs button:focus-visible { outline: 2px solid var(--gold); outline-offset: 2px; }"
        ].join("\n");
        document.head.appendChild(style);
    }

    fetch(dataUrl.href)
        .then(function (response) {
            if (!response.ok) throw new Error("missing itineraries");
            return response.json();
        })
        .then(function (all) {
            render(all[city]);
        })
        .catch(function () {
            fail("The day plans could not be loaded. Refresh the page and try the lengths again.");
        });
})();
