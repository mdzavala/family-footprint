# Contributing

Thanks for helping families stay safer online.

- Keep the CLI contract and the findings format stable (see `docs/data-model.md`).
- `python -m unittest discover tests` must pass. Privacy tests are not optional.
- Never add real personal data. New test data must be fictional, use `example.*` domains,
  and place any coordinates at sea.
- New detectors go in `footprint/detectors/` and are registered in `DETECTORS`.
- If you add a real-world data source, add its terms of use and a legal note to the PR.

By contributing, you agree that your contributions are licensed under Apache 2.0.
