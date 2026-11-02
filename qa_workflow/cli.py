import argparse
import json
from .workflow import run, run_path, approve, export_approved


def main():
    parser = argparse.ArgumentParser(
        description="Reviewed QA workflow with explicit offline and live modes"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("run")
    start.add_argument("--mode", choices=["offline", "ollama"], default="offline")
    start.add_argument("--model", default="qwen3:4b")
    start.add_argument("--base-url", default="http://127.0.0.1:11434")
    start.add_argument("--seeded-bug", action="store_true")
    review = sub.add_parser("approve")
    review.add_argument("run_id")
    review.add_argument("--reviewer", required=True)
    export = sub.add_parser("export")
    export.add_argument("run_id")
    args = parser.parse_args()
    if args.command == "run":
        result = run(args.mode, args.model, args.base_url, args.seeded_bug)
        print(json.dumps(result, indent=2))
        if result["passed"] != result["total"]:
            raise SystemExit(1)
    elif args.command == "approve":
        print((run_path(args.run_id) / "draft-report.md").read_text())
        confirmation = input("Type the run id to confirm you reviewed this evidence: ")
        if confirmation != args.run_id:
            raise SystemExit("Approval cancelled")
        print(approve(args.run_id, args.reviewer))
    else:
        print(export_approved(args.run_id))


if __name__ == "__main__":
    main()
