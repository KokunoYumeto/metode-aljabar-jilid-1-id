# Unit 013 equation-number continuity correction

Status: passed locally; corrected artifact installed; publication not performed
in this bounded repair task.

## Defect and scope

The Unit 013 standalone driver inherited Chapter 2 and Section 2.5 counters but
left the equation counter at zero. It therefore rendered the labels
`eqn:Yoneda-cat-duality` and `eqn:Yoneda-map` as (2.1) and (2.2), even though
the complete Chapter 2 source already contains `eqn:naturaltrans-def` at line
255 and `eqn:horizontal-comp` at line 290 as equations (2.1) and (2.2).

The repair adds exactly `\setcounter{equation}{2}` immediately before the
existing `\InputSourceLineRange{chapter2.tex}{678}{765}` call. No source span,
translation, mathematics, environment, label key, reference target, diagram,
index entry, terminology decision, rights statement, or declared source
correction changed.

## Deterministic proof

- Driver after repair: 4,776 bytes; SHA-256
  `f3a7b9e2351288eaf273930572d564cb8d0011e44441cd22246e8f385985cdf2`.
- Build A PDF: 106,159 bytes; SHA-256
  `f5611f6a03109577d47aae9aba9cdcd992d567547085e3c69548e14f259cce93`.
- Build B PDF and installed reader: 106,162 bytes; SHA-256
  `03ced2b80bf14814d01bc73cf378bfab820ec40ad0571eaa33cf514d79d760cf`.
- Build B final log and installed log: 86,834 bytes; SHA-256
  `605c9d68009fcfa0d9b746864ebad7e1618943932cd6d8cd1140e84fbd657039`.
- Final AUX: 2,078 bytes; SHA-256
  `1c95b7121342b9d73fa1915a3efe8eab0c4dc19d3a65f5d48903e3fbad301f4f`.
- Exact final AUX map:
  `eqn:Yoneda-cat-duality -> 2.3, page 1, equation.2.3`;
  `eqn:Yoneda-map -> 2.4, page 1, equation.2.4`.
- Functional replay: 7/7 page PNGs are identical between clean builds in
  Poppler and independently 7/7 in MuPDF at 144 dpi.
- Poppler concatenated render SHA-256:
  `f950194f9bc7305c9040e0d7952b215545ee9ba2e2fb3493dd9ffcbcc1a063fd`.
- MuPDF concatenated render SHA-256:
  `ac6f13e1379f69d94449ecb81474e52c67fe8b6f95ee840f46fccf2d4a8a5032`.
- Old-to-new isolation in both renderers: pages 1, 2, 5, 6, and 7 are
  pixel-identical; only pages 3 and 4 changed, exactly where the printed
  equation numbers and their three references occur.
- Final-log blockers: zero. All seven Build B pages were inspected at original
  render resolution in both Poppler and MuPDF; no visual defect was found.

The replaced reader was 106,154 bytes with SHA-256
`4db806c3a0c42449b1333e25109d135176931880a48982a70b776e04be7ffa2a`.
The replaced final log was 86,810 bytes with SHA-256
`a407323233d53e8f20d952dbacaea16000ccb96b7c03bf9854695f9110311b91`.

## Backend gate

The Unit 013 generator now pins the repaired driver, installed PDF, final log,
final AUX, and this correction receipt. Before emitting data it requires the
counter-setting command immediately before the frozen source input and requires
the exact two AUX label-number-page-anchor records. The regenerated JSON and all
six Unit 013 CSV projections passed the shared v1 schema, identity, relation,
order, and live-binding validator. A dedicated `backend_integrity` QA event
records this equation-number continuity proof without changing the previously
admitted translation audit.

## Rights and provenance continuity

Wen-Wei Li remains the source author. The principal text and translation remain
CC BY 4.0; the AJbook fragment remains CC BY-SA 3.0; bundled fonts remain OFL
1.1. The reader remains an independent, non-endorsed derivative. Production
provenance remains `OpenAI Codex gpt-5.6-sol, Ultra`, separately recorded from
source authorship and human-contributor credit.
