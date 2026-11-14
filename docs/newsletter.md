# Publishing The Business of Technology

Readers sign up at [/newsletter/](https://www.teraearlywine.com/newsletter/) and choose *Choose Your Next AI Workflow*, *From Technical Work to Business Impact*, or both. Email confirmation activates the subscription. The existing RSS feed remains available for feed readers.

The site keeps confirmed readership and guide choices in the `teraearlywine` Datastore database. The stable `NEWSLETTER_IDENTITY_KEY` identifies repeat signups across sessions. Migrate subscriber IDs before changing that key. Pending confirmations expire after 24 hours. Database TTL removes expired pending records and temporary abuse counters.

## Newsletter measurement

The website sends these GA4 events when the visitor grants analytics consent. The event parameters contain fixed labels. Email addresses, subscriber identifiers, confirmation tokens, and unsubscribe tokens stay out of analytics.

| GA4 event | When it fires | Parameters |
| --- | --- | --- |
| `newsletter_cta_click` | A reader follows a newsletter or guide signup link. | `placement` and `guide` |
| `newsletter_guide_select` | A reader changes their guide selection on the signup form. | `guide` |
| `newsletter_signup` | The browser opens a receipt for an accepted signup request. | `guide` |
| `newsletter_confirm` | The browser opens the receipt for a newly confirmed subscription. | `guide` |
| `newsletter_guide_download` | A reader selects a PDF on the guide download page. | `guide` |
| `newsletter_unsubscribe` | A reader completes a browser unsubscribe and opens its receipt. | None |
| `navigation_click` | A reader chooses the archive or RSS in the blog header, or reads a sample from signup. | `placement` and `destination_type` |

In a GA4 exploration, use **Event name** and **Event count** to follow requests through confirmation. Break down **Page path** and **placement** to compare homepage, blog, and audience-page invitations. Use the event-scoped **guide** dimension to compare `teams`, `professionals`, and `both`. The signup and confirm events include the submitted guide even when the reader keeps the default. A download counts a click on an individual PDF. Mailbox one-click unsubscribes have no browser event. Use the subscriber database for list totals, including readers who declined analytics.

Newsletter issue footer links use the fixed campaign `business_of_technology`, source `newsletter`, medium `email`, and content `issue`. In Traffic acquisition, filter by this campaign to see return visits.

## Preview an issue

From the website repository, install its Python requirements and write the issue body in a UTF-8 text file. Set `NEWSLETTER_FROM` to the verified sender configured for the public site. Supply your current business mailing address for the footer. The following command prints the complete plain-text email with a sample unsubscribe link. Previewing uses no account credentials and sends nothing.

```sh
python -m scripts.send_newsletter \
  --issue 2026-12-workflow-test \
  --subject 'How would we know this workflow helped?' \
  --body /path/to/issue.txt \
  --address "$BUSINESS_MAILING_ADDRESS" \
  --audience all
```

Use `--audience teams` or `--audience professionals` for an issue intended for readers who chose that guide. The default `all` sends one copy per confirmed reader. Readers who chose both guides can receive either segment’s issue.

## Send and resume

Use Google Application Default Credentials for the website project. The sending operator needs access to the subscriber database and the configured Resend secret. In the same shell, set the production environment and repeat the preview command with `--send`.

```sh
export GOOGLE_CLOUD_PROJECT=teraearlywine
export RESEND_API_KEY_SECRET_ID=NEWSLETTER_RESEND_API_KEY
export SITE_URL=https://www.teraearlywine.com
```

Use a unique issue ID for each new edition. The first send records the edition’s content fingerprint and start time. A rerun of that ID requires the same body, sender, subject, address, site, and audience. It skips readers already accepted by the provider and readers who confirmed after the edition started. The command checks current consent before each provider request. Each message has a reader-specific unsubscribe link in the body and matching one-click headers.

The issue footer also links to the Ideas archive with a shared campaign tag. GA4 can attribute consenting visits to source `newsletter`, medium `email`, campaign `business_of_technology`, and content `issue`. All readers receive the same archive URL. Provider acceptance, mailbox delivery, opens, and archive visits represent different events.

If delivery stops, rerun the identical command after the two-minute in-flight lease expires. Resend deduplicates identical requests for 24 hours. The script stops retrying an uncertain delivery after 23 hours to leave room for transport delays. A `needs review` count means the provider window expired or the individual payload changed. Look up the affected `NewsletterIssueDelivery` record by its stable edition and subscriber key, check provider delivery evidence, and reconcile that record before any further send. A provider receipt records acceptance for delivery. Mailbox delivery is a separate event. [Resend idempotency documentation](https://resend.com/docs/dashboard/emails/idempotency-keys)
