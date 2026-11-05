# FAQ

## Does Signoff send data anywhere?

No. The runtime evidence path is local and makes no network calls. Package installation and image preparation may need a separate controlled dependency source.

## Does it use an LLM to answer questions?

No. It applies explicit, human-decided mapping rules and leaves unmatched questions `UNMAPPED`.

## Is the demo evidence real?

No. Demo inputs and outputs are synthetic and marked `SIMULATION_DISCLOSURE`.

## Does a verified pack prove the evidence is true?

No. Verification checks pack integrity, artifact digests and required disclosure markers. It does not authenticate source records or validate their real-world truth.

## Who signs the Oversight Statement?

An accountable human. The generated statement leaves the signature fields blank.

## Can I use the repository mapping table as a production policy?

No. `OWNER/mapping-table.csv` is deliberately header-only. The owner must make and sign each decision for the specific questionnaire and context.

## Why is a question unanswered?

It may not have a signed mapping rule or sufficient evidence. Review the answer file and gap list; do not infer an answer from a nearby rule.
