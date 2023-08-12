import pyupbit
import sys_data
import upbit_realtime
import asyncio
import threading

if __name__ == '__main__':
    tickers = pyupbit.get_tickers(fiat="KRW")
    sys_data.TARG_JM_CODE = tickers
    t_job = threading.Thread(target=upbit_realtime.sync_realtime, name='sync_realtime', daemon=True)
    t_job.start()
    asyncio.run(upbit_realtime.init())
