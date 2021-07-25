#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from valuation_class import valuation_class


# In[2]:


class valuation_mcs_european(valuation_class):
    ''' 단일 요인 몬테카를로 시뮬레이션을 사용한 임의의 페이오프에 대한 유로피안 옵션 가치 평가 클래스
    
    Method
    =======
    generate_payoff : 
        주어진 경로와 페이오프 함수를 이용하여 페이오프 계산
    present_value :
        몬테카를로 방식으로 추정한 현재 가치 반환
    
    '''
    
    def generate_payoff(self, fixed_seed = False):
        '''
        인수
        ====
        fixed_seed : Boolean
             가치 계산용 시드 값을 중복 사용
        '''
        try:
            # 행사가가 정의 되었는지 확인
            strike = self.strike
        
        except:
            pass
        
        paths = self.underlying.get_instrument_values(fixed_seed = fixed_seed)
        time_grid = self.underlying.time_grid
        
        try:
            time_index = np.where(time_grid == self.maturity)[0]
            time_index = int(time_index)
        
        except:
            print('Maturity date not in time grid of underlying')
        
        maturity_value = paths[time_index]
        # 전체 경로에 대한 평균
        mean_value = np.mean(paths[:time_index], axis = 1)
        # 전체 경로에 대한 최대값
        max_value = np.amax(paths[:time_index], axis = 1)[-1]
        # 전체 경로에 대한 최솟값
        min_value = np.amin(paths[:time_index], axis = 1)[-1]
        
        try:
            payoff = eval(self.payoff_func)
            return payoff
        
        except:
            print('Error evaluating payoff function')
            
    def present_value(self, accuracy = 6, fixed_seed = False, full = False):
        '''
        인수
        ====
        accuracy : int
            반환 값의 자리수
        fixed_seed : Boolean
            가치 계산용 시드 값을 중복 사용
        full : Boolean
            현재 값에 대한 1차원 배열도 반환
        
        '''
        cash_flow = self.generate_payoff(fixed_seed = fixed_seed)
        discount_factor = self.discount_curve.get_discount_factors((self.pricing_date, self.maturity))[0, 1]
        result = discount_factor * np.sum(cash_flow) / len(cash_flow)
        
        if full:
            return round(result, accuracy), discount_factor * cash_flow
        else:
            return round(result, accuracy)


# In[ ]:




