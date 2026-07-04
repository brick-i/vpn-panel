from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClientCreate(BaseModel):
    name: str
    allowed_ips: str = "0.0.0.0/0, ::/0"
    dns: str = "1.1.1.1, 8.8.8.8"
    expires_at: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    allowed_ips: Optional[str] = None
    dns: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[str] = None


class ServerConfigUpdate(BaseModel):
    listen_port: Optional[int] = None
    dns: Optional[str] = None
    jc: Optional[int] = None
    jmin: Optional[int] = None
    jmax: Optional[int] = None
    s1: Optional[int] = None
    s2: Optional[int] = None
    h1: Optional[int] = None
    h2: Optional[int] = None
    h3: Optional[int] = None
    h4: Optional[int] = None


class ServerStatus(BaseModel):
    installed: bool
    running: bool
    interface: str = "awg0"
    listen_port: int = 51820
    connected_clients: int = 0


class SystemInfo(BaseModel):
    hostname: str
    os: str
    cpu_percent: float
    ram_total: int
    ram_used: int
    ram_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    network_rx: int
    network_tx: int
    uptime: float
