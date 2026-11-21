# MainImage Pass: Launch Copy

Ready to paste. Everything below is based only on what the tool
verifiably does today (verified end to end on 18 Nov 2026 and again on
21 Nov 2026, see test-evidence/). Replace https://mainimagepass.site with the real
public URL from DEPLOY.md Step 1 before using any of it.

What the tool does, and nothing more:
- Accepts up to 10 JPG or PNG photos per listing.
- Removes the background and composites the product on pure white,
  RGB 255,255,255.
- Outputs a 2000x2000 JPG with the product centered at about 85
  percent frame fill.
- Produces a per-image preflight report with a PASS or FAIL for each
  technical check: output resolution, background purity (sampled at
  the image edges), JPEG format, frame fill, and source resolution
  warnings (a source under 500px fails, under 2000px warns).
- Delivers one ZIP containing the processed images and the report.
- Honest limits, stated everywhere on purpose: the checks cover the
  technical main-image rules only. Content rules (no text, no props,
  no lifestyle elements, no watermarks) cannot be checked
  automatically and stay the seller's responsibility. Edge quality on
  complex products (fur, glass, reflective surfaces) can be weaker.

## 1. Creem products

### Product 1: MainImage Pass Single: 1 Listing (10 Photos), $19 one-time

MainImage Pass Single fixes the main images of one Amazon listing.
Upload up to 10 raw product photos (JPG or PNG) and get back a ZIP
with Amazon main-image ready versions of every photo: background
removed, composited on pure white (RGB 255,255,255), resized to
2000x2000, product centered in the frame. Every photo also gets a
preflight report with a PASS or FAIL for each technical main-image
check, so you can see exactly what was verified before you upload to
Amazon. One-time payment, no subscription. The report covers
technical rules only; content rules such as no text or props in the
main image remain your responsibility as the seller.

### Product 2: MainImage Pass Bundle: 5 Listings, $49 one-time

MainImage Pass Bundle covers five Amazon listings, up to 10 photos
per listing. Each listing gets the same treatment: background removal
to pure white (RGB 255,255,255), 2000x2000 output, product centered,
and a per-image PASS/FAIL preflight report covering output
resolution, background purity, file format, frame fill, and source
resolution warnings. Results are delivered as one ZIP per listing,
with the processed images and the report inside. One-time payment,
no subscription. Built for sellers fixing a small catalog or
relaunching suppressed listings. Technical checks only; content
rules stay the seller's responsibility.

### Product 3: MainImage Pass Agency: 20 Listings, $99 one-time

MainImage Pass Agency covers twenty Amazon listings, up to 10 photos
per listing, for agencies and high-volume sellers. Every photo is
processed the same way: background removed, composited on pure white
(RGB 255,255,255), output at 2000x2000 with the product centered,
plus a per-image PASS/FAIL preflight report so each listing can be
checked before it goes back to Amazon. Delivery is one ZIP per
listing with the processed images and the report. One-time payment,
no subscription. The report verifies technical main-image rules
only; content rules such as no text, props, or lifestyle elements
remain the seller's responsibility.

### Product 4: MainImage Pass Done-For-You: 1 Listing, $49 one-time

Live Creem product ID: prod_4X0VGq2B2VONjU27C5Apwc
Payment link: https://www.creem.io/payment/prod_4X0VGq2B2VONjU27C5Apwc

We do it for you. Send us the raw photos for one Amazon listing and a
human checks every output by hand: a compliant main image on pure
white (RGB 255,255,255), 2000x2000 JPEG, product centered, plus the
full PASS/FAIL preflight report. Delivered by email as a ZIP within
24 hours of receiving your photos. After checkout, email your photos
to hello@mainimagepass.site from the same email you used to pay,
with your product name in the subject. One-time payment, no
subscription. Technical checks only; content rules stay the seller's
responsibility.

### Product 5: MainImage Pass Done-For-You: 5 Listings, $199 one-time

Live Creem product ID: prod_3kRtSFmx6XZYttejho0Ks9
Payment link: https://www.creem.io/payment/prod_3kRtSFmx6XZYttejho0Ks9

We do it for you, five listings. Send us the raw photos for five
Amazon listings and a human checks every output by hand: compliant
main images on pure white (RGB 255,255,255), 2000x2000 JPEG, product
centered, plus a PASS/FAIL preflight report for every photo.
Delivered by email as a ZIP within 24 hours of receiving your
photos. After checkout, email your photos to
hello@mainimagepass.site from the same email you used to pay, with
your product names in the subject. One-time payment, no
subscription. Technical checks only; content rules stay the seller's
responsibility.

## 2. TrustMRR startup listing

Name: MainImage Pass

Tagline: Turn raw product photos into Amazon main-image compliant
images, with a PASS/FAIL preflight report for every photo.

Description: MainImage Pass is a web tool for Amazon sellers whose
listings are held back by main-image rule violations. A seller
uploads up to 10 raw product photos per listing and receives a ZIP
with compliant versions: background removed and composited on pure
white (RGB 255,255,255), 2000x2000 output, product centered in the
frame, plus a per-image preflight report that marks each technical
check PASS or FAIL (resolution, background purity, JPEG format,
frame fill, source resolution). Pricing is one-time: $19 for 1
listing, $49 for 5 listings, $99 for 20 listings. Built solo in
November 2026 for the Ship or Die $100K Hackathon.

Website: https://mainimagepass.site

## 3. X launch post (280 characters max)

Post this text, with https://mainimagepass.site replaced by the real URL:

Amazon main image got your listing suppressed? MainImage Pass turns raw product photos into compliant main images: pure white background (RGB 255,255,255), 2000px, plus a PASS/FAIL report for every photo. One-time price. https://mainimagepass.site

## 4. Community post for Amazon seller groups (case-study format)

Post title: I built a preflight checker for Amazon main images,
here is what it found on a test photo

Post body:

Hi all, I am a solo developer and I built a small tool after reading
one too many main-image suppression threads. Posting it here as a
worked example, not a sales pitch, and I would genuinely like to
know if the checks match what you see in Seller Central.

The problem it targets: a main image that breaks the technical rules
(non-white background, too small, wrong format) can get a listing
suppressed, and the fix has to be right the first time.

What the tool does with each photo:
1. Removes the background and composites the product on pure white,
   RGB 255,255,255.
2. Rebuilds the image at 2000x2000 with the product centered at
   about 85 percent of the frame.
3. Runs a preflight report and marks every check PASS or FAIL:
   output resolution, background purity sampled at the edges, JPEG
   format, frame fill, and source resolution (under 500px fails,
   under 2000px warns).
4. Returns a ZIP with the processed images and the report.

Worked example, from my own test files, not a customer: I ran a
product photo shot on a beige background through it. The output came
back at 2000x2000, all four corners sampled at pure white
(255,255,255), and the report marked the image PASS with the
background method and every check listed. That is the whole flow, it
takes one upload.

What it does not do, honestly: it checks technical rules only. It
cannot judge content rules (text on the product, props, lifestyle
elements, watermarks), so that part is still on us as sellers. Edge
quality on fur, glass, or reflective products can also be weaker
than a manual edit.

Pricing, so nobody has to ask: one-time, $19 for 1 listing (10
photos), $49 for 5 listings, $99 for 20 listings. No subscription.

If you have a suppressed listing right now, I am happy to run one
photo through it and show you the report, free, in the replies.
Feedback on the check list is welcome either way: what would you
want a preflight report to catch before you re-upload?

Tool: https://mainimagepass.site
