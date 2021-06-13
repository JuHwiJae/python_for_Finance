#!/usr/bin/env python
# coding: utf-8

# In[ ]:


class market_environment(object):
    ''' 가치 평가와 관련된 시장 환경 모형을 위한 클래스
    
    속성
    ====
    name : string
        시장 환경 이름
    pricing_date : datetime object
        시장 환경 날짜
    
    Method
    =======
    add_constant :
        상수(모형 파라미터) 추가
    get_constant :
        상수 반환
    add_list :
        (기초자산 등의) 리스트 추가
    get_list :
        리스트 반환
    add_curve :
        (이자율 커브 등의) 시장 커브 추가
    get_curve :
        시장 커브 반환
    add_environment :
        상수, 리스트, 커브 등의 전체 시장 환경 추가 또는 갱신
    '''
    
    def __init__(self, name, pricing_date):
        self.name = name
        self.pricing_date = pricing_date
        self.constants = {}
        self.lists = {}
        self.curves = {}
    
    def add_constant(self, key, constant):
        self.constants[key] = constant
    
    def get_constant(self, key):
        return self.constants[key]
    
    def add_list(self, key, list_object):
        self.lists[key] = list_object
    
    def get_list(self, key):
        return self.lists[key]
    
    def add_curve(self, key, curve):
        self.curves[key] = curve
    
    def get_curve(self, key):
        return self.curves[key]
    
    def add_environment(self, env):
        # 존재하는 값이 있을땐 갱신
        for key in env.constants:
            self.constants[key] = env.constants[key]
        
        for key in env.lists:
            self.lists[key] = env.lists[key]
        
        for key in env.curves:
            self.curves[key] = env.curves[key]

