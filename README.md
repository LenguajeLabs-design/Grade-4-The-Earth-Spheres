# Earth Explorers - Grade 4

One master website for the Biosphere, Hydrosphere, Geosphere and Atmosphere unit. Designed for GitHub Pages, using the four-section structure of the Grade 5 Space Explorer readers.

## Student experience

- Choose a sphere from the home page.
- Follow Discover, Explore, Connect and Your mission.
- Keep the English visible and reveal Japanese, Korean or Simplified Chinese after each paragraph.
- Listen to an English paragraph, a translation, or a whole section. Included narration covers all four languages. Pause, resume, stop, change the reading speed, or choose an optional device voice.
- Use the illustrated vocabulary, questions and sentence frames.
- Open Reading settings for speed, text size, translation display, printing and voice choices. Pause and Stop appear in the compact toolbar during playback.

All illustrations and narration are stored with the site. No sign-in, translation service, application server, API key, paid speech service or build framework is required. Included synthetic narration uses Samantha (English), Kyoko (Japanese), Yuna (Korean) and Tingting (Chinese). Whole-paragraph clips keep the flow of each passage. Device/browser speech is an optional alternative and a fallback if a clip cannot load.

## Publish on GitHub Pages

In this repository, open **Settings > Pages**. Choose **Deploy from a branch**, select **main** and **/(root)**, then **Save**.

The project URL is:

https://lenguajelabs-design.github.io/Grade-4-The-Earth-Spheres/

The URL becomes available after GitHub finishes its Pages deployment. All paths are relative so they also work under the repository's project URL. The `.nojekyll` file keeps the static files unchanged.

## Edit or rebuild

The complete English and translated content lives in `content/`, one JSON file per sphere. Shared behavior and appearance live in `app.js` and `styles.css`.

The rendered HTML is committed, so GitHub Pages needs no build command. To regenerate it after editing JSON:

```sh
python3 tools/apply_book_layout.py
python3 tools/check_site.py
```

Use `apply_book_layout.py` as the build entry point to preserve the Grade 5-style four-section layout. It also updates the home page and credits. The generator uses Python's standard library only. It does not require the original PDFs or anything outside this repository.

For local preview:

```sh
python3 -m http.server 8764
```

Narration is already included. After changing spoken content, regenerate clips on macOS with these four voices installed using `python3 tools/build_narration.py`, then rebuild the HTML. This optional step uses macOS speech and audio services. Other platforms can serve and edit the website without regenerating audio. The narration manifest maps the exact text to each clip.

## Content and images

The classroom reader illustrations are identified as illustrations. These are not documentary photographs. Read `credits.html` for science sources and language/audio notes. Selected Japanese science terms have readings in parentheses. Translations have not had an independent native-speaker review.

Reading preferences are stored only in the browser. No student answers or personal information are collected by this site. Hosting and device speech services have their own policies.

## Geosphere extension

`earthquakes-volcanoes.html` adds a reading-only extension designed to support Grade 4 learners working around WIDA 2–3. It includes nine short passages with Japanese, Korean and Simplified Chinese translations, a volcano cross-section, earthquake sequencing, vocabulary, questions and sentence frames. No audio files are added. Edit `content/earthquakes-volcanoes.json` and rebuild with the normal entry point. `tools/build_geosphere_extension.py` generates the extension; `extension.js` handles language and reading preferences. The Geosphere reader links to it from its cover and volcano topic.
