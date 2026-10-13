# DECISIONS

One line each: decision, then why. Details in `docs/REDESIGN_PLAN.md`.

- **Multi-page structure:** the homepage is the 30-second view and project pages carry the depth, so recruiters skim fast and can still dig in.
- **Ops console + case file theme:** one coherent visual language replaces three clashing styles (luxury serif, terminal mono, pixel robot) and fits agentic/security work.
- **Rule-based chatbot, no LLM:** answers stay accurate, cheap and honest, with no hallucinated claims and no API cost on a free host.
- **Chatbot answers editable in admin:** Bunny can fix or add answers without a code change or deploy.
- **Robot parked, no roaming:** keeps the character without it covering text and project tags.
- **Replays from recorded logs, never live:** shows real agent runs safely, with no live execution, keys or cost on the site.
- **Experience and certifications split:** real roles were labelled "Credential" and mixed with certificates; separate models show each correctly.
- **No experience slugs for now:** with one real role, detail pages add little; revisit at 2 to 3 roles.
- **JD match deferred:** out of scope until the core site is rebuilt.
