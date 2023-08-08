from time import sleep
import asyncio
from chapter1 import upbit_realtime

async def init():
    error_count = 0
    while error_count < 10:
        try:
            error_msg = await upbit_realtime.upbit_ws_client()
            print(f'{error_msg}')
        except Exception as e:
            error_count += 1
            print(f'{e}')
            sleep(3)

if __name__ == '__main__':
    asyncio.run(init())
