from fastapi import APIRouter, Depends

from services import vpn, system
from routers.auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
async def stats_overview(user=Depends(get_current_user)):
    status = await vpn.get_status()
    sys_info = system.get_system_info()
    transfer = await vpn.get_transfer_stats()

    total_rx = sum(t["rx_bytes"] for t in transfer)
    total_tx = sum(t["tx_bytes"] for t in transfer)

    return {
        "server": status,
        "system": sys_info,
        "traffic": {
            "total_rx": total_rx,
            "total_tx": total_tx,
            "total_rx_fmt": system.format_bytes(total_rx),
            "total_tx_fmt": system.format_bytes(total_tx),
        },
        "uptime_fmt": system.format_uptime(sys_info["uptime"]),
    }


@router.get("/traffic")
async def traffic_stats(user=Depends(get_current_user)):
    db = await get_db()
    cursor = await db.execute(
        """SELECT ts.*, c.name FROM traffic_stats ts
           LEFT JOIN clients c ON ts.client_id = c.id
           ORDER BY ts.recorded_at DESC LIMIT 100"""
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/clients")
async def client_stats(user=Depends(get_current_user)):
    transfer = await vpn.get_transfer_stats()
    handshakes = await vpn.get_handshakes()
    db = await get_db()

    result = []
    for t in transfer:
        cursor = await db.execute("SELECT name FROM clients WHERE public_key = ?", (t["public_key"],))
        row = await cursor.fetchone()
        name = row["name"] if row else "Unknown"
        result.append({
            "name": name,
            "public_key": t["public_key"],
            "rx_bytes": t["rx_bytes"],
            "tx_bytes": t["tx_bytes"],
            "rx_fmt": system.format_bytes(t["rx_bytes"]),
            "tx_fmt": system.format_bytes(t["tx_bytes"]),
            "last_handshake_ago": handshakes.get(t["public_key"]),
            "is_active": handshakes.get(t["public_key"], 999) < 180,
        })
    return sorted(result, key=lambda x: x["rx_bytes"] + x["tx_bytes"], reverse=True)


@router.get("/system")
async def system_info(user=Depends(get_current_user)):
    info = system.get_system_info()
    info["ram_total_fmt"] = system.format_bytes(info["ram_total"])
    info["ram_used_fmt"] = system.format_bytes(info["ram_used"])
    info["disk_total_fmt"] = system.format_bytes(info["disk_total"])
    info["disk_used_fmt"] = system.format_bytes(info["disk_used"])
    info["network_rx_fmt"] = system.format_bytes(info["network_rx"])
    info["network_tx_fmt"] = system.format_bytes(info["network_tx"])
    info["uptime_fmt"] = system.format_uptime(info["uptime"])
    return info
