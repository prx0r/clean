# Delivery Notes

This bundle contains the deterministic v2 framework, model prompt, decision protocol, schemas, complete argument IR, 88-shot visual program, public timing map, contact sheet, QA montage, validation report, and final silent MP4.

The supplied essay and generated narration text are not duplicated in this export. Place the essay at:

`essays/the-song-with-no-singer.md`

Then run:

```bash
npm install
npm run build:song
npm run audit:song-analysis
npm run audit:song
npm test
npm run compile:song
npm run render:song
```

The included video uses draft word-count timing. For publication, record or synthesize final narration, force-align it to the stable `song-001` through `song-088` shot IDs, and pass one exact duration for every shot through `--timings`.
