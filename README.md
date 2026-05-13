# Action100M Benchmark Candidates Viewer

Single-page viewer for 168 benchmark-candidate videos auto-filtered from the
[Action100M-preview](https://huggingface.co/datasets/facebook/Action100M-preview)
dataset (HowTo100M source corpus).

**Live**: https://jxb1st.github.io/action100m-viewer/

## How candidates were picked

1. **Duration gate** — keep videos with 180 s ≤ duration ≤ 300 s (3–5 min)
2. **LLM judgement** — for each survivor, send Action100M's hierarchical
   Tree-of-Captions (title + description + root GPT summary + deduplicated
   action list) to GPT-4o with a strict prompt classifying:
   - **domain**: `kitchen` / `manipulation` / `navigation` / `neither`
   - **distinct event count** (semantically merged, narrative steps removed)
   - **is_good_candidate**: at least one target domain AND > 3 distinct events

The exact prompt is visible in the viewer's "LLM Prompt" panel.

## Result

| Domain          | Videos |
|-----------------|-------:|
| Kitchen         |     80 |
| Manipulation    |     84 |
| Navigation      |      3 |
| Kitchen + Manip |      1 |
| **Total**       |    168 |

## Layout

```
action100m-viewer/
├── index.html            single-page viewer
├── index.json            lightweight per-video summary (for dropdown / filters)
├── data/<uid>.json       full per-video record: metadata, nodes, LLM prompt + response
└── videos/<uid>.mp4      144p mp4 for a subset (others fall back to YouTube iframe)
    └── manifest.json     list of uids that have local mp4
```

## License / source

- Videos are sourced from YouTube via the Action100M-preview dataset.
- Annotations (`nodes[*].gpt`) are from Meta FAIR's Action100M release
  (FAIR Noncommercial Research License).
- LLM judgements (`llm.judgement`) are produced by this project using GPT-4o.
