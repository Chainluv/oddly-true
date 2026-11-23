# NO WAY. blog

Live page: https://claude.ai/artifact/RgSSfSfEzDV5N7Pb9YwSeM (private until shared from its Share menu).

There's one post per video topic (18 so far), in the same style as the videos: film grain, Anton and Oswald type, amber and red accents, series tags, and counters that tick up. Each post has a muted 5-second preview loop cut from its video, the story, "What we checked", sources, a "Watch the Short" link (and a long-version link where there is one), and previous/next links to go through the posts one by one. The home page has a stat ticker and History, News and Series filters.

- `index.html`: the whole blog. The posts live in the `POSTS` array; add a new entry when a new video ships.
- `media/`: 288×512 preview loops (5s, muted) and poster frames, cut from each episode's MP4:
  ```bash
  ffmpeg -nostdin -ss <start> -t 5 -i <episode>/<file>.mp4 -an -vf "scale=288:512,fps=24" -c:v libx264 -crf 31 -movflags +faststart blog/media/<slug>.mp4
  ffmpeg -nostdin -ss <start+1> -i <episode>/<file>.mp4 -frames:v 1 -vf scale=288:512 -q:v 5 blog/media/<slug>.jpg
  ```
- Watch links point at the MP4s on GitHub (`claude/molasses-flood-shorts-qnqvbt`). Viewers need access to the repo, or swap in YouTube links once the videos are posted.
