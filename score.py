#!/usr/bin/env python3
"""Score language-identification predictions on FinConvBench v1.0.

Usage:
    python3 score.py predictions.csv
    python3 score.py predictions.csv --benchmark data/FinConvBench_v1.0.csv

predictions.csv needs a header row and two columns:
    id                the benchmark row id (1 to 11465)
    predicted_label   one of: en, hi, hi-en, ta, ta-en, te, te-en, kn, kn-en
                      Other values receive zero exact-label and
                      label-in-family credit. Reply-language accuracy is
                      scored separately.
An optional third column, reply_language, gives the language your system
would reply in. If the column is absent, the reply language is derived from
the predicted label (see "Reply-language accuracy" below). If the column is
present, every scored row needs a value in it.

As in the paper, the 468 rows labeled `unknown` are not scored. A prediction
is required for each of the other 10,997 rows.

Metrics
    Exact-label accuracy     predicted_label equals the benchmark label.
    Reply-language accuracy  the reply language is acceptable for the message
                             (Section 3 of the paper):
                               Hindi messages (hi, hi-en) accept hi or hi-en;
                               Tamil, Telugu and Kannada messages accept their
                               own language (native or romanized) or en;
                               English messages accept en only.
                             Derived reply language, used when no reply_language
                             column is given: the predicted label if it is hi or
                             hi-en, otherwise en (the English fallback policy of
                             the paper, under which Tamil, Telugu and Kannada
                             users are answered in English).
    Label-in-family          the predicted label is one of the nine labels and
                             has the same base language as the benchmark label
                             (ta and ta-en are one family).

The script does not map a tool's raw output (for example ISO codes) to these
labels. Do that first; the paper's mapping is described in its Appendix B.

Standard library only. No model and no detector code is included.
"""
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

LABELS = {"en", "hi", "hi-en", "ta", "ta-en", "te", "te-en", "kn", "kn-en"}
HINDI = {"hi", "hi-en"}


def base(label):
    return label.split("-")[0]


def derived_reply(pred):
    return pred if pred in HINDI else "en"


def reply_ok(gold, reply):
    if gold in HINDI:
        return reply in HINDI
    if gold == "en":
        return reply == "en"
    return reply in {base(gold), base(gold) + "-en", "en"}


def in_family(gold, pred):
    return pred in LABELS and base(pred) == base(gold)


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Score predictions on FinConvBench v1.0.")
    ap.add_argument("predictions", help="CSV with columns id, predicted_label[, reply_language]")
    ap.add_argument("--benchmark", default=str(here / "data" / "FinConvBench_v1.0.csv"))
    args = ap.parse_args()

    with open(args.benchmark, newline="", encoding="utf-8") as f:
        gold = {r["id"]: r["expected_language"] for r in csv.DictReader(f)}
    scored = {i: g for i, g in gold.items() if g != "unknown"}

    with open(args.predictions, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        if "id" not in cols or "predicted_label" not in cols:
            sys.exit("predictions file needs the columns: id, predicted_label")
        has_reply = "reply_language" in cols
        preds = {}
        for r in reader:
            i = r["id"].strip()
            if i in preds:
                sys.exit(f"duplicate id in predictions: {i}")
            preds[i] = (r["predicted_label"].strip(), (r.get("reply_language") or "").strip())

    missing = [i for i in scored if i not in preds]
    if missing:
        sys.exit(f"{len(missing)} scored rows have no prediction (first: id {missing[0]})")

    n = len(scored)
    exact = reply = family = 0
    per_n, per_exact = Counter(), Counter()
    for i, g in scored.items():
        pred, rep = preds[i]
        if not has_reply:
            rep = derived_reply(pred)
        elif not rep:
            sys.exit(f"empty reply_language for id {i}: fill every scored row or remove the column")
        per_n[g] += 1
        if pred == g:
            exact += 1
            per_exact[g] += 1
        reply += reply_ok(g, rep)
        family += in_family(g, pred)

    print(f"Scored rows: {n} (the {len(gold) - n} `unknown` rows are excluded)")
    print(f"Exact-label accuracy:     {100 * exact / n:6.2f}%  ({exact}/{n})")
    print(f"Reply-language accuracy:  {100 * reply / n:6.2f}%  ({reply}/{n})"
          + ("  [from the reply_language column]" if has_reply else "  [derived from the predicted label]"))
    print(f"Label-in-family:          {100 * family / n:6.2f}%  ({family}/{n})")
    print("\nExact-label accuracy by benchmark label:")
    for g in sorted(per_n, key=lambda x: (base(x) != "en", x)):
        print(f"  {g:6s} {100 * per_exact[g] / per_n[g]:6.2f}%  ({per_exact[g]}/{per_n[g]})")


if __name__ == "__main__":
    main()
