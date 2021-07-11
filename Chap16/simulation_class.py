#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd


# In[ ]:


class simulation_class(object):
    ''' 시뮬레이션 클래스의 베이스 메서드 제공
    
    속성
    ====
    name : string
        객체 이름
        
    mar_env : instance of market_environment
        시뮬레이션에 필요한 시장 환경 자료
    
    corr : Boolean
        다른 모형 객체와 상관관계가 있으면 True
    
    Method
    =======
    generate_time_grid : 
        시뮬레이션 시간 그리드 반환
    
    get_instrument_values :
        현재 증권 가치(배열) 반환
    
    '''
    
    def __init__(self, name, mar_env, corr):
        try:
            self.name = name
            self.pricing_date = mar_env.pricing_date
            self.initial_value = mar_env.get_constant('initial_value')
            self.volatility = mar_env.get_constant('volatility')
            self.final_date = mar_env.get_constant('final_date')
            self.currency = mar_env.get_constant('currency')
            self.frequency = mar_env.get_constant('frequency')
            self.paths = mar_env.get_constant('paths')
            self.discount_curve = mar_env.get_curve('discount_curve')
            
            try:
                # mar_env 안에 time_grid가 있으면 이 값을 취함
                # (포트폴리오 가치 평가용)
                self.time_grid = mar_env.get_list('time_grid')
            
            except:
                self.time_grid = None
            
            try:
                # 만약 특별한 날짜가 있다면 추가
                self.special_dates = mar_env.get_list('special_dates')
            
            except:
                self.special_dates = []
            
            self.instrument_values = None
            self.correlated = corr
            
            if corr is True:
                # 이 위험 요인은 상관관계가 있는 포트폴리오에서만 필요
                self.cholesky_matrix = mar_env.get_list('cholesky_matrix')
                self.rn_set = mar_env.get_list('rn_set')[self.name]
                self.random_numbers = mar_env.get_list('random_numbers')
        
        except:
            print("Error prasing market environment.")
    
    def generate_time_grid(self):
        start = self.pricing_date
        end = self.final_date
        # pandas date_rage 함수 (일간 : 'B', 주간 : 'W', 월간 : 'M')
        time_grid = pd.date_range(start = start, end = end, freq = self.frequency).to_pydatetime()
        time_grid = list(time_grid)
        # 시작, 끝, 특별 날짜를 time_grid에 추가
        
        if start not in time_grid:
            time_grid.insert(0, start)
        
        if end not in time_grid:
            time_grid.append(end)
        
        if len(self.special_dates) > 0:
            # 모든 특별 날짜를 추가
            time_grid.extend(self.special_dates)
            
            # 복제를 추가
            time_grid = list(set(time_grid))
            
            # 리스트 정렬
            time_grid.sort()
            
        self.time_grid = np.array(time_grid)
    
    def get_instrument_values(self, fixed_seed=True):
        if self.instrument_values is None:
            # 증권 가격이 없다면 시뮬레이션 시작
            self.generate_paths(fixed_seed=fixed_seed, day_count=365.)
        elif fixed_seed is False:
            # fixed_seed가 False면 다시 시뮬레이션
            self.generate_paths(fixed_seed=fixed_seed, day_count=365.)
        return self.instrument_values

