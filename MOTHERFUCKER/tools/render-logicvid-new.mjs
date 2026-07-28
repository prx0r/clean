import { readFile } from 'node:fs/promises';
import { renderVideo, renderContactSheet, validateVideo } from '../renderer.mjs';
const pack = JSON.parse(await readFile('packs/compiled/logicvid-reality-appears.json', 'utf8'));
await renderContactSheet(pack, 'build/logicvid/contact-sheet.png', {columns: 3, cellWidth: 480, time: 0.5});
const result = await renderVideo(pack, 'build/logicvid/video.mp4');
const validation = validateVideo(pack, 'build/logicvid/video.mp4');
console.log(JSON.stringify({result, validation}, null, 2));
if (!validation.valid) process.exit(1);
