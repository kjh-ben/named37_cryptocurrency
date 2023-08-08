import json
import websockets
from time import sleep
import asyncio


async def upbit_ws_client():
    """
    업비트 실시간 시세를 조회한다.
    """
    async with websockets.connect('wss://api.upbit.com/websocket/v1', ping_interval=60) as websocket:
        subscribe_fmt = [
            {"ticket": "UNIQUE_TICKET"},
            {
                "type": "ticker",
                "codes": ['KRW-BTC', 'KRW-ETH', 'KRW-XRP'],
                "isOnlyRealtime": True
            },
            {"format": "SIMPLE"}
        ]
        subscribe_data = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)
        while True:
            try:
                data = await websocket.recv()
                data = json.loads(data)
                if data.get('mw') != 'NONE':
                    continue
                print(f'{data}')
            except Exception as e:
                msg = e
                print(f'{e}')
        return msg

async def init():
    error_count = 0
    while error_count < 10:
        try:
            error_msg = await upbit_ws_client()
            print(f'{error_msg}')
        except Exception as e:
            error_count += 1
            print(f'{e}')
            sleep(3)

if __name__ == '__main__':
    asyncio.run(init())