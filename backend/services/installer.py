import asyncio
from pathlib import Path

INSTALL_LOG = Path("/tmp/vpn_panel_install.log")
_install_progress = {"running": False, "current": 0, "total": 0, "message": "", "error": None}


async def run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode or 0, stdout.decode(), stderr.decode()


async def progress_callback(current: int, total: int, message: str):
    _install_progress["current"] = current
    _install_progress["total"] = total
    _install_progress["message"] = message
    with open(INSTALL_LOG, "a") as f:
        f.write(f"[{current}/{total}] {message}\n")


async def install_amneziawg() -> bool:
    _install_progress.update(running=True, current=0, total=5, message="Starting...", error=None)

    steps = [
        ("Updating package list", ["apt-get", "update", "-y"]),
        ("Installing dependencies", ["apt-get", "install", "-y", "curl", "ca-certificates", "gnupg", "lsb-release", "qrencode"]),
        ("Adding AmneziaWG repository", None),
        ("Installing amneziawg-tools", ["apt-get", "install", "-y", "amneziawg"]),
        ("Creating wireguard directory", ["mkdir", "-p", "/etc/wireguard"]),
    ]

    try:
        for i, (desc, cmd) in enumerate(steps):
            await progress_callback(i, len(steps), desc)

            if cmd:
                code, _, stderr = await run_cmd(cmd)
                if code != 0:
                    raise RuntimeError(f"Step '{desc}' failed: {stderr}")
            else:
                repo_script = """
                curl -fsSL https://deb.debian.org/debian/pool/main/a/amneziawg/amneziawg.gpg.key | gpg --dearmor -o /usr/share/keyrings/amneziawg.gpg 2>/dev/null
                echo "deb [signed-by=/usr/share/keyrings/amneziawg.gpg] https://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/amneziawg.list
                apt-get update -y
                """
                code, _, stderr = await run_cmd(["bash", "-c", repo_script])
                if code != 0:
                    raise RuntimeError(f"Failed to add repo: {stderr}")

        await progress_callback(len(steps), len(steps), "Installation complete")
        return True
    except Exception as e:
        _install_progress["error"] = str(e)
        _install_progress["message"] = f"Error: {e}"
        return False
    finally:
        _install_progress["running"] = False


def get_install_progress() -> dict:
    return _install_progress.copy()
