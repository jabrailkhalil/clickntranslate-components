# Repository rules

- Author/committer: jabrailkhalil <78273416+jabrailkhalil@users.noreply.github.com>.
- Use task-based branch names without assistant/tool prefixes.
- Never commit private keys. CI receives snapshot/timestamp keys only; root/targets remain with the maintainer.
- A discovered upstream version is a candidate, not an approved update.
- Do not claim native or frozen-app checks that were not run.
- Keep stable catalogs unchanged until their exact artifact bytes pass release checks.
- Never replace an existing released artifact under the same name.
