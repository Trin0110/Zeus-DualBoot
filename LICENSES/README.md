# Licensing and provenance

New Zeus code is MIT (`../LICENSE`). The unmodified DarwinBoot source/test subset
is BSD-2-Clause-Patent; its full license is retained beside it and copied here.
`third_party/DarwinBoot/UPSTREAM.json` records exact revision, original paths,
SHA256 hashes and recent upstream history. It is a partial source snapshot; the
original upstream Git history remains accessible at the recorded immutable commit.

HakiOS is fetched at a fixed commit only into ignored build output for research.
Its loader/tools are MIT, while XNU derivatives are APSL; its combined notice is
retained here. Its repository may have other components governed by their own notices.
Do not redistribute build caches without auditing their contents/licenses.

ios-sweet's console was compiled in an external research checkout. Its project MIT
notice is retained as research attribution; no console/font source is included in
the final tree because the generated cp850 font needs its own provenance review.
Other projects have mixed or unresolved grants. No code is copied from repositories
merely because they are public. Linux/Xiaomi DTS/driver references are not imported
into the MIT library; GPL/APSL integration questions remain explicit research work.
