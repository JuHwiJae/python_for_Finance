#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from get_year_deltas import *
import numpy as np

class constant_short_rate(object):
    ''' 고정 단기 이자율 할인 클래스
    
    속성
    ====
    name : string
        객체 이름
    short_rate : float (positive)
        할인에 사용될 고정 이자율
    
    Method
    =======
    get_disocunt_factors :
        datetime 객체 or 1년 기준 비율의 리스트/배열이 주어지면 할인율 반환
    '''
    
    def __init__(self, name, short_rate):
        self.name = name
        self.short_rate = short_rate
        if short_rate < 0:
            raise ValueError('Short rate negative.')
        
    def get_discount_factors(self, date_list, dtobjects = True):
        if dtobjects is True:
            dlist = get_year_deltas(date_list)
        
        else:
            dlist = np.array(date_list)
        
        dflist = np.exp(self.short_rate * -dlist)
        return np.array((date_list, dflist)).T

