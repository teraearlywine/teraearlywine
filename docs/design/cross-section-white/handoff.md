# Cross Section website review

The Mac preview uses the website’s Flask templates, local artwork and local fonts. The booking button opens Tera’s existing Google appointment page. Form submissions exercise the local delivery service with simulated email and Linear destinations.

## Review on Tera’s Mac

- Open the [homepage](http://127.0.0.1:5413/) and try Source, Rule and Check. Switch the refund off and on to compare $600 with $560.
- Move the pointer over Tera’s name in the header, or tab to the home link. The blue offcut slides into the T while the wordmark stays in place. Reduce Motion shows the assembled mark and its orange seam.
- Read the [migration service](http://127.0.0.1:5413/services/data-migration-rescue) and follow its inquiry link. Choose **Help me scope it** and submit a test message.
- Open [Writing](http://127.0.0.1:5413/blog/) and move the mouse onto the stack. Watch the orange edge and essay title change together. Move to **Read essay** to open that selection, or use **Newer** to return to the top sheet. Browse the complete archive or copy the feed address on the [subscription page](http://127.0.0.1:5413/blog/subscribe/).
- Read [Nothing Wasted](http://127.0.0.1:5413/blog/nothing-wasted/) through the last paragraph. The blue offcut slides into the T and settles above the offer. With Reduce Motion enabled, the finished mark appears immediately.

[Desktop homepage capture](home-desktop.png)

To restart the preview, start the [local contact broker and Firestore emulator](../../contact-spam.md) for form delivery. From the website root, use its Python environment and run `PYTHONPATH=. python docs/design/cross-section-white/preview.py`. All reading and booking links work independently of the local delivery service.

## Checks on the Mac, November 12, 2026

- Compared the live sitemap and RSS feed against the redesign. All 36 sitemap paths, the 30 feed identities and their order match. Checked the subscription page, 50 linked fragment targets, the legacy About redirect, social metadata and locally served artwork.
- The 222 Python and 11 JavaScript checks cover the local broker integration, brand motion, stack selection and the opt-in browser test for the current Google analytics library. The latter intercepted its measurement requests.
- Browser checks covered 320, 390 and 1440 pixels, navigation by keyboard, all 30 sheets, the JavaScript-free archive and form, reduced motion and failed video playback. The booking link resolved to the existing Google appointment page.
- Standard and unspecified inquiries exercised the signed local delivery path. A retry produced one email and one Linear operation in the test destinations. A rejected submission produced neither. The consented booking event and successful inquiry event were distinct.

## Release after Tera approves the reviewed revision

1. Record the approved commit and run the full suites on that revision. Save the current App Engine allocation **at deployment time** with `gcloud app services describe default --project=teraearlywine --format='json(split)'`. Keep the allocation weights, split method and serving versions available through the rollout.
2. Give the approved commit a fresh App Engine version ID and deploy `app.yaml` with `--project=teraearlywine --version=<new-version> --no-promote --no-stop-previous-version`. Verify that the saved public traffic allocation still applies.
3. On the new version’s URL, check the homepage, all four services, the 30 essay paths, the archive, RSS, subscription and errors. Fetch the versioned hero, social card, fonts, logo and MP4. Check the mobile example, paper controls, sign-off, consent and booking link. Canonical and feed identities on the hosted version should point to the public domain.
4. Shift the default service to the reviewed version with `gcloud app services set-traffic default --project=teraearlywine --splits=<new-version>=1`. Verify the service allocation and visit the public domain to confirm the new headline, working visitor journeys, signature and media. Review App Engine errors and contact broker delivery outcomes, including email and Linear completion status.
5. If a critical journey fails, restore the saved weights and split method using `gcloud app services set-traffic default --project=teraearlywine --splits=<saved-allocations> --split-by=<saved-method>`. Check the restored allocation, public routes and delivery health. Record the deployed version, final allocation and observed results.
