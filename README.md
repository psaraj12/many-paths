# Many Paths

A lightweight English–Tamil spiritual guide for GitHub Pages. It presents Hindu, Buddhist and other major perspectives without ranking one tradition above another.

## How this version works

- No backend, API, API key, database, login or build step
- No third-party JavaScript or remote fonts
- Answers come only from the local curated knowledge base
- Questions and conversation history stay in the visitor's browser
- Unanswered questions are stored locally so topics can be identified later
- A service worker makes the site available offline after its first successful visit

The included foundational topics are editorial drafts. Religious scholars and fluent Tamil reviewers should review them before a public claim of authority or completeness.

## Preview locally

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080/spiritual-companion/` if the server was started from the parent folder, or `http://localhost:8080/` if started inside this folder.

## Publish on GitHub Pages

1. Create a GitHub repository and copy these files into its root.
2. Commit and push the files.
3. Open **Settings → Pages** in the repository.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select the branch, choose `/ (root)`, and save.

No secrets or environment variables are needed.

## Add or revise an answer

Edit `knowledge-base.js`. Each entry contains bilingual titles, common question forms, search keywords, separate tradition perspectives, common ground, sources and a reflection. Do not merge traditions into an artificial consensus.

After changing files, increment `CACHE` in `sw.js` so returning visitors receive the new knowledge base.

## Retrieve unanswered topics during testing

Open the browser developer console and run:

```js
JSON.parse(localStorage.getItem("many-paths-unanswered") || "[]")
```

After reviewing and adding the missing topics, clear the list with:

```js
localStorage.removeItem("many-paths-unanswered")
```

## Limitation

This version does not generate new answers or understand every possible wording. It returns an editorially reviewed entry only when the local matching score is strong enough. This deliberate boundary keeps the site private, predictable and free to operate.
