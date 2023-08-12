import json
import websockets
import sys_data
from time import sleep
from datetime import datetime
from datetime import timedelta
import mm_real_avg_dt as mm_ra_dt

def set_realtime(data):
    """
    실시간 정보를 임시 저장한다.
    """
    jm_code = data.get('jm_code')
    data['price'] = data.get('price')
    data['volume'] = data.get('volume')
    data['count'] = 1
    sys_data.REAL_TEMP[jm_code] = data

def sync_realtime():
    """
    1초 단위로 REAL_TEMP 의 값을 dataclass로 가공한 후 REAL_AVG_DT 객체에 할당한다.
    :return:
    """
    while True:
        if len(sys_data.REAL_TEMP) > 0:
            for jm_code in sys_data.REAL_TEMP:
                price = sys_data.REAL_TEMP[jm_code]['price']
                volume = sys_data.REAL_TEMP[jm_code]['volume']
                count = sys_data.REAL_TEMP[jm_code]['count']

                if jm_code in sys_data.REAL_AVG_DT:
                    model = sys_data.REAL_AVG_DT.get(jm_code)
                    past_dt = []
                    now = datetime.now()
                    bf = timedelta(seconds=10)
                    min_bf = now - bf

                    model.update_data(price=price, volume=volume, count=count, past_dt=past_dt, min_bf=min_bf)

                else:
                    model = mm_ra_dt.RealAvgDt(jm_code, price, volume)
                # 최종적으로 가공된 dataclass 를 REAL_AVG_DT 객체에 할당한다.
                sys_data.REAL_AVG_DT[jm_code] = model
                print(f'{sys_data.REAL_AVG_DT[jm_code]}')
            # 동기화가 완료된 작업은 반복 처리되지 않도록 REAL_TEMP 객체를 초기화한다.
            sys_data.REAL_TEMP.clear()
        sleep(1)

async def upbit_ws_client():
    """
    업비트 실시간 시세를 조회한다.
    """
    async with websockets.connect('wss://api.upbit.com/websocket/v1', ping_interval=60) as websocket:
        subscribe_fmt = [
            {"ticket": "UNIQUE_TICKET"},
            {
                "type": "ticker",
                "codes": sys_data.TARG_JM_CODE,
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
                parse_data = {'jm_code': data.get('cd'), 'price': data.get('tp'), 'volume': data.get('tv')}
                set_realtime(parse_data)
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
