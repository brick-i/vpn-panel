import subprocess
import asyncio
import ipaddress
from pathlib import Path

INTERFACE = "awg0"
WG_QUICK_CONF = Path("/etc/wireguard/awg0.conf")


async def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode or 0, stdout.decode(), stderr.decode()


async def is_installed() -> bool:
    code, _, _ = await run_cmd(["which", "awg"])
    return code == 0


async def is_running() -> bool:
    code, stdout, _ = await run_cmd(["awg", "show", INTERFACE])
    return code == 0 and "interface" in stdout.lower()


async def get_status() -> dict:
    installed = await is_installed()
    running = await is_running() if installed else False
    connected = 0
    if running:
        code, stdout, _ = await run_cmd(["awg", "show", INTERFACE, "latest-handshakes"])
        if code == 0 and stdout.strip():
            import time
            now = time.time()
            for line in stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        ts = int(parts[1])
                        if now - ts < 180:  # active within 3 min
                            connected += 1
                    except ValueError:
                        pass
    return {
        "installed": installed,
        "running": running,
        "interface": INTERFACE,
        "connected_clients": connected,
    }


async def get_transfer_stats() -> list[dict]:
    if not await is_running():
        return []
    code, stdout, _ = await run_cmd(["awg", "show", INTERFACE, "transfer"])
    if code != 0:
        return []
    results = []
    for line in stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 3:
            results.append({
                "public_key": parts[0],
                "rx_bytes": int(parts[1]),
                "tx_bytes": int(parts[2]),
            })
    return results


async def get_handshakes() -> dict[str, int]:
    if not await is_running():
        return {}
    code, stdout, _ = await run_cmd(["awg", "show", INTERFACE, "latest-handshakes"])
    if code != 0:
        return {}
    import time
    now = time.time()
    result = {}
    for line in stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                result[parts[0]] = now - int(parts[1])
            except ValueError:
                pass
    return result


async def generate_keypair() -> tuple[str, str]:
    code, privkey, _ = await run_cmd(["wg", "genkey"])
    if code != 0:
        raise RuntimeError("Failed to generate private key")
    privkey = privkey.strip()
    proc = await asyncio.create_subprocess_shell(
        f"echo '{privkey}' | wg pubkey",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    pubkey = stdout.decode().strip()
    return privkey, pubkey


async def generate_psk() -> str:
    code, psk, _ = await run_cmd(["wg", "genpsk"])
    if code != 0:
        raise RuntimeError("Failed to generate PSK")
    return psk.strip()


def get_next_ip(existing_ips: list[str]) -> str:
    network = ipaddress.IPv4Network("10.0.0.0/24")
    used = {ipaddress.IPv4Address(ip) for ip in existing_ips}
    for host in network.hosts():
        if host not in used and str(host) != "10.0.0.1":
            return str(host)
    raise RuntimeError("No available IPs in 10.0.0.0/24")


async def add_peer(public_key: str, allowed_ips: str, dns: str = "1.1.1.1", endpoint: str = ""):
    cmd = ["awg", "set", INTERFACE, "peer", public_key, "allowed-ips", allowed_ips]
    if endpoint:
        cmd.extend(["endpoint", endpoint])
    code, _, stderr = await run_cmd(cmd)
    if code != 0:
        raise RuntimeError(f"Failed to add peer: {stderr}")


async def remove_peer(public_key: str):
    code, _, stderr = await run_cmd(["awg", "set", INTERFACE, "peer", public_key, "remove"])
    if code != 0:
        raise RuntimeError(f"Failed to remove peer: {stderr}")


async def apply_config(clients: list[dict], config: dict):
    lines = [
        "[Interface]",
        f"Address = 10.0.0.1/24",
        f"ListenPort = {config.get('listen_port', 51820)}",
        f"PrivateKey = <SERVER_PRIVATE_KEY>",
        "",
    ]
    if config.get("dns"):
        lines.append(f"DNS = {config['dns']}")

    obfs_params = []
    for key in ["jc", "jmin", "jmax", "s1", "s2", "h1", "h2", "h3", "h4"]:
        val = int(config.get(key, 0))
        if val > 0:
            obfs_params.append(f"{key.upper()} = {val}")
    if obfs_params:
        lines.append("# AmneziaWG obfuscation")
        lines.extend(obfs_params)

    for client in clients:
        if not client.get("is_active"):
            continue
        lines.extend([
            "",
            f"# {client['name']}",
            "[Peer]",
            f"PublicKey = {client['public_key']}",
            f"AllowedIPs = {client['ip_address']}/32",
        ])

    return "\n".join(lines)


async def start_vpn():
    code, _, stderr = await run_cmd(["wg-quick", "up", INTERFACE])
    if code != 0:
        raise RuntimeError(f"Failed to start: {stderr}")


async def stop_vpn():
    code, _, stderr = await run_cmd(["wg-quick", "down", INTERFACE])
    if code != 0:
        raise RuntimeError(f"Failed to stop: {stderr}")


async def restart_vpn():
    await stop_vpn()
    await start_vpn()


async def install_amneziawg(progress_callback=None) -> bool:
    steps = [
        ("Updating package list", ["apt-get", "update", "-y"]),
        ("Installing dependencies", ["apt-get", "install", "-y", "curl", "ca-certificates", "gnupg", "lsb-release"]),
        ("Adding AmneziaWG repository", None),  # special
        ("Installing amneziawg-tools", ["apt-get", "install", "-y", "amneziawg"]),
        ("Creating wireguard directory", ["mkdir", "-p", "/etc/wireguard"]),
    ]

    for i, (desc, cmd) in enumerate(steps):
        if progress_callback:
            await progress_callback(i, len(steps), desc)

        if cmd:
            code, _, stderr = await run_cmd(cmd)
            if code != 0:
                raise RuntimeError(f"Step '{desc}' failed: {stderr}")
        else:
            # Add repo step
            repo_script = """
            curl -fsSL https://deb.debian.org/debian/pool/main/a/amneziawg/amneziawg.gpg.key | gpg --dearmor -o /usr/share/keyrings/amneziawg.gpg
            echo "deb [signed-by=/usr/share/keyrings/amneziawg.gpg] https://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/amneziawg.list
            """
            code, _, stderr = await run_cmd(["bash", "-c", repo_script])
            if code != 0:
                raise RuntimeError(f"Failed to add repo: {stderr}")

    if progress_callback:
        await progress_callback(len(steps), len(steps), "Installation complete")
    return True
