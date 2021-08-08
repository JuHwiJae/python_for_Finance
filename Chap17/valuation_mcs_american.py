#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from valuation_class import valuation_class


# In[2]:


class valuation_mcs_american(valuation_class):
    ''' 단일 요인 몬테카를로 시뮬레이션을 사용한 임의의 페이오프에 대한 아메리칸 옵션 가치 평가 클래스
    
    Method
    =======
    generate_payoff : 
        주어진 경로와 페이오프 함수를 이용하여 페이오프 계산
    present_value :
        롱스태프-슈바르츠 방식에 따른 현재 가치 반환
    
    '''
    
    def generate_payoff(self, fixed_seed = False):
        '''
        인수 
        ====
        fixed_seed : 
            가치 계산용 시드 값을 중복 사용
        
        '''
        try : 
            strike = self.strike
        
        except :
            pass
        
        paths = self.underlying.get_instrument_values(fixed_seed = fixed_seed)
        time_grid = self.underlying.time_grid
        
        try:
            time_index_start = int(np.where(time_grid == self.pricing_date)[0])
            time_index_end = int(np.where(time_grid == self.maturity)[0])
        
        except:
            print('Maturity date not in time grid of underlying')
        
        instrument_values = paths[time_index_start:time_index_end + 1]
        
        try:
            payoff = eval(self.payoff_func)
            return instrument_values, payoff, time_index_start, time_index_end
        
        except:
            print('Error evaluating payoff function')
    
    def present_value(self, accuracy = 6, fixed_seed = False, bf = 5, full = False):
        ''' 
        인수
        ====
        accuracy : int
            반환되는 결과의 자리수
        fixed_seed : Boolean
            가치 계산용 시드 값을 중복 사용
        bf : int
            회귀분석에 사용할 기저 함수의 숫자
        full : Boolean
            현재 가치의 1차원 배열 반환
        
        '''
        
        instrument_values, inner_values, time_index_start, time_index_end = self.generate_payoff(fixed_seed = fixed_seed)
        time_list = self.underlying.time_grid[time_index_start:time_index_end + 1]
        discount_factors = self.discount_curve.get_discount_factors(time_list, dtobjects = True)
        V = inner_values[-1]
        for t in range(len(time_list) - 2, 0, -1):
            # 주어진 시간 구간에 대한 할인율
            df = discount_factors[t, 1] / discount_factors[t + 1, 1]
            # 회귀분석 단계
            rg = np.polyfit(instrument_values[t], V * df, bf)
            # 경로에 대한 보유 가치 계산
            C = np.polyval(rg, instrument_values[t])
            # 최적 결정 다계
            # 내재 가치가 회귀분석한 보유 가치보다 크면 내재 가치 선택 그외엔 보유 가치 선택
            V = np.where(inner_values[t] > C, inner_values[t], V * df)
        
        df = discount_factors[0, 1] / discount_factors[1, 1]
        result = df * np.sum(V) / len(V)
        if full:
            return round(result, accuracy), df * V
        else:
            return round(result, accuracy)


# In[ ]:




