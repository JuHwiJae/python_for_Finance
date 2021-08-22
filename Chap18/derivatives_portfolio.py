#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd

from dx_frame import *
from sn_random_numbers import sn_random_numbers
from geometric_brownian_motion import geometric_brownian_motion
from jump_diffusion import jump_diffusion
from square_root_diffusion import square_root_diffusion
from simulation_class import simulation_class

from valuation_class import valuation_class
from valuation_mcs_european import valuation_mcs_european
from valuation_mcs_american import valuation_mcs_american

from derivatives_position import derivatives_position


# In[ ]:


class derivatives_portfolio(object):
    ''' 파생상품 포지션 포트폴리오 생성용 클래스
    
    속성
    ====
    name : str
        객체 이름
    positions : dict
        포지션용 사전(derivatives_position 클래스 인스턴스)
    val_env : market_environment
        가치 평가용 시장 환경
    assets : dict
        각 자산용 시장 환경 사전
    correlations : list
        자산간의 상관관계
    fixed_seed : Boolean
        랜덤 변수용 시드 플래그
    '''
    
    def __init__(self, name, positions, val_env, assets,correlations = None, fixed_seed = False):
        self.name = name
        self.positions = positions
        self.val_env = val_env
        self.assets = assets
        self.underlyings = set()
        self.correlations = correlations
        self.time_grid = None
        self.underlying_objects = {}
        self.valuation_objects = {}
        self.fixed_seed = fixed_seed
        self.special_dates = []
        
        for pos in self.positions:
            # 가장 빠른 starting_date 결정
            self.val_env.constants['starting_date'] = min(self.val_env.constants['starting_date'], positions[pos].mar_env.pricing_date)
            
            # 관련 있는 최신 날짜 결정
            self.val_env.constants['final_date'] = max(self.val_env.constants['final_date'], positions[pos].mar_env.constants['maturity'])
            
            # 모든 기초자산을 집합으로 모아서 중복 제거
            self.underlyings.add(positions[pos].underlying)
            
        # 시간 그리드 생성
        start = self.val_env.constants['starting_date']
        end = self.val_env.constants['final_date']
        time_grid = pd.date_range(start = start, end = end, freq = self.val_env.constants['frequency']).to_pydatetime()
        time_grid = list(time_grid)
        
        for pos in self.positions:
            maturity_date = positions[pos].mar_env.constants['maturity']
            
            if maturity_date not in time_grid:
                time_grid.insert(0, maturity_date)
                self.special_dates.append(maturity_date)
        
        if start not in time_grid:
            time_grid.insert(0, start)
        
        if end not in time_grid:
            time_grid.append(0, end)
        
        # 중복 요소 제거
        time_grid = list(set(time_grid))
        
        # time_grid 안의 날짜 정렬
        time_grid.sort()
        self.time_grid = np.array(time_grid)
        self.val_env.add_list('time_grid', self.time_grid)
        if correlations is not None:
            # 상관관계 계산
            ul_list = sorted(self.underlyings)
            correlation_matrix = np.zeros((len(ul_list), len(ul_list)))
            np.fill_diagonal(correlation_matrix, 1.0)
            correlation_matrix = pd.DataFrame(correlation_matrix, index = ul_list, columns = ul_list)
            
            for i, j, corr in correlations:
                corr = min(corr, 0.999999999999)
                correlation_matrix.loc[i, j] = corr
                correlation_matrix.loc[j, i] = corr
                
            # 숄레스키 행렬 계산
            cholesky_matrix = np.linalg.cholesky(np.array(correlation_matrix))
            
            # 각각의 기초자산과 랜덤 넘버 슬라이스에 대한 인덱스 위치 저장
            rn_set = {asset : ul_list.index(asset) for asset in self.underlyings}
            
            # (상관관계가 있는 경우) 모든 기초자산이 사용하는 랜덤 넘버 배열
            random_numbers = sn_random_numbers((len(rn_set), len(self.time_grid), self.val_env.constants['paths']), fixed_seed = self.fixed_seed)
            
            # 모든 기초자산이 공유하는 가치 계산용 환경 정보 추가
            self.val_env.add_list('cholesky_matrix', cholesky_matrix)
            self.val_env.add_list('random_numbers', random_numbers)
            self.val_env.add_list('rn_set', rn_set)
        
        for asset in self.underlyings:
            # 각 자산에 대한 시장 환경 선택
            mar_env = self.assets[asset]
            
            # 시장환경에 가치 계산용 환경 정보 추가
            mar_env.add_environment(val_env)
            
            # 시뮬레이션 클래스 선택
            model = models[mar_env.constants['model']]
            
            # 시뮬레이션 객체 생성
            if correlations is not None:
                self.underlying_objects[asset] = model(asset, mar_env, corr = True)
            
            else:
                self.underlying_objects[asset] = model(asset, mar_env, corr = False)
                
        for pos in positions:
            # 가치평가 클래스 선택
            val_class = otypes[positions[pos].otype]
            
            # 시장 환경 및 가치 계산용 환경 선택
            mar_env = positions[pos].mar_env
            mar_env.add_environment(self.val_env)
            
            # 가치 평가용 클래스 인스턴스 생성
            self.valuation_objects[pos] = val_class(name = positions[pos].name,
                                                    mar_env = mar_env, 
                                                    underlying = self.underlying_objects[positions[pos].underlying], 
                                                    payoff_func = positions[pos].payoff_func)
    
    def get_positions(self):
        ''' 포트폴리오 내의 모든 파생상품 포지션에 대한 정보를 얻기 위한 Method
        '''
        for pos in self.positions:
            bar = '\n' + 50 * '-'
            print(bar)
            
            self.positions[pos].get_info()
            print(bar)
            
    def get_statistics(self, fixed_seed = False):
        ''' 포트폴리오 통계 제공 '''
        res_list = []
        
        # 포트폴리오 내의 모든 포지션에 대해 반복
        for pos, value in self.valuation_objects.items():
            p = self.positions[pos]
            pv = value.present_value(fixed_seed = fixed_seed)
            res_list.append([p.name,
                             p.quantity,
                             pv,
                             value.currency,
                             pv * p.quantity,
                             value.delta() * p.quantity,
                             value.vega() * p.quantity])
        res_df = pd.DataFrame(res_list, columns = ['name', 'quant', 'value', 'curr.',
                                                       'pos_value', 'pos_delta', 'pos_vega'])
        return res_df

