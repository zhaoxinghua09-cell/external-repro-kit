# Verification Policy

This policy defines who counts as an **independent validator**, what evidence is accepted, and what may never be claimed. It deliberately gives this project **no certification power**.

## 1. What a receipt can and cannot mean

A receipt means: *"on this machine, at this commit, with these commands, this happened."* It does **not** mean the tool is certified, audited, compliant, or endorsed. No receipt may be used as a quality guarantee.

## 2. Three validator classes

| Class | Who | Can attest | Cannot attest |
|---|---|---|---|
| **A · Technical** | independent developers, security researchers, agent/MCP engineers, benchmark engineers | independent reproduction, defects, compatibility counter-examples | industry adoption, procurement |
| **B · Application** | enterprise AI teams, agent-platform developers, applied teams | integration evidence, real-scenario feedback, willingness-to-pay signals | standards endorsement, academic citation |
| **C · Theory / standards** | academic researchers, standards experts, independent governance researchers | citations, review comments, co-authored contributions | product usability, commercial conclusions |

## 3. Independence rules

1. **Affiliation excludes E3.** Maintainers, members of the projects' own organisations, internal collaborators, and **AI agents acting alone** cannot be independent validators. Their runs are recorded as `E2 (self-affiliated)`.
2. **AI cannot sign a receipt.** Reports produced by an LLM/agent without a natural-person or institutional signature never count as E3/E4. AI may be used as a tool by a human validator; the responsibility stays with the human.
3. **One person, one record.** Multiple runs by the same person = 1 validator, N reproductions.
4. **No purchased conclusions.** Paid engagements are allowed only if disclosed, and the conclusion may not be pre-set.

## 4. Evidence ladder

| Level | Meaning | Accepted evidence |
|---|---|---|
| E0 | no external action | — |
| E1 | external discovery/access | star, fork, clone, download, first issue |
| E2 | install + run completed | install log, run log, `RESULT.json` (if same operator, mark `self-affiliated`) |
| E3 | independent reproduction or integration | third-party receipt with environment, pin, commands, exit code, deltas; integration PR/issue; citation |
| E4 | non-affiliated validation with reviewable evidence | signed external report (environment / commands / output / delta analysis) that others can re-check |

E4 is **not** a certification and must not be described as industry recognition.

## 5. What counts as a receipt

Accepted: OS/arch, Python/Node version, install method **and pin**, verbatim commands, exit code, output excerpt or `RESULT.json`, signed with a real or contactable pseudonymous identity, independence declaration included.

Rejected: "it worked for me", good news only, anonymous with no contact (recorded as E2 at best), AI-generated without a human signature, something that cannot be reviewed.

## 6. Rights and duties of a validator

Rights: full pack and expected baseline; the known-issues list; the right to have deltas recorded verbatim; the right to withdraw the attribution at any time (we remove references within 30 days); the right to refuse pre-set conclusions.

Duties: declare any affiliation (including "I once opened a PR"); do not modify the repositories under test; do not present an E3 receipt as certification/audit/compliance; desensitise real data; report high-severity findings privately with a 30-day fix window before publishing.

## 7. Downgrade and revocation

| Situation | Action |
|---|---|
| first valid receipt | recorded as E3 |
| same person, new pin | +1 reproduction, still 1 validator |
| receipt found fabricated / unreviewable | downgraded to E2 or removed, marked `revoked` |
| affiliation discovered later | marked `conflict=declared`, downgraded to E2 |
| validator withdraws | marked `withdrawn`, no further citation |
| same conclusion by ≥2 unrelated validators | may be marked E4 (still not a certification) |
| E3 receipt older than 12 months | marked `stale` until re-run on a new pin |

## 8. Wording rules

Never: "third-party certified", "independently audited", "industry-recognised", "N experts endorse" (when any of them is affiliated), describing E2 as external validation.

Allowed: "independently reproduced by `<name>` on `<environment>` on `<date>`, result `<match/no match>`; this receipt is not a certification." / "independent reproduction evidence: `k/n`, remainder unverified."

## 9. Filing a receipt

Open an issue titled `reproduction: <pack> on <os> <python>` and attach `RESULT.json`. Deltas are more valuable than agreement — record them, do not edit our baseline.
