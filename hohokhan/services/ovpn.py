from __future__ import annotations

import asyncio
import ipaddress
import socket
from pathlib import Path


async def _resolve_public_ip(hostname: str) -> str:
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        loop = asyncio.get_running_loop()
        records = await loop.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        addresses = [record[4][0] for record in records]
        if not addresses:
            raise ValueError("دامنه داخل فایل resolve نشد") from None
        ip = ipaddress.ip_address(addresses[0])

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
        raise ValueError("برای امنیت، تبدیل به IP خصوصی/رزروشده مجاز نیست")
    return str(ip)


async def replace_remote_hosts(source: Path, destination: Path) -> list[tuple[str, str]]:
    """Replace only OpenVPN `remote host port` hostname tokens with public IPs."""
    raw = source.read_text(encoding="utf-8", errors="strict")
    lines = raw.splitlines(keepends=True)
    replacements: list[tuple[str, str]] = []
    result: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            result.append(line)
            continue
        parts = stripped.split()
        if len(parts) >= 2 and parts[0].lower() == "remote":
            hostname = parts[1]
            ip = await _resolve_public_ip(hostname)
            parts[1] = ip
            indentation = line[: len(line) - len(line.lstrip())]
            newline = "\n" if line.endswith("\n") else ""
            result.append(indentation + " ".join(parts) + newline)
            replacements.append((hostname, ip))
        else:
            result.append(line)

    if not replacements:
        raise ValueError("دستور remote معتبری در فایل پیدا نشد")
    destination.write_text("".join(result), encoding="utf-8")
    return replacements
