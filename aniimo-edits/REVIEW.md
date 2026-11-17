# ANIIMO stream edits — review notes (preview, belum render)

Source: `Map Baru. Azam baru.mp4` (vertical 1080×1920 HEVC 60fps, 4j14m).
Google Drive hit its download quota after 6.7 GB, so only the first **2j26m** was
downloaded, transcribed (faster-whisper medium, Malay) and used. Part 2 (2:27–4:14)
was never analysed.

Gameplay window is cropped from the stream layout (1080×608 at y=463); chat and
viewer names are left out.

| Video | Project | Length | Style |
|---|---|---|---|
| Funny Moments | `funny-moments/` | 111.5 s | Comic: yellow halftone, tilted frame, bouncing stroked captions, sticker bursts, shake/punch-ins, stripe wipes |
| Best Moments | `best-moments/` | 117.3 s | Neon arena: 8 numbered highlights, big crops, light-slash + flash transitions, damage-number callouts |
| New Discoveries | `new-discoveries/` | 98.1 s | Field journal: full HUD kept for context, ENTRY chapters, info cards with BARU/EVO/TIP stamps, iris transitions |

Workflow: `edl/make_edls.py` (cut list, source-time captions, zooms, SFX) → `tools/cut.sh`
(crop and cut clips) → `tools/build.py` (writes `index.html` + `compositions/captions.html`).

## Creative calls
- Hooks: Funny opens on "Woi! Dia pakai bontot!", Best on the CATCH x10 mass catch, Discoveries on the Scrubbit card.
- Mira says "secubit / sugartini / posh whips". On screen these use the in-game names (Scrubbit, Sugarslime, Pouchwisp), which were read from the game UI.
- Best Moments lowers the stream audio (0.35–0.5) where Mira is chatting about something else during fights. Captions are only on lines about the fight.
- Left out: the long tutorial and Q&A stretches, the gender joke at 1:34 (sensitive), and the ID/QR overlays.

## What was measured vs. only looked at
- `hyperframes check` passes on all three (0 errors). The remaining warnings are platform safe-zone edges for the top titles and the cards, plus lint style notes.
- Snapshots were reviewed at key times. **The sound was measured, not heard**: cut points come from whisper word timestamps.
- SFX come from the bundled HyperFrames library only (Pixabay licence; Openverse is blocked here). There is no music bed, so the game's own music carries.

## Weakest spots
- Funny f08 ("bunuh je lah aku") plays over a static menu screen. Only the zoom keeps it moving.
- Some whisper lines may still have small errors. Check the captions in the preview.
