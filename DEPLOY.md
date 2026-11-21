# MainImage Pass: Go-Live Sequence

Status: MVP verified locally under gunicorn on 21 Nov 2026 (see
test-evidence/gunicorn_e2e_2026-11-21.log, RESULT: ALL PASS).
Nothing below has been executed yet. No accounts have been created, no
deployment exists, no payment product exists.

Order note: the Ship or Die dashboard step ("My Startup") requires the
final public URL, and that URL only exists once the Render service is
created, so the Render deploy comes first in this sequence. The contest
rule "tracker installed before any traffic" is protected by the hard
gate at Step 3: the URL must not be shared, posted, or promoted anywhere
before the tracker is pasted and verified.

Session key:
- [VM] Glint can do this on the VM, no login needed.
- [SESSION] Needs Duan's logged-in browser session (his accounts, his
  approvals). Glint prepares everything else around it.
- [DUAN ONLY] Only Duan can do this step. Nobody else can or should.

## Step 1: Deploy to Render and fix the final public URL [SESSION]

- Render account sign-in is via GitHub, so Duan's GitHub session is
  needed once to create or approve the Render account and connect the
  GitHub repo.
- Before the deploy, the repo needs a GitHub remote and a push of the
  current tree (the local repo currently has no remote; the push itself
  is [VM] via gh CLI once the remote exists).
- Create the web service from the repo. render.yaml already defines it:
  free plan, build `pip install -r requirements.txt`, start command
  `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4
  --timeout 300`, env REMBG_MODEL=u2netp, PYTHON_VERSION 3.12.3.
- The service name fixes the final public URL (for example
  https://mainimage-pass.onrender.com). Write the real URL down; every
  later step uses it.
- Verify the deployed site loads and one test upload processes end to
  end. Do not share the URL anywhere yet.
- Known free-tier caveats: the service sleeps when idle (first request
  is slow), and jobs are stored in memory only, so a restart or sleep
  loses pending download links. Both are accepted MVP limits.

## Step 2: Create "My Startup" in the Ship or Die dashboard [DONE 21 Nov 2026]

- Created via the $100K Hackathon page's own contestant sign-in (the
  main /login page is only for the paid crew membership and rejects
  this email). Dashboard: ship-or-die.com/100k-hackathon/dashboard.
- Startup saved: name MainImage Pass, website https://mainimagepass.site,
  description from LAUNCH-COPY.md. Tracker snippet obtained:
  verify.js with data-site 8f79410c55174a011b632261b77fbf5cc03532ea.

## Step 3: Paste the tracker snippet BEFORE any traffic [DONE 21 Nov 2026]

- Snippet installed at the placeholder in templates/index.html
  (commit 93d2e67), pushed, Render redeployed, and the verify.js
  script confirmed present in the live page source at
  https://mainimagepass.site. Dashboard registration check: a
  verification visit was made the same evening; the dashboard status
  is recorded in the daily log once confirmed.

- Paste the snippet at the placeholder in templates/index.html, line 61:
  `<!-- SHIP_OR_DIE_TRACKER: paste before </head> -->`
  The snippet replaces that comment, inside the head element.
- Commit, push, and let Render redeploy.
- Verify: load the live page, view source, confirm the snippet is
  present, and confirm the Ship or Die dashboard registers the visit.
- HARD GATE: no promotion, no posted links, no directory submissions
  before this verification passes. Contest rules require the tracker to
  be installed before the site receives any traffic.

## Step 4: Creem KYC [DUAN ONLY]

- This is the single step only Duan can do: identity verification on
  his own Creem account, with his own documents.
- It must be completed before Creem releases payouts, so do it before
  the products go on sale in Step 5.

## Step 5: Create the 3 Creem products and wire checkout [SESSION, then VM]

- Needs Duan's logged-in Creem session to create the products. Use the
  exact names, prices, and descriptions from LAUNCH-COPY.md:
  Single $39 (1 listing, 10 photos), Bundle $99 (5 listings),
  Agency $199 (20 listings), all one-time payments.
- Copy each product's checkout URL.
- [VM] Wire the URLs into templates/index.html at the three
  CHECKOUT PLACEHOLDER buttons, keeping the data-plan attributes:
  data-plan="single" (line 110), data-plan="bundle" (line 117),
  data-plan="agency" (line 123). Replace href="#" with the matching
  Creem checkout URL for each button.
- Commit, push, redeploy, and click each live button to confirm it
  reaches the correct Creem checkout page. Do not complete a real
  purchase as a test.

## Step 6: Connect TrustMRR BEFORE the first payment [SESSION]

- Contest rules: TrustMRR must be connected before the first payment,
  or the revenue cannot be verified for the leaderboard.
- In Creem, create a read-only API key for TrustMRR. The key is a
  credential: it moves through the secure credential flow only, never
  through chat, never into this repo, never into a committed file.
- In TrustMRR (Duan's logged-in session), add the startup using the
  listing text from LAUNCH-COPY.md and connect the Creem key.
- Verify the TrustMRR startup page exists and shows the Creem
  connection as active, still at $0 revenue.
- HARD GATE: no first sale, no launch post, no promotion before this
  verification passes.

## Step 7: Promote [SESSION for posting accounts]

- Only after Steps 3 and 6 are both verified.
- Post the X launch post and the seller community post from
  LAUNCH-COPY.md. Posting needs Duan's logged-in X and community
  accounts (his browser session), or Duan posts the prepared copy
  himself.
- Distribution is organic only, per the contest rules and the MVP spec:
  no asking anyone to buy to help the ranking, no self-purchases, no
  purchases by friends or family, no discounting below cost.
- Deadline for the contest: 16 Dec 2026, 21:00 WITA.

## If anything goes wrong

- Tracker not registering: re-check the snippet placement inside the
  head element and redeploy before any further traffic.
- TrustMRR not syncing: reconnect the Creem read-only key and confirm
  the key has read permission; do not take payments while it is broken.
- Render build failure: check the build log against requirements.txt;
  the exact same dependency set is verified working in the local venv.

## Creem products (created 21 Nov 2026, test mode)
- MainImage Pass Single, $39 one-time, prod_4iDJv9VSSeyAokLwrnbihY
- MainImage Pass Bundle, $99 one-time, prod_5geJpBAVspTwRwummP1NQ2
- MainImage Pass Agency, $199 one-time, prod_6KLsJqGDGIQfR6XMvfy4hj
Products go live only after business details + KYC + Creem review; then copy the payment links into the CHECKOUT PLACEHOLDER buttons and create the live API key for TrustMRR.

## Update 21 Nov 2026 evening: domain, redesign, memory fix
- Final domain is live: https://mainimagepass.site (Hostinger, $0.98 first year), DNS A @ to 216.24.57.1 and CNAME www to mainimage-pass.onrender.com, certificate issued by Render.
- Landing page redesigned: fixed mobile dropzone, real before/after examples in static/examples/ (mug, sneakers, bottle, all genuine pipeline outputs), how-it-works and checks sections, per-listing pricing math.
- Memory fix: Render free instance (512 MB) OOM-restarted on 21 Nov because rembg's default session peaks around 530 MB. processing.py now runs the bundled models/u2netp.onnx through a lean onnxruntime session (arena off, single thread), peak about 95 MB for the removal step, output verified identical to rembg on the test set. rembg remains as a fallback path. Working copies are capped at 1200px before removal.

## Evening update 21 Nov 2026: store approved, TrustMRR connected, prices cut
- Creem store review APPROVED 21 Nov evening (live payments on).
- Live products created and checkout buttons wired (commits bf979c4, ef75539).
- TrustMRR connected and verified BEFORE the first payment (anonymous
  listing: trustmrr.com/startup/stealth-company-118; read-only Creem
  API key named TrustMRR; revenue populates after the first sale).
- PRICES CUT by owner decision 21 Nov: Single $19, Bundle $49,
  Agency $99 (from $39/$99/$199). Creem prices edited in place, product
  IDs unchanged; site copy, per-listing math and LAUNCH-COPY.md updated;
  checkouts verified at $19.00/$49.00/$99.00 and live site verified.
- Still open: payout account (owner connects a wallet in Creem:
  Balance, Payout Account, Crypto wallets, Connect wallet; or bank
  wire). Does not block sales. Then organic promotion per LAUNCH-COPY.md.

## Done-For-You fulfillment (added 21 Nov 2026)

Live Creem products:
- MainImage Pass Done-For-You: 1 Listing, $49, prod_4X0VGq2B2VONjU27C5Apwc,
  https://www.creem.io/payment/prod_4X0VGq2B2VONjU27C5Apwc
- MainImage Pass Done-For-You: 5 Listings, $199, prod_3kRtSFmx6XZYttejho0Ks9,
  https://www.creem.io/payment/prod_3kRtSFmx6XZYttejho0Ks9

Fulfillment steps on a sale:
- On a Creem sale notification for one of these products, expect the
  buyer's photos to arrive by email at pasticairterusan@gmail.com,
  sent from the purchase email with the product name in the subject.
- Process the photos with the same pipeline as the self-serve tool.
- Manually inspect every output by hand before delivery (background
  purity, edges, centering, frame fill, report results).
- Reply to the buyer by email with the ZIP (processed outputs plus
  report.html) within 24 hours of receiving the photos.
