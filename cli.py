"""CMMC Control Mapper CLI."""
import argparse
import json
import sys
from pathlib import Path
from src.cmmc_mapper.mapper import (
    load_controls, get_controls_by_domain, get_controls_by_level,
    get_control_by_id, get_domain_summary, search_controls, DOMAINS
)
from src.cmmc_mapper.oscal_export import export_oscal_json

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
    RICH = True
except ImportError:
    RICH = False

console = Console() if RICH else None


def cmd_list(args):
    controls = get_controls_by_level(args.level)
    if args.domain:
        controls = [c for c in controls if args.domain.lower() in c["domain"].lower()]

    if RICH:
        table = Table(title=f"CMMC Level {args.level} Controls ({len(controls)} total)", show_lines=True)
        table.add_column("ID", style="cyan bold", width=20)
        table.add_column("Domain", style="magenta", width=28)
        table.add_column("AWS Services", style="green", width=36)
        table.add_column("NIST", style="yellow", width=18)
        for c in controls:
            table.add_row(
                c["id"],
                c["domain"],
                "\n".join(c.get("aws_services", [])),
                ", ".join(c.get("nist_mapping", [])),
            )
        console.print(table)
    else:
        for c in controls:
            print(f"{c['id']} | {c['domain']} | {', '.join(c.get('aws_services', []))}")


def cmd_summary(args):
    summary = get_domain_summary()
    if RICH:
        table = Table(title="CMMC Domain Summary", show_lines=True)
        table.add_column("Domain", style="cyan bold", width=34)
        table.add_column("L1", justify="center", style="green", width=6)
        table.add_column("L2", justify="center", style="yellow", width=6)
        table.add_column("Total", justify="center", style="magenta bold", width=7)
        table.add_column("AWS Services", style="blue", width=8)
        for row in summary:
            table.add_row(
                row["domain"],
                str(row["level_1"]),
                str(row["level_2"]),
                str(row["total"]),
                str(row["aws_service_count"]),
            )
        console.print(table)
    else:
        for row in summary:
            print(f"{row['domain']}: L1={row['level_1']} L2={row['level_2']} Total={row['total']}")


def cmd_detail(args):
    control = get_control_by_id(args.id)
    if not control:
        print(f"Control {args.id} not found.")
        sys.exit(1)
    if RICH:
        content = f"""[cyan bold]{control['id']}[/cyan bold] — {control['domain']}
[white]{control['practice']}[/white]

[yellow]NIST Mappings:[/yellow] {', '.join(control.get('nist_mapping', []))}
[green]AWS Services:[/green]
""" + "\n".join(f"  • {s}" for s in control.get("aws_services", [])) + f"""

[blue]AWS Config Rules:[/blue]
""" + "\n".join(f"  • {r}" for r in control.get("aws_config_rules", [])) if control.get("aws_config_rules") else "  None"
        console.print(Panel(content, title="Control Detail", border_style="cyan"))
    else:
        print(json.dumps(control, indent=2))


def cmd_search(args):
    results = search_controls(args.query)
    print(f"Found {len(results)} controls matching '{args.query}':")
    for c in results:
        print(f"  {c['id']} | {c['domain']}")


def cmd_export(args):
    output = args.output or f"cmmc_oscal_level{args.level}.json"
    path = export_oscal_json(output, level=args.level, organization=args.org)
    print(f"OSCAL Component Definition exported to: {path}")


def main():
    parser = argparse.ArgumentParser(
        prog="cmmc-mapper",
        description="CMMC 2.0 Control Mapper — maps CMMC practices to AWS services and OSCAL output",
    )
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List CMMC controls")
    p_list.add_argument("--level", type=int, choices=[1, 2], default=2, help="CMMC level (default: 2)")
    p_list.add_argument("--domain", help="Filter by domain name")
    p_list.set_defaults(func=cmd_list)

    # summary
    p_summary = sub.add_parser("summary", help="Show domain summary")
    p_summary.set_defaults(func=cmd_summary)

    # detail
    p_detail = sub.add_parser("detail", help="Show detail for a specific control")
    p_detail.add_argument("id", help="Control ID (e.g. AC.L2-3.1.3)")
    p_detail.set_defaults(func=cmd_detail)

    # search
    p_search = sub.add_parser("search", help="Search controls by keyword")
    p_search.add_argument("query", help="Search term")
    p_search.set_defaults(func=cmd_search)

    # export
    p_export = sub.add_parser("export", help="Export OSCAL Component Definition JSON")
    p_export.add_argument("--level", type=int, choices=[1, 2], default=2)
    p_export.add_argument("--output", help="Output file path")
    p_export.add_argument("--org", default="My Organization", help="Organization name")
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
