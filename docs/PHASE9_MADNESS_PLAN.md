# Phase 9 Plan: The Madness Layer

Status: **draft for Bunny's review.** Nothing here is built yet. Nothing in this phase starts until Bunny says go.

---

## 1. The idea in one paragraph

The current site stays exactly as it is. It is the clean, fast version for recruiters who give it 30 seconds. On top of it sits a hidden **madness layer**: secret effects that visitors unlock with cheat codes, by poking Wall-E, or by finding hidden triggers. Each effect takes over the page they are already on (Wall-E eats the text, the page inverts in time, the roster turns into bounty posters). Finding secrets earns achievements, and finding all of them unlocks a **director's cut**: the full cinematic version of the site. One key (Esc) or one button always brings the clean site back.

**Rule of the phase: sane surface, mad underneath.** A recruiter who never triggers anything must get the exact same site, at the exact same speed.

---

## 2. Principles (apply to every layer)

1. **Opt-in only.** Nothing plays unless the visitor triggers it. No autoplay, no first-visit takeover.
2. **Always escapable.** Esc, or the "Back to normal" pill that appears while any layer is active, restores the page fully (DOM, scroll position, Wall-E, timers).
3. **Zero cost for the normal visitor.** Only a tiny core script loads by default. Layer code and CSS download only after a trigger.
4. **Inspired by, never copied.** No film or game names, logos, stills, quotes, music or official fonts on the site. Invent our own cheat words and lines.
5. **Honest content.** Bounties, time spent and Wall-E's lines use only real data or Bunny's own words. Drafts use `[TODO: Bunny]`. No invented bugs, numbers or dates.
6. **Site copy rules still apply.** No emoji icons, no em dashes in any visible text.
7. **Respect reduced motion.** With `prefers-reduced-motion`, every layer shows a still version (a "postcard") instead of the animation.
8. **Works on phones.** Every trigger has a touch path, not just a keyboard path.
9. **Accessible.** Wall-E's subtitles go through an `aria-live="polite"` region. No focus traps. The "Back to normal" pill is a real button.
10. **Calm by default even when mad.** Animate only `transform` and `opacity`, use `requestAnimationFrame`, stop every timer on exit and when the tab is hidden.

---

## 3. Inventory

### 3.1 Ways in (triggers)

| Trigger | Desktop | Phone | Notes |
|---|---|---|---|
| Cheat codes | Type a word anywhere (ignored inside inputs) | Typed into the code prompt (below) | Our own invented words, one per layer |
| Code prompt | Click the hidden footer glyph | Tap the hidden footer glyph | Opens a tiny terminal-style input: "enter code". Solves "phones have no keyboard" |
| Wall-E malfunction | Press and hold Wall-E for 1.5 s | Long-press Wall-E | A normal click still opens the chat. Holding makes him glitch and offer a random unlocked-next layer |
| Chat secrets | Ask Wall-E a secret phrase | Same | Rule-based answer with a hint and a "try it" button |
| Console note | Message in dev tools console | n/a | For engineers: a short note and the first code |
| Hidden spots | Long-press the Flagship badge; double-click the KP logo | Same with long-press | Each spot unlocks one specific layer |
| Credits hint | End of the director's cut credits | Same | Hints at the last undiscovered secret |

### 3.2 Madness layers

| # | Layer | Inspired by (internal note only) | Size | Data needed |
|---|---|---|---|---|
| L1 | Wall-E compactor | Wall-E | M | none |
| L2 | Inversion | Tenet | M | none |
| L3 | Self-aware Wall-E | Wall-E, games | S | none |
| L4 | Previously on | TV series recaps | S | visitor's own browser history of the site (local only) |
| L5 | Eaten 404 | Dune | S | none |
| L6 | Bounty board | RDR | M | `CaseIncident` (already exists) |
| L7 | Radio logs | GTA | M | `BlogPost.log_type` (already exists) |
| L8 | Drop zone | PUBG | L | existing home page data |
| L9 | Desert night | Dune | M | none |
| L10 | Time dilation | Interstellar | S | new optional `Project.hours_spent` |
| L11 | Director's cut | all of it | L | existing data |
| L12 | Black hole | Interstellar | XL | none |
| L13 | Sandworm | Dune | L | none |

### 3.3 Small eggs

Quick, self-contained surprises. Each one unlocks an achievement.

| # | Egg | Inspired by (internal note only) | Size |
|---|---|---|---|
| E1 | Dead-eye | RDR | M |
| E2 | Campfire | RDR | S |
| E3 | Wanted level | GTA | S |
| E4 | Mission complete | GTA | S |
| E5 | Mechanical map | GoT | M |
| E6 | Frost and the wall | GoT | S |
| E7 | Raven post | GoT | S |
| E8 | Houses of the stack | GoT | S |

The bounty board (L6), radio logs (L7) and the cheat codes themselves already cover the other RDR and GTA references.

### 3.4 Rewards and safety
- **Achievements:** one per layer, stored in the visitor's own browser. A small counter ("3 / 10 secrets") appears only after the first find.
- **Final reward:** when every other secret is found, the black hole (L12) swallows the normal site and spits out the director's cut (L11). See L11 for the alternative if Bunny prefers them separate.
- **Back to normal:** Esc or the pill, always.
- **Admin off switch:** `SiteSettings.madness_enabled`. Off means the core script is not even included.

---

## 4. Architecture

### 4.1 Files

```
static/madness/
  core.js          always loaded (tiny): triggers, registry, state, Esc, achievements, lazy loader
  madness.css      loaded on first trigger: shared UI (pill, subtitles, code prompt, toasts, achievements)
  layers/
    compactor.js   one file per layer, loaded on demand
    inversion.js
    selfaware.js
    previously.js
    bounty.js
    radio.js
    dropzone.js
    desert.js
    dilation.js
    directors_cut.js
    blackhole.js     WebGL shader, the largest file, loaded only on unlock
    sandworm.js
    eggs.js          all small eggs (E1 to E8) in one file
  img/
    blackhole-still.webp   fallback for no WebGL and reduced motion
templates/
  404.html         eaten 404 (also the normal 404, with a plain fallback)
  partials/madness_core.html   includes core.js + config, only when enabled
```

This breaks two current rules ("all CSS in `static/styles.css`" and "no heavy animations"), so both need an explicit exception. See section 8.

### 4.2 Core API (`core.js`)

```js
window.Madness = {
  register(name, { start, stop, achievement, reducedMotion }),  // called by each layer file
  trigger(name),        // lazy-loads layers/<name>.js + madness.css, then calls start()
  stop(),               // stops the active layer, restores everything
  active,               // name of the running layer or null
  found(),              // list of unlocked achievements
  say(text, ms),        // Wall-E subtitle via the aria-live region
};
```

- **One layer at a time.** Triggering a new layer stops the current one first. L4 (Previously on) and L3 (Self-aware Wall-E) are passive and can run alongside.
- **State on the page:** `<html data-mm="inversion">` so CSS can scope everything under `[data-mm]`. Nothing in `madness.css` matches unless a layer is active.
- **Restore contract:** every layer's `stop()` must undo all DOM changes, remove added nodes, clear timers and listeners, and restore scroll position. The core verifies by re-checking that no `.mm-*` nodes remain.
- **Lazy loading:** `trigger()` injects `<script src=".../layers/<name>.js">` once and caches the promise. CSS is injected once on the first trigger.
- **Storage:** `localStorage["mm:v1"] = { found: [...], visits: [...], last: {...} }`, every read and write in `try/catch`. If storage is blocked, everything still works, it just forgets.
- **Config from Django:** `partials/madness_core.html` renders a `json_script` with `{ enabled, static_base, data_url }` so the JS never hardcodes paths.

### 4.3 Backend

- **`SiteSettings.madness_enabled`** (bool, default `True`). Admin: in a new "Madness layer" fieldset.
- **`Project.hours_spent`** (positive int, optional). L10 only shows for projects that have it filled. Bunny fills real numbers or leaves it empty.
- **Endpoint `GET /api/madness/data/`** returns JSON for the data-driven layers, loaded only when a layer needs it:
  - `bounties`: from `CaseIncident` (project title, slug, symptom, root cause, fix).
  - `stations`: blog posts grouped by `log_type` (title, slug, date, type).
  - `dilation`: projects with `hours_spent`.
  - Returns 404 when `madness_enabled` is off. No personal data beyond what the site already shows.
- **Chat secrets:** one new `ChatAnswer` topic (`secrets`) seeded by a data migration with keywords like "secret", "cheat", "easter egg". The answer text is Bunny's, and it can include a hint. The chat widget turns a marker such as `[[try:inversion]]` in an answer into a "Try it" button that calls `Madness.trigger()`.
- **Migration set:** one, clearly named, e.g. `0028_phase9_madness_layer.py` (fields) and `0029_seed_secrets_chat_answer.py` (data).
- **`404.html`:** Django serves it when `DEBUG=False`. Needs a test with `DEBUG=False`.

### 4.4 Performance budget
- `core.js` under 4 KB gzipped, no dependencies.
- Each layer under 15 KB gzipped. No libraries, no images over 30 KB, inline SVG preferred.
- Exception: `blackhole.js` may reach 30 KB gzipped (shader plus fallbacks). It caps its render resolution on phones and high-DPI screens and targets 60 fps on a mid-range laptop, dropping quality before frames.
- Normal-mode Lighthouse score and page weight must not change by more than the size of `core.js`.

---

## 5. Layer specs

Each layer below lists: trigger, what happens, details that make it feel finished, reduced-motion version, phone version, exit, and achievement name. All visible text marked `[TODO: Bunny]` must be written or approved by Bunny.

### L1. Wall-E compactor
- **Trigger:** cheat word `[TODO: Bunny]`, or Wall-E malfunction.
- **What happens:**
  1. Wall-E's eyes flicker and he leaves his corner.
  2. He rolls to a word on screen, grabs it, and it shrinks into a small cube carrying the word.
  3. He carries the cube to a corner and stacks it. The pile grows into a little tower and leans, but never falls on content.
  4. Lines as subtitles at moments in the run `[TODO: Bunny]`.
  5. He stops after about 30 words, or when nothing visible is left, then sits on top of his tower.
- **Details:**
  - Words are wrapped in spans only inside chosen containers (hero, roster, logs, case-file headings), never inside links' `href` or form fields.
  - Cube colour follows the design tokens. A short "crunch" squash animation on each cube.
  - Scrolling while he works makes him chase the next visible word.
  - Clicking the tower scatters the cubes back to their places (that is the fun way to reset).
- **Reduced motion:** words fade out one by one and a still picture of Wall-E on a cube tower appears.
- **Phone:** fewer words (15), pile in the bottom-left above the safe area.
- **Exit:** Esc, the pill, or clicking the tower. Every word returns.
- **Achievement:** `[TODO: Bunny]` (example style: "Directive complete").

### L2. Inversion
- **Trigger:** cheat word, or double-click the KP logo.
- **What happens:**
  1. A red bar and a blue bar slide in on the left and right edges.
  2. The page flips into a mirror image, including the nav, with a short, smooth turn.
  3. The view jumps to the end of the page. Scrolling down moves up (wheel, keys and touch swipe all reversed).
  4. A countdown runs backwards in the corner.
  5. Headings "un-type" and re-type themselves once as they come into view.
  6. Case files in this mode show their sections in reverse: outcome first, then incidents, then decisions, then the problem.
- **Details:** reaching the top of the page plays a small "you made it back to the start" moment, then offers "Play forward" (normal mode).
- **Reduced motion:** no flip animation. The page is mirrored and the scroll is reversed instantly, with a note explaining it.
- **Phone:** swipe direction reversed with touch handlers. The mirror covers the content only, not the browser UI.
- **Exit:** Esc, the pill, or "Play forward".
- **Achievement:** `[TODO: Bunny]`.

### L3. Self-aware Wall-E (passive, always on once unlocked)
- **Unlock:** the first time any secret is found.
- **What happens:** Wall-E reacts to the visitor:
  - Very fast scrolling: he holds on and wobbles, with a subtitle.
  - Idle for 60 s: he falls asleep (eyes dim).
  - Ignoring him on 3 pages: he hides behind the footer and peeks out.
  - Resize the window very small: he squishes.
- **Details:** each reaction plays at most once per page, so it never gets annoying.
- **Reduced motion:** reactions become still expressions only.
- **Exit:** a toggle in the achievements panel ("Wall-E's personality: on/off").
- **Achievement:** none (this is the reward for finding the first secret).

### L4. Previously on (passive)
- **Unlock:** second visit after finding any secret.
- **What happens:** on return, a short recap card appears for a few seconds: what they looked at last time, built from their own local history of the site (page titles only). Example structure: "Previously: you opened [project], read [log], found [n] secrets."
- **Details:** dismissible, shows once per visit, never sent anywhere. Wording `[TODO: Bunny]`.
- **Reduced motion:** same card, no slide-in.
- **Exit:** close button, Esc.

### L5. Eaten 404
- **Trigger:** any broken link (it is the real 404 page).
- **What happens:** the page looks like it was swallowed by something under the sand: torn edges, a half-buried nav, and Wall-E digging. The useful part stays clear: "This page is gone. Go home / See projects / Contact".
- **Details:** a hidden dig spot on this page unlocks an achievement.
- **Reduced motion and plain fallback:** the same message and links, without the digging.
- **Achievement:** `[TODO: Bunny]`.

### L6. Bounty board
- **Trigger:** cheat word, or long-press the Flagship badge.
- **What happens:**
  1. The roster table "pins up" into a row of wanted posters, one per real `CaseIncident`.
  2. Each poster: the bug as the outlaw (symptom), "last seen in" (project), "known accomplice" (root cause), and a "bounty claimed" stamp with the fix.
  3. Clicking a poster opens that case file at its incidents section.
- **Details:** if there are no incidents, the layer says "No bounties posted yet" instead of inventing any. Poster text comes straight from admin data, so it is always real.
- **Reduced motion:** posters appear in place, no pin-up animation.
- **Phone:** posters become a vertical stack.
- **Exit:** Esc, the pill.
- **Achievement:** `[TODO: Bunny]`.

### L7. Radio logs
- **Trigger:** cheat word, or click the "Logs" label on the home page three times.
- **What happens:**
  1. A radio dial slides in over the logs section. Each `log_type` is a station (build log, incident, decision, note).
  2. Turning the dial plays a short static effect (visual only, no sound by default) and switches the list to that station's posts.
  3. Wall-E "DJs" each station with a one-line intro `[TODO: Bunny]`.
- **Details:** station names `[TODO: Bunny]`. Optional sound only behind an explicit "sound on" button.
- **Reduced motion:** no static effect, instant switch.
- **Exit:** Esc, the pill.
- **Achievement:** `[TODO: Bunny]`.

### L8. Drop zone
- **Trigger:** cheat word.
- **What happens:**
  1. The page zooms out into a top-down "map" of the site's sections: Agents, Logs, About, Contact, Resume.
  2. A flight path line crosses it. The visitor clicks where to drop.
  3. After the drop, a circle "zone" closes in, fading everything that is not essential until only the 30-second view remains (name, looking for, best work, links).
  4. A final card: "You made it to the end zone" with the resume and contact.
- **Details:** this doubles as the fastest recruiter summary on the site.
- **Reduced motion:** a static map; clicking a section scrolls there; the "zone" is a simple fade to the 30-second view.
- **Phone:** the map becomes a list of drop points.
- **Exit:** Esc, the pill, or landing.
- **Achievement:** `[TODO: Bunny]`.

### L9. Desert night
- **Trigger:** cheat word.
- **What happens:**
  1. The palette shifts from gold on black to sand and ember under a deep night sky (only CSS custom properties change, so it is cheap).
  2. Fine sand slowly piles up along the bottom of the viewport as the visitor scrolls.
  3. When the pile gets high, Wall-E rolls along and sweeps it away.
- **Details:** the sand is a single canvas or a few CSS shapes, capped in size, paused when the tab is hidden.
- **Reduced motion:** palette shift only, no sand.
- **Exit:** Esc, the pill.
- **Achievement:** `[TODO: Bunny]`.

### L10. Time dilation
- **Trigger:** cheat word while on a case file.
- **What happens:** a small instrument panel appears: "time spent building this" (from `hours_spent`) next to "time you have spent reading" (live). The visitor's clock ticks normally while the build clock is shown as a huge, slowly counting total.
- **Details:** only shows for projects with `hours_spent` filled. Otherwise it says the number is not logged yet. No estimates, no rounding up.
- **Reduced motion:** static numbers.
- **Exit:** Esc, the pill.
- **Achievement:** `[TODO: Bunny]`.

### L11. Director's cut
- **Unlock:** every other achievement found. Then a new cheat word appears in the achievements panel.
- **What happens:** the cinematic version from the earlier mockup, built from existing data:
  1. **Cold open:** letterbox bars, the ringed planet over the dune ridge, the name in wide type, Wall-E's subtitle.
  2. **Act I, origin:** about and education as scenes.
  3. **Act II, missions:** each project as a scene from a different world, with its replay inside.
  4. **Interlude:** the journey timeline that runs backwards until inverted.
  5. **End credits:** the stack, the contact, and a hint toward any hidden extra.
- **Details:** it is an overlay on the home page, not a new URL, so nothing is indexed and the recruiter site is untouched. Scenes are driven by scroll, with keyboard arrows as an alternative.
- **Reduced motion:** scenes as still frames with captions.
- **Phone:** vertical scenes, letterbox thinner.
- **Exit:** Esc, the pill, or "Roll credits" at the end.
- **Achievement:** final one `[TODO: Bunny]`.
- **Alternative (Bunny to choose):** keep the black hole and the director's cut as two separate unlocks instead of chaining them.

### L12. Black hole
- **Trigger:** a tiny dark dot hidden somewhere on the page (position `[TODO: Bunny]`). Hovering it makes nearby stars bend slightly. Clicking it, or a cheat word, starts the event.
- **What happens:**
  1. The dot grows into a realistic black hole: a bright ring of hot gas (accretion disk), light from behind it bent over and under it (gravitational lensing), a thin photon ring, and pure black at the centre.
  2. Content starts to drift toward it, nearest first: cards, headings, then whole sections.
  3. Near the edge, elements stretch long and thin (spaghettification) and slow almost to a stop (time dilation).
  4. Everything is gone. A few seconds of black, silent space with only the black hole turning.
  5. Click it, or Esc, and everything is thrown back out and flies into place.
- **How it is built:**
  - Rendering: a hand-written WebGL fragment shader on a full-screen canvas. It ray-marches bent light paths around the black hole over a procedural star field and a procedural disk (Doppler brightening on the side moving toward the viewer). No libraries, no textures to download.
  - Content motion: real DOM elements animated with `transform` and `opacity` only. Each element's path is a spiral toward the centre; the stretch is a `scale` along the direction to the centre; the slowdown is an easing curve that flattens near the edge.
  - Restore: each element's original state is recorded before it moves, and the exit plays the paths in reverse.
  - The canvas renders at reduced resolution and upscales; it pauses when the tab is hidden and stops completely on exit.
- **Details:** the visible text never names the film. Optional low hum behind an explicit "sound on" button only.
- **Fallbacks:** no WebGL: the pre-rendered still image with the same content motion. Reduced motion: the still image, content fades out and back in.
- **Phone:** lower render resolution, fewer elements animated (sections, not every card).
- **Exit:** Esc, the pill, or clicking the black hole.
- **Achievement:** `[TODO: Bunny]`.
- **Note:** the hardest effect in the plan. It gets its own sub-phase (9.6).

### L13. Sandworm
- **Trigger:** click or tap a steady rhythm on empty space, like a thumper drumming the sand. Rhythm `[TODO: Bunny]` (example: 4 slow, even taps). Also a cheat word.
- **What happens:**
  1. The page starts to tremble very slightly.
  2. Ripples travel through the page as if something is moving under the surface, getting closer to the content.
  3. A giant worm erupts from the bottom of the screen, swallows a whole section (the roster by default) and sinks back down.
  4. Wall-E panics and escapes just in time.
  5. Bonus: keep drumming after the worm sinks and it comes back for you to ride. Scrolling becomes riding across the dunes until the visitor jumps off (Esc or a "jump off" button).
- **How it is built:** the worm is a segmented SVG body following a path, with the mouth opening as it surfaces. Ripples are a few CSS-animated SVG arcs. The tremble is a tiny `transform` on the page wrapper, max a few pixels.
- **Details:** our own creature design (not the film's). It never covers the "Back to normal" pill.
- **Reduced motion:** no tremble or ripples; a still image of the worm holding the section, then everything returns.
- **Phone:** tap rhythm works; the ride is vertical swipe.
- **Exit:** Esc or the pill. The worm spits the section back out.
- **Achievement:** `[TODO: Bunny]`. Riding it is a second, hidden achievement.

---

## 5b. Small egg specs

All small eggs live in `layers/eggs.js`, loaded on the first trigger of any egg. Each respects reduced motion and Esc like the big layers.

### E1. Dead-eye
- **Trigger:** hold a key (`[TODO: Bunny]`) on desktop, or long-press empty space on a phone, while on the home page or the case board.
- **What happens:** time slows, the page drains of colour, a crosshair follows the pointer. Click to mark up to 3 projects (each gets a red mark). Release the key and they "fire" one after another: each marked card flashes and opens in turn (new tabs on desktop, a quick queue on phones).
- **Reduced motion:** colour drains instantly; marks and opening still work, no slow motion.

### E2. Campfire
- **Trigger:** passive. Visiting between `[TODO: Bunny]` (example: 11 pm and 4 am, visitor's local time).
- **What happens:** Wall-E sits by a small fire in his corner, with a quiet line `[TODO: Bunny]`. Clicking the fire opens the chat as usual.

### E3. Wanted level
- **Trigger:** passive. Chaotic behaviour: rapid clicking, mashing wrong cheat codes, very fast scrolling.
- **What happens:** stars light up in the top corner, one per burst of chaos, up to 5. Staying calm for a few seconds fades them out one by one. Reaching 5 unlocks the achievement.
- **Note:** purely visual; never blocks anything.

### E4. Mission complete
- **Trigger:** passive. Reaching the contact form, finishing a case file (scrolling to its end), or playing a replay to the end.
- **What happens:** a bold toast in our own wording `[TODO: Bunny]` (not the game's exact phrase), shown once per mission.

### E5. Mechanical map
- **Trigger:** cheat word, or long-press the KP logo.
- **What happens:** the page folds down into a flat map; the site's sections rise out of it like clockwork towers (Agents, Cases, Skills, Logs, About, Contact), each labelled. Clicking a tower goes to that page. Our own map of the site, not the show's.
- **Reduced motion:** a static map with the same links.

### E6. Frost and the wall
- **Trigger:** cheat word `[TODO: Bunny]`.
- **What happens:** frost creeps in from the page edges (SVG crystal patterns), and an ice wall grows at the footer. Wall-E shivers. Esc thaws it.
- **Reduced motion:** frost appears in place, no creep.

### E7. Raven post
- **Trigger:** passive, once the egg set is loaded. Sending the contact form successfully.
- **What happens:** after the normal success message, a bird flies off with a small rolled letter. The real form behaviour does not change.

### E8. Houses of the stack
- **Trigger:** cheat word, or click the Skills page heading three times.
- **What happens:** the skills groups become noble houses: each gets a banner with a sigil and a motto. Sigils and mottos `[TODO: Bunny]`.
- **Note:** only real skills; no invented ones.

---

## 6. Shared UI pieces
- **Back to normal pill:** fixed, bottom centre, appears with any active layer.
- **Subtitles:** Wall-E's lines, bottom centre, `aria-live="polite"`, max two lines.
- **Code prompt:** small terminal-style input opened from the footer glyph. Wrong code: Wall-E shakes his head.
- **Achievement toast:** small card top right, "Secret found: [name]", plus the counter.
- **Achievements panel:** opened from the counter. Lists found secrets and locked ones as "???", with one vague hint each `[TODO: Bunny]`.
- **Console note:** printed once by `core.js` `[TODO: Bunny]` wording.

---

## 7. Content Bunny needs to write or approve
1. Cheat word for each layer (our own words, not real game cheats).
2. All of Wall-E's lines (compactor, malfunction, DJ intros, sleep, chase, wrong code).
3. Achievement names and their hints.
4. Radio station names.
5. The console note.
6. The `secrets` chat answer.
7. "Previously on" wording.
8. `hours_spent` per project (real numbers only, or leave empty).
9. Real `CaseIncident` entries for the bounty board, if more are wanted.
10. Director's cut scene captions.
11. Where the black hole's dot hides, and whether the black hole chains into the director's cut.
12. The sandworm drum rhythm.
13. Dead-eye key, campfire hours, mission complete wording, frost cheat word.
14. Sigils and mottos for each tech-stack house.

---

## 8. Rule and document updates (before any code)
- **`CLAUDE.md`:** add an exception: "Heavy animation is allowed only inside opt-in madness layers, never on the default site." Add that madness CSS lives in `static/madness/madness.css`, loaded on demand.
- **`DECISIONS.md`:** "Madness layer is opt-in and hidden: the recruiter site stays clean and fast, and the creative side becomes something visitors discover."
- **`docs/REDESIGN_PLAN.md`:** add Phase 9 pointing to this file.
- **`TASKS.md` and `PROGRESS.md`:** Phase 9 tasks and log entries per sub-phase.

---

## 9. Build order (sub-phases, stop after each for review)

### 9.0 Foundations
- `madness_enabled` and `hours_spent` fields plus admin, one migration.
- `core.js`: registry, triggers (keys, code prompt, long-press, hidden spots), Esc and pill, storage, lazy loader, subtitles, achievements store.
- `madness.css` shared UI. Console note.
- Rule and document updates from section 8.
- **Acceptance:** with nothing triggered, the site is pixel-identical and only `core.js` is added. Turning the setting off removes it. Tests pass.

### 9.1 Compactor and inversion (the two proven ideas)
- L1 and L2 at full detail, including reduced motion and phone versions.
- **Acceptance:** both restore the page perfectly from every state, work by keyboard and by touch, and pass the QA list in section 10.

### 9.2 Personality
- L3 self-aware Wall-E, L4 previously on, L5 eaten 404.
- **Acceptance:** 404 renders with `DEBUG=False`; reactions fire at most once per page; nothing leaves the browser.

### 9.3 Data layers
- `/api/madness/data/` endpoint, L6 bounty board, L7 radio logs, `secrets` chat answer with "Try it" buttons.
- **Acceptance:** empty data shows honest empty states; endpoint 404s when disabled.

### 9.4 Big effects
- L8 drop zone, L9 desert night, L10 time dilation.
- **Acceptance:** stays within the performance budget; pauses when the tab is hidden.

### 9.5 Small eggs and the sandworm
- E1 to E8 in `eggs.js`, L13 sandworm.
- **Acceptance:** each egg unlocks its achievement once; drumming detection ignores normal clicks on links and buttons.

### 9.6 Black hole
- L12: shader, content motion, restore, fallbacks.
- **Acceptance:** 60 fps on a mid-range laptop, no WebGL errors, still-image fallback works with WebGL disabled, full restore from any moment of the animation.

### 9.7 Rewards
- Achievements panel and toasts, L11 director's cut, the black hole chain (if chosen).
- **Acceptance:** director's cut unlocks only after all others; can be exited from any scene.

### 9.8 Polish and launch checks
- Full QA pass, copy review with Bunny, performance check, then Bunny deploys.

---

## 10. Testing

### Django tests (`portfolio/tests.py`)
- Core script included only when `madness_enabled` is on.
- No layer script or `madness.css` is referenced in any default page HTML.
- `/api/madness/data/`: correct shape, only public fields, 404 when disabled.
- `404.html` renders with `DEBUG=False` and contains the home, projects and contact links.
- `hours_spent` optional; dilation data excludes empty ones.
- `secrets` chat answer is matched by its keywords.

### Manual QA checklist (each layer)
- Triggers by keyboard, by code prompt, and by touch.
- Esc and the pill restore everything; reload during a layer leaves no residue.
- Reduced motion shows the still version.
- Chrome, Firefox, Safari (or WebKit), and a real phone.
- No console errors; no timers running after exit (check in dev tools).
- Screen reader announces subtitles and the pill.
- Normal-mode page weight and Lighthouse score unchanged apart from `core.js`.

---

## 11. Risks and how we handle them
- **Recruiters hit an effect by accident:** triggers need a deliberate action (a typed word, a long press), and Esc is always shown.
- **Effects break the page:** the restore contract plus a reload-safe design (no state kept in the DOM after reload).
- **Copyright:** inspiration only; our own words, shapes and codes.
- **Scope creep:** each sub-phase ships alone and stops for review.
- **Mobile performance:** reduced counts on phones, capped animations, everything paused when hidden.
- **Black hole on weak devices:** capability check before starting (WebGL support, frame time in the first second); fall back to the still image automatically.
- **Sandworm drumming by accident:** the rhythm must be steady and on empty space only; clicks on links, buttons and text never count.
