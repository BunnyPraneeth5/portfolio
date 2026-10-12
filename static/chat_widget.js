/*
 * Chat helper widget (Phase 5a). Rule-based backend at /api/chat/, no LLM.
 * The robot is parked in a corner; click / Enter / Space opens a console-style dialog,
 * Esc closes it and returns focus to the robot. All text is inserted with textContent.
 */
(function () {
    'use strict';

    var root = document.getElementById('pet-widget-root');
    if (!root) return;

    var robot = document.getElementById('petCat');
    var panel = document.getElementById('pet-chat-panel');
    var closeBtn = document.getElementById('pet-chat-close');
    var messages = document.getElementById('pet-chat-messages');
    var form = document.getElementById('pet-chat-form');
    var input = document.getElementById('pet-chat-input');
    var sendBtn = form.querySelector('.pet-chat-send');
    var SAFE_HREF = /^(\/(?!\/)|https?:\/\/|mailto:)/i;

    function readJson(id, fallback) {
        var node = document.getElementById(id);
        if (!node) return fallback;
        try { return JSON.parse(node.textContent); } catch (error) { return fallback; }
    }

    var greeting = readJson('pet-chat-greeting', '');
    var defaultChips = readJson('pet-chat-chips', []);
    var started = false;
    var pending = false;

    function scrollToEnd() {
        messages.scrollTop = messages.scrollHeight;
    }

    function appendUser(text) {
        var row = document.createElement('div');
        row.className = 'pet-chat-msg pet-chat-msg--user';
        row.textContent = text;
        messages.appendChild(row);
        scrollToEnd();
    }

    function appendBot(text, links, chips) {
        var row = document.createElement('div');
        row.className = 'pet-chat-msg pet-chat-msg--bot';

        var body = document.createElement('p');
        body.className = 'pet-chat-text';
        body.textContent = text;
        row.appendChild(body);

        var safeLinks = (links || []).filter(function (link) {
            return link && typeof link.url === 'string' && SAFE_HREF.test(link.url);
        });
        if (safeLinks.length) {
            var list = document.createElement('ul');
            list.className = 'pet-chat-links';
            safeLinks.forEach(function (link) {
                var item = document.createElement('li');
                var a = document.createElement('a');
                a.href = link.url;
                a.textContent = String(link.label || link.url);
                if (/^https?:\/\//i.test(link.url)) {
                    a.target = '_blank';
                    a.rel = 'noopener';
                }
                item.appendChild(a);
                list.appendChild(item);
            });
            row.appendChild(list);
        }

        if (chips && chips.length) {
            // Only the latest set of chips stays clickable.
            Array.prototype.forEach.call(messages.querySelectorAll('.pet-chat-chips'), function (old) {
                old.remove();
            });
            var chipRow = document.createElement('div');
            chipRow.className = 'pet-chat-chips';
            chips.forEach(function (chipText) {
                var chip = document.createElement('button');
                chip.type = 'button';
                chip.className = 'pet-chat-chip';
                chip.textContent = String(chipText);
                chip.addEventListener('click', function () { send(String(chipText)); });
                chipRow.appendChild(chip);
            });
            row.appendChild(chipRow);
        }

        messages.appendChild(row);
        scrollToEnd();
    }

    function setPending(state) {
        pending = state;
        input.disabled = state;
        sendBtn.disabled = state;
        panel.setAttribute('aria-busy', String(state));
    }

    function send(text) {
        text = (text || '').trim();
        if (!text || pending) return;
        appendUser(text);
        input.value = '';
        setPending(true);
        var tokenField = document.querySelector('#pet-csrf-form [name=csrfmiddlewaretoken]');
        fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': tokenField ? tokenField.value : '',
            },
            body: JSON.stringify({ message: text }),
            credentials: 'same-origin',
        })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                appendBot(data.reply || "Sorry, I didn't catch that.", data.links, data.chips);
            })
            .catch(function () {
                appendBot("Couldn't reach the server. Try again in a moment.", [], []);
            })
            .then(function () {
                setPending(false);
                input.focus();
            });
    }

    function open() {
        panel.hidden = false;
        robot.setAttribute('aria-expanded', 'true');
        root.classList.add('is-open');
        if (!started) {
            started = true;
            appendBot(greeting, [], defaultChips);
        }
        input.focus();
    }

    function close() {
        panel.hidden = true;
        robot.setAttribute('aria-expanded', 'false');
        root.classList.remove('is-open');
        robot.focus();
    }

    robot.addEventListener('click', function () {
        if (panel.hidden) { open(); } else { close(); }
    });
    closeBtn.addEventListener('click', close);
    panel.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            event.preventDefault();
            close();
        }
    });
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        send(input.value);
    });
})();
