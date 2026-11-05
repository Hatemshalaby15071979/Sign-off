# Offline Guarantee

Signoff's evidence path uses Python's standard library and pinned `fpdf2==2.8.4`; XLSX questionnaire support is an optional pinned `openpyxl==3.1.5` extra. It makes no runtime network requests, uses no LLM, stores no credentials, and has no telemetry or server component. Inputs are read locally and artifacts are written to the requested output directory.

The guarantee applies to Signoff's runtime code. Installing Python packages or building the Docker image may require a package cache or network access beforehand. Operators can build/pull dependencies in a controlled environment, then run the container without networking:

```sh
docker run --network none --rm -v "$PWD/out:/out" signoff:latest python -m signoff demo --out /out/demo
```

`scripts/check-offline.py` statically scans runtime source for disallowed network and model imports/calls. Static scanning is evidence of code structure, not a general proof about the host or interpreter.
