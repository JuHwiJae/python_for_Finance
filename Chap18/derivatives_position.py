#!/usr/bin/env python
# coding: utf-8

# In[ ]:


class derivatives_position(object):
    ''' 파생상품 포지션 모형 클래스
    
    속성
    ====
    name : string
        객체의 이름
    quantity : float
        포지션을 이루는 자산이나 파생상품의 숫자
    underlying : string
        파생상품 자산/리스트 요인의 이름
    mar_env : instance of market_environment
        가치 평가 클래스와 관련된 상수, 리스트, 커브
    otype : string
        사용할 가치 평가 클래스('European' or 'American')
    payoff_func : string
        파생상품의 페이오프를 나타내는 문자열
    
    Method
    =======
    
    get_info : 
        파생상품 포지션과 관련된 정보 인쇄
    
    '''
    
    def __init__(self, name, quantity, underlying, mar_env, otype, payoff_func):
        self.name = name
        self.quantity = quantity
        self.underlying = underlying
        self.mar_env = mar_env
        self.otype = otype
        self.payoff_func = payoff_func
        
    def get_info(self):
        print('NAME')
        print(self.name, '\n')
        print('QUANTITY')
        print(self.quantity, '\n')
        print('UNDERLYING')
        print(self.underlying, '\n')
        print('MARKET ENVIRONMENT')
        
        print('\n**Constantss**')
        for key, value in self.mar_env.constants.items():
            print(key, value)
            
        print('\n**Lists**')
        for key, value in self.mar_env.lists.items():
            print(key, value)
        
        print('\n**Curves**')
        for kdy in self.mar_env.curves.items():
            print(key, value)
        
        print('\nOPTION TYPE')
        print(self.otype, '\n')
        print('PAYOFF FUNCTION')
        print(self.payoff_func)
        

