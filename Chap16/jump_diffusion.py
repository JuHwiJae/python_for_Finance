#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
from sn_random_numbers import sn_random_numbers
from simulation_class import simulation_class


# In[ ]:


class jump_diffusion(simulation_class):
    ''' 머튼의 점프 확산 모형에 따른 시뮬레이션 경로를 생성하기 위한 클래스
    
    속성
    ====
    name : string
        객체 이름
    
    mar_env : instance of market_environment
        시뮬레이션에 필요한 시장 환경
    
    corr : Boolean
        다른 모형 객체와 상관관계가 있으면 True
    
    Method
    =======
    update : 
        파라미터 갱신
    
    generate_paths :
        주어진 시장 환경에 따른 몬테카를로 경로 반환
    '''
    
    def __init__(self, name, mar_env, corr = False):
        super(jump_diffusion, self).__init__(name, mar_env, corr)
        try:
            # 추가 파라미터 필요
            self.lamb = mar_env.get_constant('lambda')
            self.mu = mar_env.get_constant('mu')
            self.delt = mar_env.get_constant('delta')
        
        except:
            print('Error parsing market environment')
        
    def update(self, initial_value = None, volatility = None, lamb = None, mu = None, delta = None, final_date = None):
        if initial_value is not None:
            self.initial_value = initial_value
        
        if volatility is not None:
            self.volatility = volatility
        
        if lamb is not None:
            self.lamb = lamb
        
        if mu is not None:
            self.mu = mu
        
        if delta is not None:
            self.delt = delta
        
        if final_date is not None:
            self.final_date = final_date
            
        self.instrument_values = None

    def generate_paths(self, fixed_seed = False, day_count = 365.):
        if self.time_grid is None:
            self.generate_time_grid()
                # 일반적인 시뮬레이션 클래스 Method
        
        # 시간 그리드의 날짜 수
        M = len(self.time_grid)
        
        # 경로 수
        I = self.paths
        
        # 시뮬레이션에 필요한 배열 초기화
        paths = np.zeros((M, I))
        
        # initial_value로 처음 날짜에 해당하는 값 초기화
        paths[0] = self.initial_value
        
        if self.correlated is False:
            sn1 = sn_random_numbers((1, M, I), fixed_seed = fixed_seed)
        
        else:
            sn1 = self.random_numbers
        
        # 점프 요인에 필요한 표준정규분포 난수 생성
        sn2 = sn_random_numbers((1, M, I), fixed_seed = fixed_seed)
        
        rj = self.lamb * (np.exp(self.mu + 0.5 * self.delt ** 2) - 1)
        
        short_rate = self.discount_curve.short_rate
        for t in range(1, len(self.time_grid)):
            if self.correlated is False:
                ran = sn1[t]
            
            else:
                ran = np.dot(self.cholesky_matrix, sn1[:, t, :])
                ran = ran[self.rn_set]
            
            dt = (self.time_grid[t] - self.time_grid[t - 1]).days / day_count
            poi = np.random.poisson(self.lamb * dt, I)
                # 점프 요소에 필요한 포아송 분포 난수
            
            paths[t] = paths[t - 1] * (np.exp((short_rate - rj - 0.5 * self.volatility ** 2) * dt
                                              + self.volatility * np.sqrt(dt) * ran)
                                       + (np.exp(self.mu + self.delt * sn2[t]) - 1) * poi)
        self.instrument_values = paths

