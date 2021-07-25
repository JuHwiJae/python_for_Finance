#!/usr/bin/env python
# coding: utf-8

# In[ ]:


class valuation_class(object):
    ''' 단일 요인 모형의 가치 평가를 위한 베이스 클래스
    
    속성
    ====
    name : string
        객체의 이름
    underlying : 
        시뮬레이션 클래스 인스턴스
    mar_env : instance of market_environment
        평가를 위한 시장 환경 데이터
    payoff_func : string
        파이썬 문법으로 표시된 파생상품 payoff
        example) 'np.maximum(maturity_value - 100, 0)'
        여기에서 maturity_value는 기초자산 가치에 대한 Numpy 벡터
        example) 'np.maximum(instrument_value - 100, 0)'
        여기에서 instrument_value는 전체 시간/경로 그리드 상에서 기초자산의 가치에 대한 Numpy 행렬
        
    Method
    =======
    update : 
        선택한 가치 평가 파라미터 갱신
    delta :
        파생상품 델타 반환
    vega : 
        파생상품 베가 반환'''
    
    def __init__(self, name, underlying, mar_env, payoff_func = ''):
        try:
            self.name = name
            self.pricing_date = mar_env.pricing_date
            try:
                self.strike = mar_env.get_constant('strike')
            
            except:
                pass
            
            self.maturity = mar_env.get_constant('maturity')
            self.currency = mar_env.get_constant('currency')
            # 시뮬레이션 객체의 시뮬레이션 파라미터와 할인 커브 사용
            self.frequency = underlying.frequency
            self.paths = underlying.paths
            self.discount_curve = underlying.discount_curve
            self.payoff_func = payoff_func
            self.underlying = underlying
            # 기초자산에 대한 pricing_date와 maturity 제공
            self.underlying.special_dates.extend([self.pricing_date, self.maturity])
        
        except:
            print('Error parsing market environment')
    def update(self, initial_value = None, volatility = None, strike = None, maturity = None):
        if initial_value is not None:
            self.underlying.update(initial_value = initial_value)
        if volatility is not None:
            self.underlying.update(volatility = volatility)
        if strike is not None:
            self.strike = strike
        if maturity is not None:
            self.maturity = maturity
            # time_grid 없는 새로운 만기일 추가
            if not maturity in self.underlying.time_grid:
                self.underlying.special_dates.append(maturity)
                self.underlying.instrument_values = None
    
    def delta(self, interval = None, accuracy = 4):
        if interval is None:
            interval = self.underlying.initial_value / 50.
        # 전향 처분 방식
        # 왼쪽 포인트의 옵션 가치 계산
        value_left = self.present_value(fixed_seed = True)
        # 오른쪽 포인트의 기초자산 가치 계산
        initial_del = self.underlying.initial_value + interval
        self.underlying.update(initial_value = initial_del)
        # 오른쪽 포인트의 옵션 가치 계산
        value_right = self.present_value(fixed_seed = True)
        # 시뮬레이션 객체의 초깃값 리셋
        self.underlying.update(initial_value = initial_del - interval)
        delta = (value_right - value_left) / interval
        
        # 수치 오류에 대한 수정
        if delta < -1.0:
            return -1.0
        elif delta > 1.0:
            return 1.0
        else:
            return round(delta, accuracy)
    
    def vega(self, interval = 0.01, accuracy = 4):
        if interval < self.underlying.volatility /50.:
            interval = self.underlying.volatility /50.
        # 전향 차분 방식
        # 왼쪽 포인트 값 계산
        value_left = self.present_value(fixed_seed = True)
        # 오른쪽 포인트에 대한 변동성 값
        vola_del = self.underlying.volatility + interval
        # 시뮬레이션 객체의 값 갱신
        self.underlying.update(volatility = vola_del)
        # 오른쪽 포인트의 값 계산
        value_right = self.present_value(fixed_seed = True)
        # 시뮬레이션 객체의 변동성 리셋
        self.underlying.update(volatility = vola_del - interval)
        vega = (value_right - value_left) / interval
        return round(vega, accuracy)

