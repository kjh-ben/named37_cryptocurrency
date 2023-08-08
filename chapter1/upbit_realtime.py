from collections import deque
import json
import numpy as np
import threading
import websockets
from datetime import datetime
from datetime import timedelta
from decimal import Decimal as dc
from time import sleep
import pickle
import traceback


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
