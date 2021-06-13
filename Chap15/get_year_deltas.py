#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np

def get_year_deltas(date_list, day_count = 365.):
    ''' 날짜를 1년 비율로 표현한 부동소수점 벡터를 전환.
    초깃값은 0으로 고정
    
    인수
    ====
    date_list : list or array
        datetime 객체 모음
    
    day_count : float
        1년의 날짜 수
    
    반환값
    ======
    delta_list : array
        1년 기준 비율
    '''
    
    start = date_list[0]
    delta_list = [(date - start).days / day_count for date in date_list]
    return np.array(delta_list)

