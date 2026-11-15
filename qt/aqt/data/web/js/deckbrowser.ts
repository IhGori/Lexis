/* Copyright: Anki Software, LLC and contributors
 * License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html */

$(init);

interface SearchRow {
    nid: number;
    front: string;
    back: string;
    deck: string;
    flag: string | null;
}

let searchSeq = 0;
let searchTimer: number | undefined;

function hideSearchResults() {
    const box = document.getElementById("home-search-results");
    if (box) {
        box.classList.add("hidden");
        box.textContent = "";
    }
}

// two characters, or one in a script written without spaces (kanji, hanzi,
// hangul...), where a single character is already a word
function worthSearching(query: string): boolean {
    return query.length >= 2 || (query.length === 1 && query.codePointAt(0)! > 0x2e7f);
}

function initSearch() {
    const input = document.getElementById("home-search-input") as HTMLInputElement | null;
    if (!input) {
        return;
    }
    input.addEventListener("input", () => {
        window.clearTimeout(searchTimer);
        const query = input.value.trim();
        if (!worthSearching(query)) {
            searchSeq += 1; // drop any answer still on its way
            hideSearchResults();
            return;
        }
        searchTimer = window.setTimeout(() => {
            searchSeq += 1;
            pycmd(`search:${searchSeq}:${query}`);
        }, 200);
    });
    input.addEventListener("keydown", (event) => {
        const query = input.value.trim();
        if (event.key === "Enter" && query) {
            pycmd(`search_all:${query}`);
        } else if (event.key === "Escape") {
            input.value = "";
            hideSearchResults();
            input.blur();
        }
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "/" && document.activeElement !== input) {
            event.preventDefault();
            input.focus();
        }
    });
    document.addEventListener("click", (event) => {
        if (!(event.target as Element).closest(".home-search")) {
            hideSearchResults();
        }
    });
}

// called from Python with the answer to a "search:" command
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function deckSearchResults(result: { seq: number; total: number; rows: SearchRow[] }) {
    if (result.seq !== searchSeq) {
        return; // a newer search has been started since
    }
    const box = document.getElementById("home-search-results");
    const label = document.querySelector<HTMLElement>(".home-search")?.dataset.notesLabel ?? "";
    if (!box) {
        return;
    }
    box.textContent = "";
    if (!result.rows.length) {
        box.classList.add("hidden");
        return;
    }
    // text is always set through textContent: note fields are untrusted HTML
    for (const row of result.rows) {
        const item = document.createElement("div");
        item.className = "search-row";
        if (row.flag) {
            const flag = document.createElement("img");
            flag.className = "search-flag";
            flag.src = `/_anki/imgs/flags/${row.flag}.svg`;
            flag.alt = "";
            item.append(flag);
        }
        const text = document.createElement("div");
        text.className = "search-text";
        const front = document.createElement("div");
        front.className = "search-front";
        front.textContent = row.front;
        const back = document.createElement("div");
        back.className = "search-back";
        back.textContent = row.back;
        text.append(front, back);
        const deck = document.createElement("div");
        deck.className = "search-deck";
        deck.textContent = row.deck;
        item.append(text, deck);
        item.addEventListener("click", () => pycmd(`search_note:${row.nid}`));
        box.append(item);
    }
    const footer = document.createElement("div");
    footer.className = "search-footer";
    footer.textContent = `${result.total} ${label}`;
    box.append(footer);
    box.classList.remove("hidden");
}

function init() {
    initSearch();
    // label the forecast bars with localized weekday names, starting today
    document.querySelectorAll<HTMLElement>("[data-day-offset]").forEach((el) => {
        const date = new Date(Date.now() + Number(el.dataset.dayOffset) * 86400000);
        el.textContent = date.toLocaleDateString(undefined, { weekday: "short" });
    });
    $("tr.deck").draggable({
        scroll: false,

        // can't use "helper: 'clone'" because of a bug in jQuery 1.5
        helper: function(_event) {
            return $(this).clone(false);
        },
        delay: 200,
        opacity: 0.7,
    });
    $("tr.deck").droppable({
        drop: handleDropEvent,
        hoverClass: "drag-hover",
    });
    $("tr.top-level-drag-row").droppable({
        drop: handleDropEvent,
        hoverClass: "drag-hover",
    });
}

function handleDropEvent(event, ui) {
    const draggedDeckId = ui.draggable.attr("id");
    const ontoDeckId = $(this).attr("id") || "";

    pycmd("drag:" + draggedDeckId + "," + ontoDeckId);
}
