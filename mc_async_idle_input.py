
import asyncio
import struct
import random
import string

PORT = 25565
CONNECTIONS = 300
KEEP_ALIVE_SECONDS = 10

def gen_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 12)))

def make_packet(data: bytes) -> bytes:
    length = len(data)
    out = b""
    while True:
        temp = length & 0b01111111
        length >>= 7
        if length != 0:
            temp |= 0b10000000
        out += bytes([temp])
        if length == 0:
            break
    return out + data

def handshake_packet(ip: str, port: int) -> bytes:
    ip_bytes = ip.encode("utf-8")
    packet = b""
    packet += b"\x00"  # Handshake packet ID
    packet += b"\x2f"  # Protocol version = 47
    packet += bytes([len(ip_bytes)]) + ip_bytes
    packet += struct.pack(">H", port)
    packet += b"\x02"  # Next state: login
    return make_packet(packet)

def login_start_packet(name: str) -> bytes:
    name_bytes = name.encode("utf-8")
    packet = b"\x00" + bytes([len(name_bytes)]) + name_bytes
    return make_packet(packet)

async def idle_bot(ip: str, port: int):
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        name = gen_name()
        writer.write(handshake_packet(ip, port))
        writer.write(login_start_packet(name))
        await writer.drain()
        print(f"[✓] Bot joined: {name} — idle for {KEEP_ALIVE_SECONDS}s")
        await asyncio.sleep(KEEP_ALIVE_SECONDS)
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"[x] Error: {e}")

async def main(ip: str, port: int):
    tasks = [asyncio.create_task(idle_bot(ip, port)) for _ in range(CONNECTIONS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    ip_input = input("🖥️ Nhập IP server Minecraft của bạn: ").strip()
    asyncio.run(main(ip_input, PORT))
