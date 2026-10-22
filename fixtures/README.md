# Synthetic fixtures

All dialogue, identities, meeting metadata and draft claims here are invented test data, not recovered meetings. `draft.json` is authored expected output for repeatable offline tests, not generated inference. It deliberately leaves human approvals false/unknown. The sample has one source, an unidentified speaker, a capture gap, a proposal that is not approved and a supported commitment without a deadline.

`meeting.json` is canonical evidence. `render-request.json` packages evidence and draft for REST/Responses bridge tests. Changing a quote or utterance ID to an unsupported value must fail validation. No real customer or meeting content belongs here.
