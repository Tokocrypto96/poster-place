# VELMARIS — The Poster for a Place That Isn't There

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Tokocrypto96/poster-place/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/Tokocrypto96/poster-place/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster generator for a fictional place, built for make.fun's
["The Poster for a Place That Isn't There"](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539) bounty ($50 in USDC).

**The place:** Velmaris — an island city that doesn't exist, where the tide
keeps the light. Its landmark is a spiral nautilus lighthouse on a rock
islet, watching over a teal lagoon under a coral sun. Slogan: *"Where the
tide keeps the light."*

## How it works

`main.py` draws the poster entirely with the Python standard library
(`zlib` + `struct` for a hand-encoded PNG — no PIL, no network, no
randomness) and writes a single 1024×1024 image to `/output/entry.png`.

## Run it

```sh
python3 main.py
```
