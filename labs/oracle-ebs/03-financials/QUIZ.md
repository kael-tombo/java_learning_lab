# Lab 03: Financials — Quiz

**1.** Before changing any AP configuration, what should you build first?

A. A batch hold release job
B. A hold taxonomy showing reason, volume, and value
C. A report of paid invoices
D. A tighter tolerance

<details><summary>Answer</summary><b>B</b> — Measure the distribution first. A remediation chosen without knowing the dominant hold type is guessing.</details>

---

**2.** A supplier bills 97 units against a PO for 100, and 97 were received.
The invoice is quantity-held. What is the root cause?

A. Supplier under-billing
B. The matching rule compares invoiced against ordered instead of received
C. The receipt was not entered
D. The PO was amended

<details><summary>Answer</summary><b>B</b> — Short shipment is normal. The rule is comparing the wrong quantities.</details>

---

**3.** Why is matching-rule correction preferred over widening quantity tolerance?

A. It is faster to implement
B. It makes the comparison correct rather than merely tolerable
C. It uses less storage
D. Tolerances cannot be configured

<details><summary>Answer</summary><b>B</b> — Tolerance widening hides the semantic error; rule correction removes it.</details>

---

**4.** How should a price variance tolerance ideally be chosen?

A. Round number, e.g. 5%
B. Copy industry practice
C. From the measured variance distribution, above the noise band
D. Set to zero for maximum control

<details><summary>Answer</summary><b>C</b> — A data-derived tolerance is defensible to auditors and separates noise from material discrepancies.</details>

---

**5.** A tolerance of 0% on price variance means:

A. Perfect price control
B. Any rounding difference holds the invoice
C. Prices are ignored
D. Holds are disabled

<details><summary>Answer</summary><b>B</b> — With ~99% false positives, users learn to ignore holds and the control's signal is destroyed.</details>

---

**6.** Which metric proves a hold-rate reduction did not weaken the control?

A. Average days held
B. Number of hold reasons
C. Escape rate — real discrepancies that passed validation
D. Supplier count

<details><summary>Answer</summary><b>C</b> — Hold rate can fall because the control was disabled. Escape rate distinguishes calibration from removal.</details>

---

**7.** Why is mass-releasing holds a SOX finding risk?

A. It is slow
B. It converts a control into a rubber stamp
C. It violates tax law only
D. It requires a database restart

<details><summary>Answer</summary><b>B</b> — Automated release with explicit criteria, mandatory reason codes, and full audit is defensible; blanket release is not.</details>

---

**8.** In the cumulative variance distribution, the tolerance should sit:

A. Below the noise band
B. Just above where cumulative reaches ~97–98%
C. At the maximum observed variance
D. At 50%

<details><summary>Answer</summary><b>B</b> — That separates rounding/rebate effects from material discrepancies.</details>

---

**9.** If holds average 12 days and DPP is 5 days, what is the effective payment cycle?

A. 5 days
B. 12 days
C. 17 days
D. 60 days

<details><summary>Answer</summary><b>C</b> — Hold time adds directly to payment cycle time: 5 + 12 = 17 days.</details>

---

**10.** A remediation drops holds 30%→8% but escape rate rises 0%→2%. What is the correct conclusion?

A. Success — holds are down
B. The control has been weakened; investigate the over-invoice path
C. Escape rate is not a valid metric
D. Increase tolerances further

<details><summary>Answer</summary><b>B</b> — A rising escape rate means real discrepancies now pass. Both metrics must move in the right direction.</details>

---

## Scoring
- **9–10**: Ready to run a Payables diagnostics engagement.
- **7–8**: Solid; revisit tolerance derivation and escape rate.
- **5–6**: Re-read THEORY sections on distributions and control strength.
- **<5**: Work through EXERCISES 1, 3, and 5 again.