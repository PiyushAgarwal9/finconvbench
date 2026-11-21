# FinConvBench v1.0 labeling guide

This guide documents the rule that the audited labels follow. It was derived from the label audit (4,454 label changes, 4,432 of them X to X-en). Writing the guide changed no labels.

## The rule

1. **Script decides the suffix.** If a message is native-script-dominant (Devanagari, Tamil, Telugu, Kannada), the label is the plain language (`hi`, `ta`, `te`, `kn`). If it is Latin-script-dominant and carries Indic-language content, the label is the romanized code-mix label (`hi-en`, `ta-en`, `te-en`, `kn-en`), with or without English mixed in. Romanized pure Hindi ("mera balance kitna hai") is `hi-en`, not `hi`.
2. **`en`** is Latin script with no Indic-language tokens. Borrowed banking vocabulary (balance, OTP, loan, and similar words) does not by itself make a message `en`: an otherwise-Indic message whose only English tokens are banking nouns keeps its X-en label.
3. **`unknown`** means no usable language signal: bare numbers, single ambiguous banking nouns, emoji, or gibberish. These rows are excluded from scoring.

## Known borderline zones (disclosed, left as they are)

- Messages made only of banking vocabulary with no Indic function words ("balance check"). They are labeled `en`, which is defensible because they carry no Indic evidence, but they sit next to the "single banking noun" rule for `unknown`.
- Messages with exactly one weak Indic marker in otherwise-English text.

## How the labels were reviewed

- **Label audit.** Relabels were proposed by the script rule. A proposal was accepted automatically only where the detector used during the audit agreed at confidence at least 0.8 or the script was unambiguous. Hard and boundary cases were decided by a human. Every change is listed in `audit/label_audit_record.csv`.
- **Spot check.** Language-matched reviewers checked a stratified sample of 442 automatic relabels and confirmed 436.
- **Blind study.** Two multilingual native Hindi speakers independently labeled a stratified sample of 330 messages, blind to the reference labels and to each other. They agreed on the language family for 330 of 330 messages. Exact-label agreement was Cohen's kappa 0.45, and every disagreement was plain language versus code-mix label within the same family.
- Double annotation covers that sample, not the full corpus. Thirteen label errors documented during verification are retained in the frozen benchmark.

Exact-label accuracy on this benchmark therefore measures agreement with this convention. See the paper for details.
