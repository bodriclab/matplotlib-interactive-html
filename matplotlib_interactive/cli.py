"""Command-line interface for matplotlib-interactive-html."""

from __future__ import annotations

import argparse
import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path


def _serve(args: argparse.Namespace) -> int:
    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        print(f"Error: directory not found: {directory}", file=sys.stderr)
        return 1

    handler = lambda *handler_args, **handler_kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *handler_args,
        directory=str(directory),
        **handler_kwargs,
    )

    with socketserver.ThreadingTCPServer((args.host, args.port), handler) as httpd:
        url = f"http://{args.host}:{args.port}/"
        print(f"Serving {directory} at {url}")
        print("Press Ctrl+C to stop.")
        if args.open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``matplotlib-interactive`` console script."""
    parser = argparse.ArgumentParser(
        prog="matplotlib-interactive",
        description="Tools for matplotlib-interactive-html generated pages.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser(
        "serve",
        help="Optional: serve a directory over HTTP (for videos/iframes blocked by file://).",
    )
    serve_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to serve (default: current directory).",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind (default: 127.0.0.1).",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind (default: 8000).",
    )
    serve_parser.add_argument(
        "--open",
        action="store_true",
        help="Open the served URL in the default browser.",
    )
    serve_parser.set_defaults(func=_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
