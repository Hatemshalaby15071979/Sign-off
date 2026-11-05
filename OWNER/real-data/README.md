# NEVER commit real client data

This folder is for real client CSV exports during a live engagement only.

Rules (all enforced by `.gitignore`, `.dockerignore`, and `docs/THREAT-MODEL.md`):

1. **Never commit anything under this folder.** `OWNER/real-data/*` is
   git-ignored except this README.
2. **Never bake real data into a Docker image.** `.dockerignore` excludes the
   folder, and any `*.csv` under `OWNER/`.
3. **Run on the customer's machine.** The whole product is offline for a
   reason: their exports stay on their hardware. Best practice is to run
   Signoff on the customer's own machine, with their data mounted read-only.
4. **No data leaves the machine.** Signoff writes outputs only into the
   `--out` directory you give it, uses no network, logs no file contents, and
   never embeds absolute host paths in artifacts.
5. **Deliver the pack, not data.** The signed dossier carries evidence IDs and
   relative source paths, so the pack can reference the customer's records
   without containing wholesale copies beyond what the pack itself shows.
