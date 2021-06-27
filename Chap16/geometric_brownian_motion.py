#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
from sn_random_numbers import *
from simulation_class import *

class geometric_brownian_motion(simulation_class):
    ''' 블랙-숄즈-머튼의 기하 브라운 운동 모형에 따른 시뮬레이션 경로를 생성하는 클래스
    
    속성
    ====
    name : string
        객체 이름
    mar_env : instance of market_environment
        시뮬레이션에 필요한 시장 환경 데이터
    corr : Boolean
        다른 시뮬레이션 객체와 상관관계가 있으면 True
        
    Method
    ======
    update :
        파라미터 갱신
    generate_paths :
        시장 환경이 주어지면 몬테카를로 경로를 반환
    '''
    
    def __init__(self, name, mar_env, corr = False):
        super(geometric_brownian_motion, self).__init__(name, mar_env, corr)
        
    def update(self, initial_value = None, volatility = None, final_date = None):
        if initial_value is not None:
            self.initial_value = initial_value
            
        if volatility is not None:
            self.volatility = volatility
            
        if final_date is not None:
            self.final_date = final_date 
        
        self.instrument_values = None
    
    def generate_paths(self, fixed_seed = False, day_count = 365.):
        if self.time_grid is None:
            self.generate_time_grid()
                # 일반적 시뮬레이션 클래스의 Method
        
        # time_grid의 날짜 수
        M = len(self.time_grid)
        
        # 경로 수
        I = self.paths
        
        # 경로 시뮬레이션을 위한 배열 초기화
        paths = np.zeros((M, I))
        
        # initial_value로 처음 날짜 초기화
        paths[0] = self.initial_value
        
        if not self.correlated:
            # 상관관계 없을 시 난수 생성
            rand = sn_random_numbers((1, M, I), fixed_seed = fixed_seed)
        
        else:
            # 상관관계 있을 시 시장 환경에서 제공하는 random_numbers 사용
            rand = self.random_numbers
        
        short_rate = self.discount_curve.short_rate
            # 증가율을 위한 단기 이자율
        
        for t in range(1, len(self.time_grid)):
            if not self.correlated:
                ran = rand[t]
            
            else:
                ran = np.dot(self.cholesky_matrix, rand[:, t, :])
                ran = ran[self.rn_set]
            
            dt = (self.time_grid[t] - self.time_grid[t-1]).days / day_count
                # 두 날짜 차이를 1년 기준 비율로 표현
            
            paths[t] = paths[t-1] * np.exp((short_rate - 0.5 * self.volatility ** 2) * dt + self.volatility * np.sqrt(dt) * ran)
        
        self.instrument_values = paths

