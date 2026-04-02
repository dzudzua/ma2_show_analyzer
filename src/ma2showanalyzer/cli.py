from __future__ import annotations

import argparse
from pathlib import Path

from .parser import XMLShowParser
from .reporters import ReportWriter
from .webapp import main as web_main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="grandMA2 XML Show Analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze an export folder")
    analyze.add_argument("--input", required=True, type=Path, help="Input folder with XML exports")
    analyze.add_argument("--output", required=True, type=Path, help="Output folder for reports")
    analyze.add_argument("--recursive", action="store_true", help="Recursively search for XML files")
    analyze.add_argument("--glob", default="*.xml", help="Glob pattern for XML files")

    serve = sub.add_parser("serve", help="Run local web server for uploads and report generation")
    serve.add_argument("--host", default="127.0.0.1", help="Bind host")
    serve.add_argument("--port", default=8765, type=int, help="Bind port")
    serve.add_argument("--data-dir", default="web_jobs", type=Path, help="Directory for uploaded jobs")
    serve.add_argument("--open-browser", action="store_true", help="Open default browser after server start")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        xml_parser = XMLShowParser()
        show = xml_parser.parse_folder(args.input, recursive=args.recursive, glob=args.glob)
        reporter = ReportWriter()
        reporter.write_all(show, args.output)
        print(f"Analysis complete. Output written to: {args.output}")
        return 0

    if args.command == "serve":
        return web_main(
            [
                "--host",
                args.host,
                "--port",
                str(args.port),
                "--data-dir",
                str(args.data_dir),
                *(["--open-browser"] if args.open_browser else []),
            ]
        )

    parser.error("Unknown command")
    return 2
