import math
import numpy as np
from dataclasses import dataclass
from datetime import datetime

@dataclass(unsafe_hash=True)
class RealAvgDt:
    jm_code: str # 종목코드
    last_price: float # 마지막 가격
    avg_price: float # 평균 가격
    volume: float # 실시간 거래량
    count: int # 조회 횟수

    def __init__(self, jm_code, last_price, volume) -> None:
        self.jm_code = jm_code
        self.last_price = last_price
        self.avg_price = last_price
        self.volume = volume
        self.count = 1

    def update_data(self, price: float, volume: float, count: int, past_dt: dict, min_bf: datetime):
        if len(past_dt) > 0:
            real_count = 0
            past_count = 0
            past_prices = []
            past_volumes = []
            real_volumes = []
            for i, pd in enumerate(past_dt, start=0):
                # 히스토리 데이터 시간이 조회 간격을 초과했을 경우
                if pd['n_time'] < min_bf:
                    past_count += 1
                    past_prices.append(pd.get('price'))
                    past_volumes.append(pd.get('volume'))
                else:
                    real_count += 1
                    real_volumes.append(pd.get('volume'))

            if (len(past_prices) == 0 or len(past_volumes) == 0) and real_count > 0:
                self.update_def(price=price, volume=volume, count=real_count)
            else:
                past_avg_price = np.mean(past_prices) # 과거의 가격 평균
                real_sum_volume = sum(real_volumes) # 현재의 거래량 합계

                real_count = real_count + count
                per = 100 # 백분율 구하기

                if real_count > past_count:
                    past_per = math.trunc((past_count / real_count) * 100)
                    real_per = per - past_per
                elif past_count > real_count:
                    real_per = math.trunc((real_count / past_count) * 100)
                    past_per = per - real_per
                else:
                    real_per = 50
                    past_per = 50

                self.last_price = price
                self.avg_price = (price * real_per / 100) + ((past_avg_price * past_per) / 100)
                self.volume = volume + real_sum_volume
        else:
            self.update_def(price=price, volume=volume, count=0)

    def update_def(self, price: float, volume: float, count: int):
        self.last_price = price
        self.avg_price = ((self.avg_price * count) + price) / count + 1
        self.volume = self.volume + volume
        if count == 0:
            self.count += 1
        else:
            self.count = count
