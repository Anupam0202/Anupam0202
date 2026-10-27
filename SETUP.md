# Maintaining this profile

Everything visual on the profile is generated from one file, so updates take a minute and never drift out of sync.

```text
data/profile.toml  ──►  scripts/build.py  ──►  assets/*.svg  +  CERTIFICATIONS.md
                                                   ▲
README.md (hand-written) references these images ──┘
```

## Update something

1. Edit `data/profile.toml`: metrics, timeline, experience map, projects, recognition, stack or certifications.
2. Run `python3 scripts/build.py` (Python 3.11+, standard library only).
3. Commit the data change together with the regenerated files.

`python3 scripts/build.py --check` fails if any generated file is stale or if a README points at a missing image. The `profile` GitHub Actions workflow runs the same check on every push and pull request.

## Common edits

| Task | Where |
| --- | --- |
| Add the 74th credential's link | Fill in the last `[[certifications]]` entry and remove `pending = true`. Keep it in lightest-to-heaviest order: the build refuses a list that is out of order. |
| Add certificate PDFs | Save them as `certificates/<id>.pdf` (ids are listed in the vault index) and rebuild. The vault index links each PDF automatically. |
| Add a project card | Add a `[[projects]]` entry (`tier = "featured"`, `group = "agents"` or `"products"`), rebuild, then add its card to the matching grid in `README.md`. |
| Change a headline number | `[[metrics]]` for the hero; the README text repeats a few numbers, so search it too. |

## Publish checklist

- Preview the README in GitHub's light and dark themes, and on a phone.
- Pin `NexusRAG`, `Anupam_Roy`, `cutline`, `food-bank-recall-closure-agent`, `raceproof` and `pantryproof`, in that order, so the pinned cards echo the page.
- Use the portfolio, `https://anupam-roy.vercel.app/`, as the website field on the GitHub profile.

## Design notes

- **One thesis, proven repeatedly:** the page argues that AI should prove its work, and every section links to the repository or issuer page that proves it.
- **Evidence levels are kept honest:** test counts are labelled as counted in the repository unless they were run for a release; live links are included only where the project itself lists one and it is not known to expose a key.
- **Theme-aware and accessible:** every themed image has light and dark variants, full alt text and a reduced-motion fallback. Text is measured with a wide fallback font so it fits on any OS.
- **No third-party widgets:** nothing on the page depends on a stats service that can rate-limit or go down.
