#!/usr/bin/env python3
"""Generate a single Ruantiblock list from categorized domains and IPv4/CIDR."""
from __future__ import annotations
import argparse
import ipaddress
import re
from pathlib import Path

LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

def domain_name(value: str) -> str:
    name = value.rstrip(".").encode("idna").decode("ascii").lower()
    if len(name) > 253 or len(name.split(".")) < 2 or any(not LABEL.fullmatch(x) for x in name.split(".")):
        raise ValueError(f"Invalid domain: {value}")
    return name

def build(root: Path, combined: Path, domains_path: Path, ips_path: Path) -> tuple[int, int]:
    approved = set()
    approval = root.parent / "config" / "approved-broad-cidrs.txt"
    if approval.exists():
        for line in approval.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                approved.add(ipaddress.IPv4Network(line, strict=True))
    domains = {}
    groups = []
    networks = []
    for path in sorted(root.rglob("*.txt")):
        records = []
        for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                parts = line.split()
                if len(parts) != 1:
                    raise ValueError("Only a single domain or IPv4/CIDR per line is allowed")
                value = parts[0]
                try:
                    network = ipaddress.IPv4Network(value, strict=True)
                except ValueError:
                    if "/" in value or ":" in value or (value.count(".")==3 and all(x.isdigit() for x in value.split("."))):
                        raise ValueError(f"Invalid IPv4/CIDR: {value}")
                    name = domain_name(value)
                    if name not in domains:
                        domains[name] = path
                        records.append(name)
                else:
                    if network.prefixlen <= 16 and network not in approved:
                        raise ValueError(f"Wide range must be approved: {network}")
                    networks.append(network)
            except ValueError as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
        if records:
            groups.append((path.relative_to(root).with_suffix("").as_posix(), records))
    redundant = set()
    for domain in domains:
        parts = domain.split(".")
        if any(".".join(parts[i:]) in domains for i in range(1,len(parts)-1)):
            redundant.add(domain)
    header = ["# Ruantiblock — automatically generated.", "# Edit lists/**/*.txt, not this file."]
    domain_lines = []
    for group, records in groups:
        values = [d for d in records if d not in redundant]
        if values:
            domain_lines.extend(["", "# " + group, *values])
    nets = sorted(ipaddress.collapse_addresses(networks), key=lambda n: (int(n.network_address),n.prefixlen))
    ip_lines = ["", "# IPv4 / CIDR"] + [str(n.network_address) if n.prefixlen==32 else str(n) for n in nets]
    for target, lines in ((combined,domain_lines+ip_lines), (domains_path,domain_lines), (ips_path,ip_lines)):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(header+lines)+"\n", encoding="utf-8")
    return len(domains)-len(redundant), len(nets)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("lists"))
    parser.add_argument("--output", type=Path, default=Path("all.txt"))
    parser.add_argument("--domains-output", type=Path, default=Path("domains.txt"))
    parser.add_argument("--ips-output", type=Path, default=Path("ips.txt"))
    args = parser.parse_args()
    domains, ranges = build(args.source,args.output,args.domains_output,args.ips_output)
    print(f"Generated: {domains} domains, {ranges} IP ranges")

if __name__ == "__main__":
    main()
