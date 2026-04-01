import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("smoke-urls.json")
EXAMPLE_CONFIG_PATH = Path(__file__).with_name("smoke-urls.example.json")


def read_json(url: str) -> dict:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def post_stream(url: str, payload: dict) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        buffer = ""

        for chunk in iter(lambda: response.read(1024), b""):
            buffer += chunk.decode("utf-8", errors="replace")

            while "\n\n" in buffer:
                frame, buffer = buffer.split("\n\n", 1)
                if not frame.startswith("data: "):
                    continue

                payload = json.loads(frame[6:])
                status = payload.get("status", "unknown")
                message = payload.get("message") or payload.get("log") or ""

                if status in {"completed", "error"}:
                    return status, message

    return "error", "Stream ended without a terminal event."


def load_urls(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(
            f"Smoke URL config not found at {path}. Copy {EXAMPLE_CONFIG_PATH.name} to {path.name} and fill the URLs you want to test."
        )

    data = json.loads(path.read_text(encoding="utf-8"))
    return {key: value for key, value in data.items() if value}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run manual integration smoke checks against the local backend.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Backend base URL, default: http://127.0.0.1:8000")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to JSON config containing manual smoke URLs.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)

    try:
        urls = load_urls(config_path)
    except FileNotFoundError as exc:
        print(exc)
        return 1

    if not urls:
        print("No smoke URLs configured. Add one or more URLs to the config before running manual smoke.")
        return 1

    preflight = read_json(f"{args.base_url}/api/health/preflight")
    print(f"Preflight: {preflight['status']} - {preflight.get('status_message', '')}")

    for name, details in preflight.get("checks", {}).items():
        if not details.get("ok"):
            print(f"  ! {name}: {details.get('hint', 'not ready')}")

    exit_code = 0

    for platform, url in urls.items():
        print(f"\n[{platform}] {url}")
        try:
            status, message = post_stream(
                f"{args.base_url}/api/download/",
                {"url": url, "quality": "1", "format": "mp4"},
            )
            print(f"  -> {status}: {message}")
            if status != "completed":
                exit_code = 1
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"  -> http_error {exc.code}: {body}")
            exit_code = 1
        except urllib.error.URLError as exc:
            print(f"  -> network_error: {exc.reason}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
