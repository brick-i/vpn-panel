from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from services import vpn, installer
from models import ServerStatus, ServerConfigUpdate
from routers.auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/server", tags=["server"])


@router.get("/status", response_model=ServerStatus)
async def server_status(user=Depends(get_current_user)):
    status = await vpn.get_status()
    db = await get_db()
    cursor = await db.execute("SELECT key, value FROM server_config")
    rows = await cursor.fetchall()
    config = {r["key"]: r["value"] for r in rows}
    return ServerStatus(
        installed=status["installed"],
        running=status["running"],
        interface=status["interface"],
        listen_port=int(config.get("listen_port", 51820)),
        connected_clients=status["connected_clients"],
    )


@router.post("/start")
async def server_start(user=Depends(get_current_user)):
    if not await vpn.is_installed():
        raise HTTPException(status_code=400, detail="AmneziaWG not installed")
    try:
        await vpn.start_vpn()
        return {"message": "VPN started"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def server_stop(user=Depends(get_current_user)):
    try:
        await vpn.stop_vpn()
        return {"message": "VPN stopped"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart")
async def server_restart(user=Depends(get_current_user)):
    try:
        await vpn.restart_vpn()
        return {"message": "VPN restarted"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def server_config(user=Depends(get_current_user)):
    db = await get_db()
    cursor = await db.execute("SELECT key, value FROM server_config")
    rows = await cursor.fetchall()
    return {r["key"]: r["value"] for r in rows}


@router.put("/config")
async def update_config(data: ServerConfigUpdate, user=Depends(get_current_user)):
    db = await get_db()
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        await db.execute(
            "INSERT OR REPLACE INTO server_config (key, value) VALUES (?, ?)",
            (key, str(value)),
        )
    await db.commit()
    return {"message": "Config updated"}


@router.post("/install")
async def install(user=Depends(get_current_user)):
    if installer.get_install_progress()["running"]:
        raise HTTPException(status_code=400, detail="Installation already in progress")
    import asyncio
    asyncio.create_task(installer.install_amneziawg())
    return {"message": "Installation started"}


@router.get("/install/progress")
async def install_progress(user=Depends(get_current_user)):
    return installer.get_install_progress()


@router.get("/install/stream")
async def install_stream(user=Depends(get_current_user)):
    async def event_generator():
        import asyncio
        while True:
            progress = installer.get_install_progress()
            yield f"data: {progress}\n\n"
            if not progress["running"] and progress["current"] >= progress["total"]:
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
