/*
 * Recorded replay player (Phase 4).
 * Plays back validated steps ({t, actor, kind, text}) like a terminal.
 * All text is inserted with textContent, never innerHTML.
 * With prefers-reduced-motion, every step is shown at once and nothing animates.
 */
(function () {
    'use strict';

    const KINDS = ['info', 'tool_call', 'result', 'error'];
    const MS_PER_CHAR = 14;
    const MAX_TYPE_MS = 700;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    function formatTime(seconds) {
        const total = Math.max(0, Math.floor(seconds));
        const m = String(Math.floor(total / 60)).padStart(2, '0');
        const s = String(total % 60).padStart(2, '0');
        return `${m}:${s}`;
    }

    function makeLine(step) {
        const kind = KINDS.includes(step.kind) ? step.kind : 'info';
        const li = document.createElement('li');
        li.className = `replay-line replay-line--${kind}`;
        const actor = document.createElement('span');
        actor.className = 'replay-line__actor';
        actor.textContent = String(step.actor);
        const text = document.createElement('span');
        text.className = 'replay-line__text';
        li.append(actor, text);
        return { li, text, full: String(step.text) };
    }

    function setupPlayer(root) {
        const replays = Array.from(root.querySelectorAll('script[type="application/json"][id^="replay-data-"]'))
            .map(node => {
                try { return JSON.parse(node.textContent); } catch (error) { return null; }
            })
            .filter(data => data && Array.isArray(data.steps) && data.steps.length);
        if (!replays.length) return;

        const consoleEl = root.querySelector('[data-replay-console]');
        const titleEl = root.querySelector('[data-replay-title]');
        const metaEl = root.querySelector('[data-replay-meta]');
        const controls = root.querySelector('[data-replay-controls]');
        const playBtn = root.querySelector('[data-replay-play]');
        const restartBtn = root.querySelector('[data-replay-restart]');
        const speedBtn = root.querySelector('[data-replay-speed]');
        const progressWrap = root.querySelector('[data-replay-progress-wrap]');
        const progress = root.querySelector('[data-replay-progress]');
        const tabs = Array.from(root.querySelectorAll('[data-replay-index]'));

        const state = {
            replay: replays[0],
            elapsed: 0,
            next: 0,
            playing: false,
            speed: 1,
            typing: [],
            lastFrame: 0,
            frame: 0,
        };

        function duration() {
            const last = state.replay.steps[state.replay.steps.length - 1].t;
            return Math.max(Number(state.replay.duration_s) || 0, last, 0.001);
        }

        function updateProgress() {
            const pct = Math.min(100, (state.elapsed / duration()) * 100);
            progress.style.width = `${pct}%`;
            progress.setAttribute('aria-valuenow', String(Math.round(pct)));
            progress.setAttribute('aria-valuetext', `${formatTime(state.elapsed)} of ${formatTime(duration())}`);
        }

        function setPlayLabel() {
            const finished = state.next >= state.replay.steps.length && !state.typing.length;
            const label = state.playing ? 'Pause' : (finished ? 'Replay' : (state.elapsed > 0 ? 'Resume' : 'Play'));
            playBtn.textContent = label;
            playBtn.setAttribute('aria-label', label);
        }

        function showAll() {
            consoleEl.replaceChildren();
            state.replay.steps.forEach(step => {
                const line = makeLine(step);
                line.text.textContent = line.full;
                consoleEl.append(line.li);
            });
            state.next = state.replay.steps.length;
            state.typing = [];
            state.elapsed = duration();
            updateProgress();
        }

        function reset() {
            cancelAnimationFrame(state.frame);
            state.playing = false;
            state.elapsed = 0;
            state.next = 0;
            state.typing = [];
            consoleEl.replaceChildren();
            const hint = document.createElement('li');
            hint.className = 'replay-line replay-line--hint';
            hint.textContent = `Recorded run, ${state.replay.steps.length} steps, ${formatTime(duration())}. Press play.`;
            consoleEl.append(hint);
            updateProgress();
            setPlayLabel();
        }

        function load(index) {
            state.replay = replays[index] || replays[0];
            titleEl.textContent = state.replay.title;
            metaEl.textContent = `${state.replay.project} · ${formatTime(duration())}`;
            tabs.forEach((tab, i) => tab.setAttribute('aria-selected', String(i === index)));
            if (reduceMotion.matches) {
                showAll();
            } else {
                reset();
            }
        }

        function tick(now) {
            // Cap the step so a backgrounded tab doesn't dump every remaining line on return.
            const dt = state.lastFrame ? Math.min((now - state.lastFrame) / 1000, 0.25) : 0;
            state.lastFrame = now;
            state.elapsed = Math.min(duration(), state.elapsed + dt * state.speed);

            const steps = state.replay.steps;
            while (state.next < steps.length && steps[state.next].t <= state.elapsed) {
                if (state.next === 0) consoleEl.replaceChildren();
                const line = makeLine(steps[state.next]);
                line.started = now;
                line.typeMs = Math.min(MAX_TYPE_MS, line.full.length * MS_PER_CHAR);
                consoleEl.append(line.li);
                state.typing.push(line);
                state.next += 1;
            }

            state.typing = state.typing.filter(line => {
                const done = (now - line.started) * state.speed >= line.typeMs;
                const chars = done ? line.full.length : Math.ceil(((now - line.started) * state.speed / line.typeMs) * line.full.length);
                line.text.textContent = line.full.slice(0, chars);
                return !done;
            });

            consoleEl.scrollTop = consoleEl.scrollHeight;
            updateProgress();

            const finished = state.next >= steps.length && !state.typing.length;
            if (finished) {
                state.playing = false;
                state.elapsed = duration();
                updateProgress();
                setPlayLabel();
                return;
            }
            state.frame = requestAnimationFrame(tick);
        }

        function play() {
            if (state.next >= state.replay.steps.length && !state.typing.length) reset();
            state.playing = true;
            state.lastFrame = 0;
            setPlayLabel();
            state.frame = requestAnimationFrame(tick);
        }

        function pause() {
            state.playing = false;
            cancelAnimationFrame(state.frame);
            setPlayLabel();
        }

        playBtn.addEventListener('click', () => (state.playing ? pause() : play()));
        restartBtn.addEventListener('click', () => { reset(); play(); });
        speedBtn.addEventListener('click', () => {
            state.speed = state.speed === 1 ? 2 : 1;
            speedBtn.textContent = `${state.speed}x`;
            speedBtn.setAttribute('aria-label', `Playback speed ${state.speed}x`);
        });
        tabs.forEach((tab, index) => tab.addEventListener('click', () => { pause(); load(index); }));

        function applyMotionPreference() {
            const reduced = reduceMotion.matches;
            controls.hidden = reduced;
            progressWrap.hidden = reduced;
            pause();
            load(Math.max(0, tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true')));
        }

        if (reduceMotion.addEventListener) {
            reduceMotion.addEventListener('change', applyMotionPreference);
        }
        applyMotionPreference();
    }

    document.querySelectorAll('[data-replay-player]').forEach(setupPlayer);
})();
