"""Download a balanced subset of Action100M candidate videos at 144p.

Picks ~50 kitchen + ~50 manipulation + all navigation, downloads via yt-dlp.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def pick_subset(index, n_per_domain=50):
    by_dom = {"kitchen": [], "manipulation": [], "navigation": []}
    for x in index:
        # primary domain: first listed (we already sort kitchen > navigation > manipulation in build)
        for d in x["domains"]:
            if d in by_dom and x not in by_dom[d]:
                by_dom[d].append(x)
                break
    # sort each by event count desc + dedupe
    for d in by_dom:
        by_dom[d].sort(key=lambda v: -v["num_events"])
    picked = (by_dom["kitchen"][:n_per_domain]
              + by_dom["manipulation"][:n_per_domain]
              + by_dom["navigation"])
    # dedupe preserving order
    seen = set()
    out = []
    for v in picked:
        if v["video_uid"] not in seen:
            seen.add(v["video_uid"])
            out.append(v)
    return out


def download_one(uid, video_dir, fmt="160+140"):
    out = video_dir / f"{uid}.mp4"
    if out.exists() and out.stat().st_size > 100_000:
        return "exists", out.stat().st_size
    r = subprocess.run(
        ["yt-dlp", "-f", fmt, "--merge-output-format", "mp4",
         "-o", str(out), "--no-progress", "--quiet",
         f"https://www.youtube.com/watch?v={uid}"],
        capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0 or not out.exists() or out.stat().st_size < 100_000:
        return "fail", r.stderr[-300:] if r.stderr else r.stdout[-300:]
    return "ok", out.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="index.json")
    ap.add_argument("--video-dir", default="videos")
    ap.add_argument("--n-per-domain", type=int, default=50)
    ap.add_argument("--format", default="160+140",
                    help="yt-dlp format spec (160+140 = 144p+audio)")
    args = ap.parse_args()

    index = json.loads(Path(args.index).read_text())
    video_dir = Path(args.video_dir)
    video_dir.mkdir(exist_ok=True)

    picks = pick_subset(index, args.n_per_domain)
    print(f"picked {len(picks)} videos to download")

    total = 0
    ok = 0
    fail = []
    for i, x in enumerate(picks):
        uid = x["video_uid"]
        status, info = download_one(uid, video_dir, args.format)
        if status == "ok":
            ok += 1
            total += info
            print(f"  [{i+1}/{len(picks)}] OK    {uid} ({info/1e6:.1f} MB, cum={total/1e6:.0f} MB)")
        elif status == "exists":
            ok += 1
            total += info
        else:
            fail.append((uid, info))
            print(f"  [{i+1}/{len(picks)}] FAIL  {uid}: {info[:80]}")
        sys.stdout.flush()

    print(f"\n=== done ===")
    print(f"  ok:    {ok}/{len(picks)}")
    print(f"  fail:  {len(fail)}")
    print(f"  total: {total/1e6:.0f} MB")
    Path("download_manifest.json").write_text(json.dumps({
        "picked": [x["video_uid"] for x in picks],
        "ok": ok,
        "fail": [u for u, _ in fail],
        "total_bytes": total,
    }, indent=2))


if __name__ == "__main__":
    main()
