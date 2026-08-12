from hohokhan.runtime import ensure_runtime

if __name__ == "__main__":
    try:
        ensure_runtime()
    except RuntimeError as exc:
        raise SystemExit(f"Runtime error: {exc}") from exc

    from hohokhan.app import run

    run()
