#!/usr/bin/env python3
"""Regenerate the Managed Artifacts table on projects/agentworks-bom.mdx from a BOM POM.

The table must reflect the BOM's dependencyManagement exactly. Portfolio members are the
io.github.markpollack and com.agentclientprotocol entries; every other managed dependency is
a third-party version pin (jackson, reactor, spring-ai, mockito, junit, ...) and is
deliberately excluded from the published table.

Usage:
    python3 scripts/generate_bom_table.py 1.18.0            # print the table
    python3 scripts/generate_bom_table.py 1.18.0 --apply    # rewrite the .mdx section
    python3 scripts/generate_bom_table.py 1.18.0 --verify   # fetch every member POM, require 200

On a BOM bump the diff should be nothing but version cells (plus any added/removed member),
so run with --apply and review the diff rather than hand-editing rows.
"""

import argparse
import pathlib
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

CENTRAL = "https://repo1.maven.org/maven2"
NS = {"m": "http://maven.apache.org/POM/4.0.0"}

MEMBER_GROUPS = ("io.github.markpollack", "com.agentclientprotocol")

# Section heading -> groupId, in the order the page presents them.
SECTIONS = [
    ("Agent Engineering (io.github.markpollack)", "io.github.markpollack"),
    ("Agent Client Protocol (com.agentclientprotocol)", "com.agentclientprotocol"),
]

# artifactId -> (display name, project page). Ordered: first matching rule wins.
PROJECT_RULES = [
    (re.compile(r"^agent-hooks-"), "Agent Hooks", "/projects/agent-hooks"),
    (re.compile(r"^(journal-core|.*-cli-capture|claude-code-capture)$"), "Agent Journal", "/projects/agent-journal"),
    (re.compile(r"^workflow-"), "Agent Workflow", "/projects/agent-workflow"),
    (re.compile(r"^experiment-"), "Agent Experiment", "/projects/agent-experiment"),
    (re.compile(r"^memory-"), "Agent Memory", "/projects/agent-memory"),
    (re.compile(r"^acp-"), "ACP Java SDK", "/projects/acp-java-sdk"),
    (re.compile(r"^claude-code-sdk$"), "Claude Agent SDK", "/projects/claude-agent-sdk"),
    (re.compile(r"^agent-bench-"), "Agent Bench", "/projects/agent-bench"),
    (re.compile(r"^agent-judge-"), "Agent Judge", "/projects/agent-judge"),
    (re.compile(r"^agent-sandbox-"), "Agent Sandbox", "/projects/agent-sandbox"),
    # Everything else in the member groups belongs to the Agent Client family:
    # agent-client-*, agent-model, agent-<provider>, <provider>-cli-sdk, agent-starter-*.
    (re.compile(r"."), "Agent Client", "/projects/agent-client"),
]

MDX = pathlib.Path(__file__).resolve().parent.parent / "projects" / "agentworks-bom.mdx"
START_MARKER = "## Managed Artifacts"
END_MARKER = "## Source"


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def http_status(url: str) -> int:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def pom_url(group: str, artifact: str, version: str) -> str:
    return f"{CENTRAL}/{group.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}.pom"


def resolve(value: str, props: dict) -> str:
    seen = 0
    while "${" in value and seen < 10:
        value = re.sub(r"\$\{([^}]+)\}", lambda m: props.get(m.group(1), m.group(0)), value)
        seen += 1
    return value


def managed_dependencies(version: str):
    """Return (members, third_party) as lists of (groupId, artifactId, version)."""
    root = ET.fromstring(fetch(pom_url("io.github.markpollack", "agentworks-bom", version)))
    props = {}
    props_el = root.find("m:properties", NS)
    if props_el is not None:
        for child in props_el:
            props[child.tag.split("}")[-1]] = (child.text or "").strip()

    members, third_party = [], []
    deps = root.find("m:dependencyManagement/m:dependencies", NS)
    if deps is None:
        sys.exit(f"agentworks-bom {version} has no dependencyManagement")
    for dep in deps.findall("m:dependency", NS):
        group = dep.findtext("m:groupId", namespaces=NS).strip()
        artifact = dep.findtext("m:artifactId", namespaces=NS).strip()
        ver = resolve(dep.findtext("m:version", namespaces=NS).strip(), props)
        (members if group in MEMBER_GROUPS else third_party).append((group, artifact, ver))
    return members, third_party


def project_for(artifact: str):
    for pattern, name, href in PROJECT_RULES:
        if pattern.search(artifact):
            return name, href
    raise AssertionError(artifact)


def render(members) -> str:
    out = [START_MARKER, ""]
    for heading, group in SECTIONS:
        rows = [m for m in members if m[0] == group]
        if not rows:
            continue
        out += [f"### {heading}", "", "| Artifact | Version | Project |", "|----------|---------|---------|"]
        for _, artifact, version in rows:
            name, href = project_for(artifact)
            out.append(f"| `{artifact}` | {version} | [{name}]({href}) |")
        out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bom_version")
    parser.add_argument("--apply", action="store_true", help="rewrite the section in the .mdx")
    parser.add_argument("--verify", action="store_true", help="fetch every member POM and require HTTP 200")
    args = parser.parse_args()

    members, third_party = managed_dependencies(args.bom_version)
    print(
        f"agentworks-bom {args.bom_version}: {len(members) + len(third_party)} managed dependencies "
        f"= {len(members)} portfolio members + {len(third_party)} third-party pins",
        file=sys.stderr,
    )

    if args.verify:
        bad = []
        for group, artifact, version in members:
            status = http_status(pom_url(group, artifact, version))
            if status != 200:
                bad.append((group, artifact, version, status))
            print(f"{status} {group}:{artifact}:{version}", file=sys.stderr)
        if bad:
            for row in bad:
                print(f"FAIL {row}", file=sys.stderr)
            return 1
        print(f"OK: {len(members)}/{len(members)} member POMs returned HTTP 200", file=sys.stderr)

    table = render(members)

    if not args.apply:
        print(table)
        return 0

    text = MDX.read_text()
    start = text.index(START_MARKER)
    end = text.index(END_MARKER, start)
    MDX.write_text(text[:start] + table + "\n" + text[end:])
    print(f"rewrote {MDX} with {len(members)} member rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
