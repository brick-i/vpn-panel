from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from models import ClientCreate, ClientUpdate
from services import vpn
from routers.auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("")
async def list_clients(user=Depends(get_current_user)):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM clients ORDER BY created_at DESC")
    rows = await cursor.fetchall()

    handshakes = await vpn.get_handshakes()
    transfer = await vpn.get_transfer_stats()
    transfer_map = {t["public_key"]: t for t in transfer}

    result = []
    for row in rows:
        pk = row["public_key"]
        result.append({
            "id": row["id"],
            "name": row["name"],
            "public_key": pk,
            "ip_address": row["ip_address"],
            "allowed_ips": row["allowed_ips"],
            "dns": row["dns"],
            "is_active": bool(row["is_active"]),
            "expires_at": row["expires_at"],
            "created_at": row["created_at"],
            "last_handshake": handshakes.get(pk),
            "rx_bytes": transfer_map.get(pk, {}).get("rx_bytes", 0),
            "tx_bytes": transfer_map.get(pk, {}).get("tx_bytes", 0),
        })
    return result


@router.post("")
async def create_client(data: ClientCreate, user=Depends(get_current_user)):
    db = await get_db()

    # Get existing IPs
    cursor = await db.execute("SELECT ip_address FROM clients")
    rows = await cursor.fetchall()
    existing_ips = [r["ip_address"] for r in rows]

    ip = vpn.get_next_ip(existing_ips)
    privkey, pubkey = await vpn.generate_keypair()

    await db.execute(
        """INSERT INTO clients (name, public_key, private_key, ip_address, allowed_ips, dns, expires_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (data.name, pubkey, privkey, ip, data.allowed_ips, data.dns, data.expires_at),
    )
    await db.commit()

    # Add peer to running interface
    if await vpn.is_running():
        try:
            await vpn.add_peer(pubkey, f"{ip}/32", data.dns.split(",")[0].strip())
        except RuntimeError:
            pass

    return {
        "id": (await db.execute("SELECT last_insert_rowid()")).fetchone()[0],
        "name": data.name,
        "public_key": pubkey,
        "private_key": privkey,
        "ip_address": ip,
    }


@router.get("/{client_id}")
async def get_client(client_id: int, user=Depends(get_current_user)):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Client not found")
    return dict(row)


@router.put("/{client_id}")
async def update_client(client_id: int, data: ClientUpdate, user=Depends(get_current_user)):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Client not found")

    updates = data.model_dump(exclude_none=True)
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [client_id]
        await db.execute(f"UPDATE clients SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        await db.commit()
    return {"message": "Client updated"}


@router.delete("/{client_id}")
async def delete_client(client_id: int, user=Depends(get_current_user)):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Client not found")

    # Remove from running interface
    if await vpn.is_running():
        try:
            await vpn.remove_peer(row["public_key"])
        except RuntimeError:
            pass

    await db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    await db.commit()
    return {"message": "Client deleted"}


@router.get("/{client_id}/config")
async def get_client_config(client_id: int, user=Depends(get_current_user)):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = await cursor.fetchone()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    cursor = await db.execute("SELECT key, value FROM server_config")
    rows = await cursor.fetchall()
    config = {r["key"]: r["value"] for r in rows}

    port = config.get("listen_port", "51820")

    obfs_lines = []
    for key in ["jc", "jmin", "jmax", "s1", "s2", "h1", "h2", "h3", "h4"]:
        val = int(config.get(key, 0))
        if val > 0:
            obfs_lines.append(f"{key.upper()} = {val}")

    conf = f"""[Interface]
PrivateKey = {client['private_key']}
Address = {client['ip_address']}/24
DNS = {client['dns']}

"""
    if obfs_lines:
        conf += "# AmneziaWG obfuscation\n"
        conf += "\n".join(obfs_lines) + "\n\n"

    conf += f"""[Peer]
PublicKey = SERVER_PUBLIC_KEY
Endpoint = SERVER_IP:{port}
AllowedIPs = {client['allowed_ips']}
PersistentKeepalive = 25
"""
    return Response(content=conf, media_type="text/plain",
                    headers={"Content-Disposition": f"attachment; filename={client['name']}.conf"})
