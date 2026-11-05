# Put LiftPlan on your iPhone Home Screen — free, no Mac, no Apple account

Takes about five minutes. Everything happens in a web browser.

## 1. Create the repository (GitHub, free)

1. Go to <https://github.com/new> (sign in or create a free account).
2. Repository name: `liftplan`. Leave it **Public** (GitHub Pages is free only on public repos for personal accounts;
   the app contains no personal data — your workouts stay on your phone).
3. Click **Create repository**.

## 2. Upload the site files (two batches)

**Batch 1** — unzip `LiftPlan-upload-batch1.zip`, open the `batch1-app-and-images-A-L` folder.
1. On the empty-repo page click **uploading an existing file**.
2. Drag in everything inside that folder: the six app files **and** the `images` folder (128 photos, A–L).
3. Commit message: `batch 1` → **Commit changes**. Wait for the page to finish.

**Batch 2** — unzip `LiftPlan-upload-batch2.zip`, open the `batch2-images-M-Z` folder.
1. In the repo click **Add file → Upload files**.
2. Drag in the `images` folder from batch 2 (104 photos, M–Z). GitHub merges it into the existing `images/` folder.
3. Commit message: `batch 2` → **Commit changes**.

Check: the repo should show `index.html` plus five small files at the root and an `images` folder with 232 files.

## 3. Turn on GitHub Pages

1. In the repo: **Settings** (tab at top) → **Pages** (left sidebar).
2. Under *Build and deployment* → Source: **Deploy from a branch**. Branch: **main**, folder **/ (root)**. **Save**.
3. Wait a minute, refresh: the page shows your URL, `https://<your-username>.github.io/liftplan/`.

## 4. Install on the iPhone

1. Open that URL in **Safari** on your phone (must be Safari, not Chrome).
2. Tap the **Share** button → **Add to Home Screen** → **Add**.
3. Launch it from the icon. It opens full-screen with no browser chrome, works offline, and the
   **Add to Apple Calendar** export downloads a real `.ics` file: tap it → choose the calendar → done.

## Updating later

Edit or replace `index.html` in the repo (pencil icon on the file, or upload again) and commit. The phone picks up
the new version the next time the app is opened with a connection. Your data is untouched by updates.

## What's different from the preview inside Claude

- `.ics` download works (the Claude preview blocks downloads).
- Exercise photos load: real start/finish photos for 120 of the 121 exercises (Free Exercise DB, public domain), with
  step-by-step instructions on each exercise's page. Inside the Claude preview these fall back to the drawn tiles.
- Safari may clear the app's local data if the app isn't opened for several weeks. Use Settings → **Copy Backup**
  occasionally, or switch sync on (next step: Supabase) so the phone is a cache rather than the only copy.

## Next step when you're ready: shared gym-equipment data

The gym pages currently hold your own observations. The community layer in the requirements doc (confirmations
across users, "gyms near me with a belt squat", gym comparison) needs a small backend. The data model in the app
already matches `docs/gym-equipment-app-requirements.md`; a free Supabase project with three tables
(`gyms`, `equipment_types`, `gym_equipment_observations`) and the sync code is the next build.
