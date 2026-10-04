# Bond Research — Candidate Securities

## Purpose
Document actual bond terms and their sources before replacing
the invented securities in Copilot's draft.

Simulation window: March 31–April 30, 2026.
Neither candidate is fully approved for inclusion yet.

## Data conventions
- Contractual terms require documentary evidence.
- Record ratings with agency, issue/entity scope, and date.
- Sector classifications are project-assigned.
- Prices, effective duration, and OAS will be simulated.
- Accrued interest and coupon cash will be calculated.
- Internal project IDs are not CUSIPs or ISINs.
- Assume no trades, defaults, or redemptions during the month.

## Candidate 1 — Celanese 6.500% due 2030

### Established contractual terms
- Internal ID: CELANESE_6.500_2030
- Legal issuer: Celanese US Holdings LLC
- Currency: USD
- Security: 6.500% Senior Notes due 2030
- Issuance date: March 14, 2025
- Maturity: April 15, 2030
- Annual coupon rate: 6.500%
- Payment frequency: semiannual
- Scheduled coupon dates: April 15 and October 15
- First coupon date: October 15, 2025
- Day-count basis: 360-day year comprising twelve 30-day months
- Minimum denomination: $2,000, then $1,000 increments
- CUSIP: 15089QAZ7
- ISIN: US15089QAZ72

### Call terms
- Before April 15, 2027:
  100% of principal plus Applicable Premium and accrued interest.
- Applicable Premium is the greater of:
  1. 1% of principal; or
  2. Present value of the April 15, 2027 call payment and
     remaining coupons through that date, excluding accrued
     interest, minus principal.
- Discount rate for that calculation:
  applicable Treasury Rate plus 50 basis points.
- Scheduled call prices:
  - April 15, 2027–April 14, 2028: 103.250%
  - April 15, 2028–April 14, 2029: 101.625%
  - April 15, 2029 onward: 100.000%
- Accrued interest is paid separately.
- This summary covers the provisions reviewed, not every
  possible redemption provision.

### Relevance to the monthly calculation
- A scheduled coupon falls on April 15, 2026.
- Track coupon cash and the reset of accrued interest together.
- Regular semiannual coupon per $100 face: $3.25.

### Sources
- Final prospectus:
  https://www.sec.gov/Archives/edgar/data/1314514/000162828025011759/a424b52025filingfinal-usd.htm
  Sections: offering summary; interest; optional redemption.
- Supplemental indenture:
  https://www.sec.gov/Archives/edgar/data/1306830/000130683025000105/ex423312510q.htm
  Section: Exhibit A-1, Form of 2030 Note.
- Issuance completion:
  https://www.sec.gov/Archives/edgar/data/1306830/000162828025012811/ce-20250314.htm

### Outstanding checks
- Dated issue-level credit rating.
- Evidence of outstanding status throughout the simulation window.
- Project sector classification: Materials/Chemicals, provisional.

## Candidate 2 — Magnolia 6.875% due 2032

### Established contractual terms
- Internal ID: MAGNOLIA_6.875_2032
- Legal co-issuers:
  Magnolia Oil & Gas Operating LLC;
  Magnolia Oil & Gas Finance Corp.
- Currency: USD
- Security: 6.875% Senior Unsecured Notes due 2032
- Issuance date: November 26, 2024
- Original issue size: $400 million
- Maturity: December 1, 2032
- Annual coupon rate: 6.875%
- Payment frequency: semiannual
- Scheduled coupon dates: June 1 and December 1
- First coupon date: June 1, 2025
- Non-business-day payment: next succeeding business day
- Record dates: May 15 and November 15
- Day-count basis: 360-day year comprising twelve 30-day months

### Identifier status
- Candidate ISIN reported by Cbonds: USU55641AB74
- Tranche designation: unconfirmed
- CUSIP: not established
- Identifier fields were blank in the reviewed indenture template.
- Do not label the Cbonds identifier as SEC-verified.

### Call terms
- Before December 1, 2027:
  100% of principal plus Applicable Premium and accrued interest.
- Applicable Premium definition: not yet extracted.
- Equity-funded call before December 1, 2027:
  up to 40% of the issue at 106.875%, plus accrued interest,
  subject to the remaining-balance and timing conditions.
- Tender-offer cleanup:
  following qualifying purchases of at least 90% of outstanding
  notes, remaining notes may be redeemed at the offer price,
  plus accrued interest not already included.
- Scheduled call-price table:
  - 2027: 103.438%
  - 2028: 101.719%
  - 2029 onward: 100.000%

### Source discrepancies
- Section 3.07(e) permits scheduled calls from December 1, 2027,
  but describes annual table periods as beginning June 1.
  Preserve this wording; schedule interpretation remains unresolved.
- Cbonds news reports November 12, 2024 as the issuance date.
  The SEC filing reports closing on November 26, 2024.
  Use the SEC closing date and retain the discrepancy.
- The 8-K equity-call summary contains a misleading 40% price.
  The indenture specifies 106.875%; 40% limits the amount redeemed.

### Relevance to the monthly calculation
- No scheduled coupon falls within April 2026.
- Assuming payments occurred as scheduled, accrued interest
  builds from December 1, 2025 at both snapshots.
- Regular semiannual coupon per $100 face: $3.4375.

### Sources
- Issuance 8-K:
  https://www.sec.gov/Archives/edgar/data/1698990/000110465924123076/tm2429486d1_8k.htm
- Attached Exhibit 4.1 indenture:
  accessed through Item 9.01 of the above 8-K.
  Sections reviewed: Exhibit A, Interest; Section 3.07.
  TODO: record the direct exhibit URL.
- Cbonds issue page:
  https://cbonds.com/bonds/1752039/

### Outstanding checks
- Check for subsequent rating actions through March 31, 2026.
- Evidence of outstanding status throughout the simulation window.
- Identifier tranche confirmation.
- Scheduled-call date discrepancy.
- Project sector classification: Energy, provisional.

## Excluded candidate
Magnolia 6.625% Senior Notes due August 15, 2034:
issued August 5, 2026, after the simulation window.
Exclude from March–April 2026 holdings.

### Dated rating evidence
- Agency: S&P Global Ratings
- Action date: August 14, 2025
- Issue rating: BB-, affirmed
- Applicable security: $400 million 6.875% senior unsecured
  notes due 2032
- Project rating bucket: BB
- Recovery rating: revised from 2 to 3; rounded recovery
  estimate of 65%
- Source:
  https://www.spglobal.com/ratings/en/regulatory/article/-/view/sourceId/101640363
- Status: verified at this date from the reviewed announcement;
  subsequent changes through March 31, 2026 remain unchecked.

  ### Outstanding-status evidence
- Q2 2026 Form 10-Q reports $400.0 million principal of
  the 2032 Senior Notes outstanding at June 30, 2026.
- This matches the original issue size.
- Supports outstanding status at June 30; April-specific
  principal activity has not been independently confirmed.
- Simulation assumption: no redemption or principal change
  during March 31–April 30, 2026.
- Source: [paste the current SEC filing URL here]

## Candidate 3 — Bath & Body Works 6.625% due 2030

### Established contractual terms
- Internal ID: BBW_6.625_2030
- Current legal issuer: Bath & Body Works, Inc.
- Original issuer name: L Brands, Inc.
- Name change effective: August 2, 2021
- Project sector: Consumer discretionary, project-assigned
- Currency: USD
- Security: Senior unsecured notes with subsidiary guarantees
- Issuance date: September 30, 2020
- Original issue size: $1 billion
- Annual coupon: 6.625%
- Maturity: October 1, 2030
- Coupon dates: April 1 and October 1
- First coupon: April 1, 2021
- Day-count basis: 360-day year comprising twelve 30-day months
- Regular coupon per $100 face: $3.3125
- Scheduled April 2026 coupon: April 1

### Call terms
Scheduled prices for twelve-month periods beginning October 1:
- 2025: 103.313%
- 2026: 102.208%
- 2027: 101.104%
- 2028 onward: 100.000%
Accrued interest is additional.
The bond is already within its scheduled-call period in April 2026.
Simulation assumption: no redemption during the month.

### Rating evidence
- As of January 31, 2026, the issuer reports:
  - S&P: BB+
  - Moody's: Ba2
  for senior unsecured debt with subsidiary guarantees.
- The filing includes the 2030 notes in this debt category.
- Evidence scope: debt-category rating, not a separately reviewed
  issue-specific agency announcement.
- Project rating bucket: BB.

### Outstanding-status evidence
- $844 million principal reported at January 31, 2026.
- April 2026 principal activity remains unchecked.
- Do not confuse principal with the $839 million net carrying value.

### Sources
Issuance, coupon schedule, call terms, and attached indenture:
https://investors.bbwinc.com/node/7306/html
Relevant sections: Item 1.01; Section 310, Computation of Interest.

Name change:
https://www.sec.gov/Archives/edgar/data/701985/000070198521000030/bbwi-20210731.htm

Debt balance, rating category, and guarantees:
https://www.sec.gov/Archives/edgar/data/701985/000070198526000008/bbwi-20260131.htm
Relevant sections: Long-term Debt; Credit Ratings;
Guarantor Summarized Financial Information.

### Outstanding checks
- CUSIP/ISIN.
- Rating changes between January 31 and March 31, 2026.
- Principal activity through April 30, 2026.

## Candidate 4 — Goodyear 5.250% due April 2031

### Established contractual terms
- Internal ID: GOODYEAR_5.250_APR2031
- Legal issuer: The Goodyear Tire & Rubber Company
- Project sector: Consumer discretionary, project-assigned
- Currency: USD
- Security: Senior unsecured notes with subsidiary guarantees
- Issuance / interest accrual start: April 6, 2021
- Original issue size: $550 million
- Annual coupon: 5.250%
- Maturity: April 30, 2031
- Coupon dates: April 30 and October 30
- First coupon: October 30, 2021
- Day-count basis: 360-day year comprising twelve 30-day months
- Regular coupon per $100 face: $2.625

### Call terms
- Before January 30, 2031:
  greater of principal or present value of remaining scheduled
  payments, discounted using Treasury Rate plus 50 basis points.
- On or after January 30, 2031: 100% of principal.
- Accrued interest is additional.
- Simulation assumption: no redemption during the month.

### Relevance to the monthly calculation
- Coupon falls on April 30, 2026, our ending snapshot date.
- Under the end-of-day convention, include the coupon in cash
  and reset accrued interest to zero.
- Distinguish this issue from Goodyear's separate 5.250% notes
  due July 2031.

### Outstanding-status evidence
- $550 million principal outstanding at December 31, 2025.
- April 2026 principal activity remains unchecked.

### Sources
Contractual terms:
https://www.sec.gov/Archives/edgar/data/42582/000119312521107057/d148655dex42.htm
Relevant section: Exhibit A, Form of Note; Interest;
Optional Redemption.

Outstanding balance and guarantees:
https://www.sec.gov/Archives/edgar/data/42582/000162828026006708/gt-20251231.htm
Relevant section: $550 million 5.25% Senior Notes due April 2031.

### Outstanding checks
- Dated issue/debt-category rating; analytical bucket not yet assigned.
- CUSIP/ISIN; reviewed note template has blank identifiers.
- Principal activity through April 30, 2026.

## Candidate 5 — United Rentals 5.250% due 2030

### Established contractual terms
- Internal ID: URNA_5.250_2030
- Legal issuer: United Rentals (North America), Inc.
- Project sector: Industrials, project-assigned
- Currency: USD
- Security: Senior unsecured notes with guarantees
- Issuance / accrual start: May 10, 2019
- Annual coupon: 5.250%
- Maturity: January 15, 2030
- Coupon dates: January 15 and July 15
- First coupon: January 15, 2020
- Record dates: January 1 and July 1
- Day-count basis: 360-day year comprising twelve 30-day months
- Minimum denomination: $2,000, then $1,000 increments
- Regular coupon per $100 face: $2.625
- No scheduled April 2026 coupon.

### Scheduled call prices
For twelve-month periods beginning January 15:
- 2025: 102.625%
- 2026: 101.750%
- 2027: 100.875%
- 2028 onward: 100.000%
Accrued interest is additional.
Simulation assumption: no redemption during April 2026.

### Rating evidence
- Corporate ratings as of January 26, 2026:
  S&P BB+; Moody's Ba1.
- These are corporate ratings, not verified issue ratings.
- Bond analytical rating bucket remains pending.

### Outstanding-status evidence
- Year-end 2025 debt table lists these notes at
  $747 million net carrying value.
- Net carrying value is not principal or market value.
- April 2026 principal activity remains unchecked.

### Sources
Contractual terms:
https://www.sec.gov/Archives/edgar/data/1067701/000110465919028631/a19-8813_4ex4d1.htm
Sections: 3.01; 3.10; Form of Security, redemption provisions.

Debt balance and corporate ratings:
https://www.sec.gov/Archives/edgar/data/1067701/000106770126000007/uri-20251231.htm

### Outstanding checks
- Dated issue/debt-category rating.
- CUSIP/ISIN.
- Principal activity through April 30, 2026.

## Candidate 6 — CCO Holdings 4.500% due 2030

### Established contractual terms
- Internal ID: CCO_4.500_2030
- Legal co-issuers:
  CCO Holdings, LLC;
  CCO Holdings Capital Corp.
- Corporate group: Charter Communications
- Project sector: Communications, project-assigned
- Currency: USD
- Security: Senior unsecured notes
- Initial issuance: February 18, 2020
- Annual base coupon: 4.500%
- Maturity: August 15, 2030
- Coupon dates: February 15 and August 15
- First coupon: August 15, 2020
- Record dates: February 1 and August 1
- Day-count basis: 360-day year comprising twelve 30-day months
- Regular base coupon per $100 face: $2.25
- No scheduled April 2026 coupon.
- Contract provides for potential registration-related
  special interest; applicability remains unchecked.
- Simulation assumption: no special interest.

### Scheduled call prices
For twelve-month periods beginning February 15:
- 2025: 102.250%
- 2026: 101.500%
- 2027: 100.750%
- 2028 onward: 100.000%
Accrued interest and applicable special interest are additional.
Simulation assumption: no redemption during April 2026.

### Outstanding-status evidence
- Year-end 2025 debt table lists $2.750 billion principal
  for the 4.500% notes due August 15, 2030.
- April 2026 principal activity remains unchecked.

### Sources
Contractual terms:
https://www.sec.gov/Archives/edgar/data/1091667/000110465920023531/tm206421d3_ex4-2.htm
Sections: 3.07; Exhibit A, Form of Note.

Debt balance:
https://www.sec.gov/Archives/edgar/data/1271833/000127183326000005/ccoh-20251231.htm

### Outstanding checks
- Dated issue/debt-category rating; analytical bucket pending.
- CUSIP/ISIN.
- Special-interest applicability.
- Principal activity through April 30, 2026.

## Candidate 7 — Cleveland-Cliffs 6.750% due 2030

### Established contractual terms
- Internal ID: CLF_6.750_2030
- Legal issuer: Cleveland-Cliffs Inc.
- Project sector: Materials, project-assigned
- Currency: USD
- Security: Senior unsecured notes with subsidiary guarantees
- Issuance date: April 14, 2023
- Original issue size: $750 million
- Annual coupon: 6.750%
- Maturity: April 15, 2030
- Coupon dates: April 15 and October 15
- First coupon: October 15, 2023
- Day-count basis: 360-day year comprising twelve 30-day months
- Regular coupon per $100 face: $3.375
- Scheduled April 2026 coupon: April 15

### Call terms
- Before April 15, 2026:
  100% of principal plus Applicable Premium and accrued interest.
- Equity-funded redemption before April 15, 2026:
  up to 35% at 106.750%, subject to contractual conditions.
- Scheduled call prices:
  - From April 15, 2026: 103.375%
  - From April 15, 2027: 101.688%
  - From April 15, 2028: 100.000%
- Accrued interest is additional.
- The scheduled-call period begins within our simulation month.
  This permits redemption; it does not establish that one occurred.
- Simulation assumption: no redemption during April 2026.

### Outstanding-status evidence
- Year-end 2025 debt table reports $750 million for this issue.
- April 2026 principal activity remains unchecked.

### Sources
Contractual terms:
https://www.sec.gov/Archives/edgar/data/764065/000076406523000129/clf-202363010xqex41.htm
Relevant sections: Exhibit A, Form of Note; Interest;
Section 5.07, Optional Redemption.

Debt balance and guarantees:
https://www.sec.gov/Archives/edgar/data/764065/000076406526000025/clf-20251231.htm
Relevant section: Note 8 — Debt and Credit Facilities.

### Outstanding checks
- Dated issue/debt-category rating; analytical bucket pending.
- CUSIP/ISIN.
- Principal activity through April 30, 2026.
- Applicability of any registration-related additional interest.

## Candidate 8 — Range Resources 4.750% due 2030

### Established contractual terms
- Internal ID: RANGE_4.750_2030
- Legal issuer: Range Resources Corporation
- Project sector: Energy, project-assigned
- Currency: USD
- Security: Senior unsecured notes with subsidiary guarantees
- Issuance / accrual start: February 1, 2022
- Original issue size: $500 million
- Annual coupon: 4.750%
- Maturity: February 15, 2030
- Coupon dates: February 15 and August 15
- First coupon: August 15, 2022
- Day-count basis: 360-day year comprising twelve 30-day months
- Regular coupon per $100 face: $2.375
- No scheduled April 2026 coupon.

### Scheduled call prices
For twelve-month periods beginning February 15:
- 2025: 102.375%
- 2026: 101.1875%
- 2027 onward: 100.000%
Accrued interest is additional.
Simulation assumption: no redemption during April 2026.

### Sources
Issuance and coupon schedule:
https://www.sec.gov/Archives/edgar/data/315852/000119312522024682/d301990d8k.htm
Relevant section: Item 1.01.

Day-count and call terms:
https://www.sec.gov/Archives/edgar/data/315852/000119312522024682/d301990dex41.htm
Relevant sections: 2.14, Computation of Interest;
3.07, Optional Redemption; Form of Note.

### Outstanding checks
- Dated issue/debt-category rating; analytical bucket pending.
- Recent outstanding principal balance.
- Principal activity through April 30, 2026.
- CUSIP/ISIN.

## Learning note — Coupon versus current borrowing cost

- Range's 4.750% coupon is 200 basis points below
  Cleveland-Cliffs' 6.750% coupon.
- The bonds were issued at different dates:
  February 2022 versus April 2023.
- Coupon differences can reflect issuance-date market rates,
  credit risk, contractual terms, and investor demand.
- These coupons alone do not establish which issuer had
  the lower credit spread or whether bonds were cheaper
  than bank loans.
- Coupon determines contractual interest payments.
- Current yield depends on the bond's market price and cash flows.
- A bond trading below par can have a yield above its coupon.

## Candidate 9 — Sirius XM 4.125% due 2030

### Established contractual terms
- Internal ID: SIRIUS_4.125_2030
- Current legal issuer: Sirius XM Radio LLC
- Original legal issuer: Sirius XM Radio Inc.
- Converted from corporation to LLC: September 6, 2024
- Project sector: Communications, project-assigned
- Currency: USD
- Security: Senior notes
- Issuance / accrual start: June 11, 2020
- Original issue size: $1.5 billion
- Annual coupon: 4.125%
- Maturity: July 1, 2030
- Coupon dates: January 1 and July 1
- First coupon: January 1, 2021
- Day-count basis: 360-day year comprising twelve 30-day months
- Regular coupon per $100 face: $2.0625
- No scheduled April 2026 coupon.

### Scheduled call prices
For twelve-month periods beginning July 1:
- 2025: 102.063%
- 2026: 101.375%
- 2027: 100.688%
- 2028 onward: 100.000%
Accrued and applicable additional interest are separate.
April 2026 falls in the 2025 call-price period.
Simulation assumption: no redemption or additional interest.

### Outstanding-status evidence
- Year-end 2025 debt table reports $1.5 billion principal.
- April 2026 principal activity remains unchecked.
- Do not confuse principal with carrying value or fair value.

### Sources
Issuance:
https://www.sec.gov/Archives/edgar/data/908937/000119312520166664/d945164d8k.htm

Contractual terms:
https://www.sec.gov/Archives/edgar/data/908937/000119312520166664/d945164dex41.htm
Relevant sections: Form of Note; Interest; Optional Redemption.

Issuer conversion and debt balance:
https://www.sec.gov/Archives/edgar/data/908937/000090893726000006/siri-20251231.htm

### Outstanding checks
- Dated issue/debt-category rating; analytical bucket pending.
- CUSIP/ISIN.
- Principal activity through April 30, 2026.
- Applicability of additional interest.

## Candidate 10 — Gates 6.875% due 2029

### Established contractual terms
- Internal ID: GATES_6.875_2029
- Legal issuer: Gates Corporation
- Corporate group: Gates Industrial Corporation plc
- Project sector: Industrials, project-assigned
- Currency: USD
- Security: Senior unsecured notes with guarantees
- Issuance / accrual start: June 4, 2024
- Original issue size: $500 million
- Annual coupon: 6.875%
- Maturity: July 1, 2029
- Coupon dates: January 1 and July 1
- First coupon: January 1, 2025
- Record dates: December 15 and June 15
- Non-business-day payment: next succeeding business day
- Day-count basis: 360-day year comprising twelve 30-day months
- Regular coupon per $100 face: $3.4375
- No scheduled April 2026 coupon.

### Verified identifiers
Rule 144A:
- CUSIP: 367398AA2
- ISIN: US367398AA27

Regulation S:
- CUSIP: U3702MAA1
- ISIN: USU3702MAA19

Source: Exhibit A, Form of Note, identifier footnotes.
Use the 144A identifiers for the hypothetical project holding.
This is a project convention, not an actual transaction.

### Call-term status
- A scheduled call-price table has been located.
- Effective dates and early-call provisions must be extracted
  before marking the call summary complete.
- Simulation assumption: no redemption during April 2026.

### Outstanding-status evidence
- Year-end 2025 filing reports $500 million principal outstanding.
- April 2026 principal activity remains unchecked.

### Sources
Issuance completion:
https://www.sec.gov/Archives/edgar/data/1718512/000110465924068270/tm2416310d1_8k.htm

Contractual terms and identifiers:
https://www.sec.gov/Archives/edgar/data/1718512/000110465924068270/tm2416310d1_ex4-1.htm
Relevant section: Exhibit A, Form of Note.

Debt balance:
https://www.sec.gov/Archives/edgar/data/1718512/000162828026007719/gtes-20251231.htm
Relevant section: Note 15 — Debt.

### Outstanding checks
- Dated issue/debt-category rating; analytical bucket pending.
- Complete call-term summary.
- Principal activity through April 30, 2026.

## Worked example: Celanese April 2026 return

All amounts are per $100 face value. Valuation dates are March 31
and April 30, 2026. Simulated clean prices are 98.00 at the beginning
and 99.00 at the end. The documented annual coupon is 6.500%, or
$6.50 per $100 face annually. The $3.25 coupon paid on April 15 is
retained as cash.

For this worked example, the day-count calculation uses 30/360 US
as an explicit project convention. The reviewed contract excerpt
specifies a 360-day year comprising twelve 30-day months but does
not distinguish US from European 30/360.

Beginning accrued interest runs from October 15, 2025 to March 31,
2026, or 166 days:

- Beginning AI = $6.50 × 166/360 = $2.997222222…
- Beginning dirty price = $98.00 + $2.997222222… = $100.997222222…

The April 15 coupon payment resets accrued interest. Ending accrual
runs from April 15 to April 30, or 15 days:

- Ending AI = $6.50 × 15/360 = $0.270833333…
- Ending dirty price = $99.00 + $0.270833333… = $99.270833333…
- Ending wealth including coupon cash = $99.270833333… + $3.25
  = $102.520833333…

The price gain is $99.00 − $98.00 = $1.00. Income gain is coupon
cash plus the change in accrued interest:

- Income gain = $3.25 + $0.270833333… − $2.997222222…
  = $0.523611111…

Total return includes both the ending dirty bond value and coupon
cash, relative to beginning dirty value:

**Total return** = (ending dirty price + coupon cash) / beginning
dirty price − 1

= ($99.270833333… + $3.25) / $100.997222222… − 1
= 1.5086% (rounded)

Coupon cash is separate from ending dirty price because the coupon
has already been paid: it is no longer part of the bond's value or
its accrued interest, but remains part of the investor's ending
wealth.

## Simulated teaching allocations

The face values in `portfolio_holdings.csv` are simulated teaching
allocations totaling $1,000,000. They were selected after inspecting
the simulated bond returns above; therefore, any portfolio performance
calculated from these allocations is illustrative and does not
demonstrate investment selection skill.

| Internal ID | Face allocation (USD) |
|---|---:|
| CELANESE_6.500_2030 | $150,000 |
| MAGNOLIA_6.875_2032 | $125,000 |
| BBW_6.625_2030 | $100,000 |
| GOODYEAR_5.250_APR2031 | $75,000 |
| URNA_5.250_2030 | $125,000 |
| CCO_4.500_2030 | $75,000 |
| CLF_6.750_2030 | $75,000 |
| RANGE_4.750_2030 | $125,000 |
| SIRIUS_4.125_2030 | $50,000 |
| GATES_6.875_2029 | $100,000 |

Beginning weights are each holding's beginning dirty market value
divided by the total beginning dirty market value. Face allocations
remain fixed during the period, while market-value weights can change
as prices and accrued interest change. Calculated weights are exported
in `outputs/portfolio_contributions.csv`.

## Simulated risk inputs

The effective-duration and OAS values in `simulated_risk_inputs.csv`
are teaching assumptions, not market observations or model-derived
measures. They are held constant between March 31 and April 30, 2026
to isolate the effects of portfolio weighting and coupon cash. These
inputs are broadly illustrative and are not calibrated to the specific
securities.

## Risk exposure formulas and interpretation

### Portfolio effective duration

For each bond, multiply its dirty market value by its effective
duration. Add these amounts across all ten bonds, then divide by total
portfolio NAV:

**Portfolio effective duration**

$$
D_{\text{portfolio}}
= \frac{\sum_{i=1}^{10} MV_i D_i}{\mathrm{NAV}}
$$

- $MV_i$ is holding \(i\)'s dirty market value in dollars.
- $D_i$ is bond \(i\)'s effective duration in years.
- $\mathrm{NAV}$ is total dirty bond market value plus cash.
- $\sum$ means sum across all ten bonds.

Equivalently, multiply each bond's NAV weight by its duration and add
the results. Cash has zero duration, so it contributes nothing to the
numerator but remains in the NAV denominator. The result is in years.

### Average bond OAS

For each bond, multiply its dirty market value by its OAS. Add these
amounts across the bonds, then divide by total dirty market value of
the bonds:

**Average bond OAS**

$$
\text{Average bond OAS}
= \frac{\sum_{i=1}^{10} MV_i\,\mathrm{OAS}_i}
       {\sum_{i=1}^{10} MV_i}
$$

- $\mathrm{OAS}_i$ is bond \(i\)'s option-adjusted spread in basis points.
- Use bond-only weights, which sum to 100% across the bonds.
- Cash is excluded from both numerator and denominator.
- The result is in basis points.

The denominators differ because duration measures risk exposure of
the whole portfolio, including cash in NAV, whereas average bond OAS
describes only the invested bond holdings.

### Simulated illustration

The following figures are a simulated teaching example, not market
observations or calibrated risk estimates:

- Bond A: market value $60,000; duration 3 years; OAS 300 bps.
- Bond B: market value $30,000; duration 5 years; OAS 500 bps.
- Cash: $10,000.
- NAV: $100,000.

Multiply each bond's market value by its duration and divide their
sum by NAV to get portfolio duration:

$$
D_{\text{portfolio}}
= \frac{60{,}000 \times 3 + 30{,}000 \times 5}{100{,}000}
= 3.3\ \text{years}
$$

Multiply each bond's market value by its OAS and divide by total bond
market value, excluding cash, to get average bond OAS:

$$
\text{Average bond OAS}
= \frac{60{,}000 \times 300 + 30{,}000 \times 500}{90{,}000}
\approx 366.67\ \text{bps}
$$

## April 2026 simulated risk exposure results

The following simulated results are from
`outputs/risk_exposure_summary.csv`. The benchmark is the constructed
same-universe benchmark, not a market index.

| Portfolio / benchmark | Valuation date | Dirty bond market value (USD) | Cash (USD) | NAV (USD) | Cash weight | Effective duration (years) | Average bond OAS (bps) |
|---|---|---:|---:|---:|---:|---:|---:|
| Portfolio | 2026-03-31 | $1,001,207.64 | $0.00 | $1,001,207.64 | 0.000000% | 3.072576 | 325.411014 |
| Portfolio | 2026-04-30 | $994,953.73 | $12,687.50 | $1,007,641.23 | 1.259129% | 3.034159 | 324.532674 |
| Constructed benchmark | 2026-03-31 | $1,001,207.64 | $0.00 | $1,001,207.64 | 0.000000% | 3.070000 | 340.000000 |
| Constructed benchmark | 2026-04-30 | $993,482.19 | $12,542.84 | $1,006,025.03 | 1.246772% | 3.031293 | 339.106474 |

Duration changes reflect changing bond market-value weights and the
accumulation of coupon cash, which has zero duration. As cash builds,
it remains in NAV but not the duration numerator.

Average bond OAS changes reflect changes in bond-only market-value
weights, not changes in individual OAS inputs; the simulated OAS
inputs are held constant at both valuation dates. This simulated
weighted OAS average provides spread context, not a direct measure of
expected loss or spread sensitivity.

The ending portfolio NAV reconciles to the simulated performance
summary: $994,953.73 ending dirty bond market value plus $12,687.50
coupon cash equals $1,007,641.23 ending NAV, matching
`outputs/performance_summary.csv`.