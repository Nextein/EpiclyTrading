
import numpy as np
import pandas as pd

def relativePositionOfCandles(data):
    """
    Tag candles with a state between:

    up, down, reverse-up, reverse-down, reverse-up2, reverse-down2, indecision, indecision2
    or undefined. ( U-D-RU-RD-RU2-RD2-I-I2-X )

    States are defined based on position relative to previous candlestick (Higher Highs or Lower Lows etc).
    """
    state = ['X' for i in range(data.shape[0])]

    # Identify state for each candle based on previous candle's state
    for i in range(2, data.shape[0]):
        if state[i-1] == 'X':
            if HH(data, i) and HL(data, i):
                state[i] = 'U'
            elif LH(data, i) and LL(data, i):
                state[i] = 'D'
            elif LH(data, i) and HL(data, i):
                if LH(data, i-1) and HL(data, i-1):
                    state[i] = 'I2'
                else:
                    state[i] = 'I'
            elif HH(data, i) and LL(data, i):
                if greenCandle(data, i):
                    state[i] = 'RU2'
                elif redCandle(data, i):
                    state[i] = 'RD2'
        elif state[i-1] == 'U':
            if HH(data, i) and HL(data, i):
                state[i] = 'U'
            elif LH(data, i) and LL(data, i):
                state[i] = 'RD'
            elif LH(data, i) and HL(data, i):
                if LH(data, i-1) and HL(data, i-1):
                    state[i] = 'I2'
                else:
                    state[i] = 'I'
            elif HH(data, i) and LL(data, i):
                state[i] = 'RU'
        elif state[i-1] == 'D':
            if HH(data, i) and HL(data, i):
                state[i] = 'RU'
            elif LH(data, i) and LL(data, i):
                state[i] = 'D'
            elif LH(data, i) and HL(data, i):
                if LH(data, i-1) and HL(data, i-1):
                    state[i] = 'I2'
                else:
                    state[i] = 'I'
            elif HH(data, i) and LL(data, i):
                state[i] = 'RU'
        elif state[i-1] == 'RU' or state[i-1] == 'RU2':
            if HH(data, i) and HL(data, i):
                state[i] = 'U'
            elif LH(data, i) and LL(data, i):
                state[i] = 'RD'
            elif LH(data, i) and HL(data, i):
                if LH(data, i-1) and HL(data, i-1):
                    state[i] = 'I2'
                else:
                    state[i] = 'I'
            elif HH(data, i) and LL(data, i):
                if greenCandle(data, i):
                    state[i] = 'RU2'
                elif redCandle(data, i):
                    state[i] = 'RD2'
        elif state[i-1] == 'RD' or state[i-1] == 'RD2':
            if HH(data, i) and HL(data, i):
                state[i] = 'RU'
            elif LH(data, i) and LL(data, i):
                state[i] = 'D'
            elif LH(data, i) and HL(data, i):
                if LH(data, i-1) and HL(data, i-1):
                    state[i] = 'I'
                else:
                    state[i] = 'I'
            elif HH(data, i) and LL(data, i):
                if greenCandle(data, i):
                    state[i] = 'RU2'
                elif redCandle(data, i):
                    state[i] = 'RD2'
        elif state[i-1] == 'I':
            if HH(data, i) and HL(data, i):
                state[i] = 'RU'
            elif LH(data, i) and LL(data, i):
                state[i] = 'RD'
            elif LH(data, i) and HL(data, i):
                state[i] = 'I2'
            elif HH(data, i) and LL(data, i):
                if greenCandle(data, i):
                    state[i] = 'RU2'
                elif redCandle(data, i):
                    state[i] = 'RD2'
        elif state[i-1] == 'I2':
            if HH(data, i) and HL(data, i):
                state[i] = 'RU'
            elif LH(data, i) and LL(data, i):
                state[i] = 'RD'
            elif LH(data, i) and HL(data, i):
                state[i] = 'I2'
            elif HH(data, i) and LL(data, i):
                if greenCandle(data, i):
                    state[i] = 'RU2'
                elif redCandle(data, i):
                    state[i] = 'RD2'
        else:
            print(f"Strategy FSM in unkown state: {state[i]}")
            exit()
    return state

def relativeCandlesReversalPatterns( data):
    """
    possible values: [-2, -1, 1, 2]

    returns: (only returns one value for last candle)
            0 when there is no pattern
            1 when there is a buy sequence,
            2 when there is a doubtful buy sequence,
        -1 when there is a sell sequence,
        -2 when there is a doubtful sell sequence,

    """
    tags = relativePositionOfCandles(data.iloc[-5:])
    state2, state1, state0 = tags[-3], tags[-2], tags[-1]
    buy_sequences = [
        state1 == 'D'  and state0 == 'RU',
        state2 == 'D'  and state1 == 'I' and state0 == 'RU',
        state1 == 'RD' and state0 == 'RU',
        state2 == 'RD' and state1 == 'I' and state0 == 'RU',
    ]

    buy_doubtful_sequences = [
        # state1 == 'D'  and state0 == 'RU2',
        state1 == 'D'  and state0 == 'RD2',
        # state2 == 'D'  and state1 == 'I' and state0 == 'RU2',
        state2 == 'D'  and state1 == 'I' and state0 == 'RD2',
        # state1 == 'RD' and state0 == 'RU2',
        state1 == 'RD' and state0 == 'RD2',
        # state2 == 'RD' and state1 == 'I' and state0 == 'RU2',
        state2 == 'RD' and state1 == 'I' and state0 == 'RD2',
    ]

    sell_sequences = [
        state1 == 'U'  and state0 == 'RD',
        state2 == 'U'  and state1 == 'I' and state0 == 'RD',
        state1 == 'RU' and state0 == 'RD',
        state2 == 'RU' and state1 == 'I' and state0 == 'RD',
    ]

    sell_doubtful_sequences = [
        # state1 == 'U'  and state0 == 'RD2',
        state1 == 'U'  and state0 == 'RU2',
        # state2 == 'U'  and state1 == 'I' and state0 == 'RD2',
        state2 == 'U'  and state1 == 'I' and state0 == 'RU2',
        # state1 == 'RU' and state0 == 'RD2',
        state1 == 'RU' and state0 == 'RU2',
        # state2 == 'RU' and state1 == 'I' and state0 == 'RD2',
        state2 == 'RU' and state1 == 'I' and state0 == 'RU2',
    ]

    if any(buy_sequences):
        return 1
    elif any(buy_doubtful_sequences):
        return 2
    elif any(sell_sequences):
        return -1
    elif any(sell_doubtful_sequences):
        return -2
    else:
        return 0

def relativeCandlesPhases( data, **args):
    """
    Direction Phases based on relative candles.
    args:
        data
    """
    tags = relativePositionOfCandles(data)
    phase = np.zeros(data.shape[0])
    
    phase[0] = 1 if greenCandle(data,0) else -1
    for i in range(1, 3):
        phase[i] = phase[i-1]

    for i in range(3,data.shape[0]):
        # up_sequences = [
        #     tags[i-2]=='RU' and tags[i-1]=='I' and tags[i]=='RU',
        #     tags[i-2]=='RU' and tags[i-1]=='I' and tags[i]=='RU2',
        #     tags[i-1]=='RU' and tags[i]=='U',
        #     tags[i-1]=='RU' and tags[i]=='RU2',
        #     tags[i-2]=='RU2' and tags[i-1]=='I' and tags[i]=='RU',
        #     tags[i-2]=='RU2' and tags[i-1]=='I' and tags[i]=='RU2',
        #     tags[i-1]=='RU2' and tags[i]=='U',
        #     tags[i-1]=='RU2' and tags[i]=='RU2',
        # ]
        # down_sequences = [
        #     tags[i-2]=='RD' and tags[i-1]=='I' and tags[i]=='RD',
        #     tags[i-2]=='RD' and tags[i-1]=='I' and tags[i]=='RD2',
        #     tags[i-1]=='RD' and tags[i]=='D',
        #     tags[i-1]=='RD' and tags[i]=='RD2',
        #     tags[i-2]=='RD2' and tags[i-1]=='I' and tags[i]=='RD',
        #     tags[i-2]=='RD2' and tags[i-1]=='I' and tags[i]=='RD2',
        #     tags[i-1]=='RD2' and tags[i]=='D',
        #     tags[i-1]=='RD2' and tags[i]=='RD2',
        # ]
        state2, state1, state0 = tags[i-2], tags[i-1], tags[i]
        up_sequences = [
            state1 == 'D'  and state0 == 'RU',
            state2 == 'D'  and state1 == 'I' and state0 == 'RU',
            state1 == 'D'  and state0 == 'RU2',
            state2 == 'D'  and state1 == 'I' and state0 == 'RU2',
            state1 == 'RD' and state0 == 'RU',
            state2 == 'RD' and state1 == 'I' and state0 == 'RU',
            state1 == 'RD' and state0 == 'RU2',
            state2 == 'RD' and state1 == 'I' and state0 == 'RU2',
            state1 == 'RD2' and state0 == 'RU',
            state2 == 'RD2' and state1 == 'I' and state0 == 'RU',
            state1 == 'RD2' and state0 == 'RU2',
            state2 == 'RD2' and state1 == 'I' and state0 == 'RU2',
            state2 == 'I' and state1 == 'I2' and state0 == 'RU',
            state2 == 'I' and state1 == 'I2' and state0 == 'RU2',

        ]

        down_sequences = [
            state1 == 'U'  and state0 == 'RD',
            state2 == 'U'  and state1 == 'I' and state0 == 'RD',
            state1 == 'U'  and state0 == 'RD2',
            state2 == 'U'  and state1 == 'I' and state0 == 'RD2',
            state1 == 'RU' and state0 == 'RD',
            state2 == 'RU' and state1 == 'I' and state0 == 'RD',
            state1 == 'RU' and state0 == 'RD2',
            state2 == 'RU' and state1 == 'I' and state0 == 'RD2',
            state1 == 'RU2' and state0 == 'RD',
            state2 == 'RU2' and state1 == 'I' and state0 == 'RD',
            state1 == 'RU2' and state0 == 'RD2',
            state2 == 'RU2' and state1 == 'I' and state0 == 'RD2',
            state2 == 'I' and state1 == 'I2' and state0 == 'RD',
            state2 == 'I' and state1 == 'I2' and state0 == 'RD2',
        ]

        # Check phase up sequence:
        if any(up_sequences):
            phase[i] = 1
        # Check phase down sequence:
        elif any(down_sequences):
            phase[i] = -1
        else:
            phase[i] = phase[i-1]
    return phase

def phaseChanges( data, nphases=4):
    """
    Returns indexes where value changes on an indicator (data).

    args:
        data: array containing a discrete set of values (your indicator)
        nphases: Set to -1 if you want the phase changes of entire data.
    """
    indexes = []
    subtotal = 0

    for i in np.arange(len(data)-2, 0, -1):
        if data[i] != data[i+1]:
            indexes.append(i+1)
            subtotal += 1
            if subtotal == nphases:
                break

    return [0] + indexes[::-1]

def Cycles( data) -> pd.Series:
    """ Cycles Indicator by Marc Goulding.

    Cycles:   A    B    CC    C    D
                -A   -B   -CC   -C   -D
    """
    possible_states = [
            "A",    "B",    "CC",    "C",    "D",
        "-A",   "-B",   "-CC",   "-C",   "-D", "X"  #  X = unknown. Only used at start
    ]

    phases = relativeCandlesPhases(data)

    current_state = "X"

    cycles = pd.Series(
        np.zeros(data.shape[0])
    ).astype(str)


    for i in range(0, data.shape[0]):
        if current_state == "A":
            if phases[i] == 1:
                current_state = "A"
                cycles[i] = current_state
            elif phases[i] == -1:
                current_state = "B"
                cycles[i] = current_state

        elif current_state == "B":
            phaseIndexes = phaseChanges(phases[:i], nphases = 2)
            minA = data.iloc[phaseIndexes[0]:phaseIndexes[1]]['Low'].min()
            try:
                minB = data.iloc[phaseIndexes[1]:i+1]['Low'].min()
            except IndexError:
                minB = data.iloc[phaseIndexes[1]:]['Low'].min()

            if minA < minB:
                if phases[i] == 1:
                    current_state = "CC"
                    cycles[i] = current_state
                elif phases[i] == -1:
                    current_state = "B"
                    cycles[i] = current_state
            else:
                current_state = "-A"
                cycles[i] = current_state

        elif current_state == "CC":
            phaseIndexes = phaseChanges(phases[:i], nphases = 3)
            try:
                maxCC = data.iloc[phaseIndexes[-1]:i+1]['High'].max()
            except IndexError:
                maxCC = data.iloc[phaseIndexes[-1]:]['High'].max()
            maxAB = data.iloc[phaseIndexes[0]:phaseIndexes[-1]]['High'].max()
            if maxCC > maxAB:
                current_state = "C"
                cycles[i] = current_state
            else:
                if phases[i] == 1:
                    current_state = "CC"
                    cycles[i] = current_state
                elif phases[i] == -1:
                    current_state = "-CC"
                    cycles[i] = current_state

        elif current_state == "C":
            if phases[i] == 1:
                current_state = "C"
                cycles[i] = current_state
            elif phases[i] == -1:
                current_state = "D"
                cycles[i] = current_state

        elif current_state == "D":
            phaseIndexes = phaseChanges(phases[:i], nphases = 3)
            minBC = data.iloc[phaseIndexes[0]:phaseIndexes[-1]]['Low'].min()
            try:
                minD = data.iloc[phaseIndexes[-1]:i+1]['Low'].min()
            except IndexError:
                minD = data.iloc[phaseIndexes[-1]:]['Low'].min()
            if minBC < minD:
                if phases[i] == 1:
                    current_state = "CC"
                    cycles[i] = current_state
                elif phases[i] == -1:
                    current_state = "D"
                    cycles[i] = current_state
            else:
                current_state = "-A"
                cycles[i] = current_state

        elif current_state == "-A":
            if phases[i] == 1:
                current_state = "-B"
                cycles[i] = current_state
            elif phases[i] == -1:
                current_state = "-A"
                cycles[i] = current_state

        elif current_state == "-B":
            phaseIndexes = phaseChanges(phases[:i], nphases = 2)
            try:
                maxB = data.iloc[phaseIndexes[1]:i+1]['High'].max()
            except IndexError:
                maxB = data.iloc[phaseIndexes[1]:]['High'].max()
            maxA = data.iloc[phaseIndexes[0]:phaseIndexes[1]]['High'].max()
            if maxA < maxB:
                if phases[i] == 1:
                    current_state = "-B"
                    cycles[i] = current_state
                elif phases[i] == -1:
                    current_state = "A"
                    cycles[i] = current_state
            else:
                current_state = "-CC"
                cycles[i] = current_state

        elif current_state == "-CC":
            phaseIndexes = phaseChanges(phases[:i], nphases = 3)
            try:
                minCC = data.iloc[phaseIndexes[-1]:i+1]['Low'].min()
            except IndexError:
                minCC = data.iloc[phaseIndexes[-1]:]['Low'].min()
            minAB = data.iloc[phaseIndexes[0]:phaseIndexes[-1]]['Low'].min()
            if minCC < minAB:
                current_state = "-C"
                cycles[i] = current_state
            else:
                if phases[i] == 1:
                    current_state = "CC"
                    cycles[i] = current_state
                elif phases[i] == -1:
                    current_state = "-CC"
                    cycles[i] = current_state

        elif current_state == "-C":
            if phases[i] == 1:
                current_state = "-D"
                cycles[i] = current_state
            elif phases[i] == -1:
                current_state = "-C"
                cycles[i] = current_state

        elif current_state == "-D":
            phaseIndexes = phaseChanges(phases[:i], nphases = 3)
            try:
                maxD = data.iloc[phaseIndexes[-1]:i+1]['High'].max()
            except IndexError:
                maxD = data.iloc[phaseIndexes[-1]:]['High'].max()
            maxBC = data.iloc[phaseIndexes[0]:phaseIndexes[-1]]['High'].max()

            if maxBC > maxD:
                if phases[i] == 1:
                    current_state = "-D"
                    cycles[i] = current_state
                elif phases[i] == -1:
                    current_state = "-CC"
                    cycles[i] = current_state
            else:
                current_state = "A"
                cycles[i] = current_state

        elif current_state == "X":

            if phases[i] == 1:
                current_state = "A"
                cycles[i] = current_state
            elif phases[i] == -1:
                current_state = "-A"
                cycles[i] = current_state

    return cycles

def trendingCycles( data):
    """
    Checks if there are 2 cycles down or 2 cycles up.
    
    Returns -1, 0 or 1 corresponding to downtrend, nothing and uptrend respectively.

    Only gives cycles during a phase 2 in the trend.
    If next phase 1 in trend has begun it will return False until phase 2 begins.
    """
    class Phase:
        def __init__(self):
            self.min = -1
            self.max = -1
        def updateMax(self, high):
            if high>self.max:
                self.max = high
        def updateMin(self, low):
            if low<self.min:
                self.min = low

    phases = phases(data)

    i = data.shape[0]-1
    state = 4  # FSM state to read last 4 phases in data
    phase = [Phase() for i in range(4)]
    phase[state-1].max = data.iloc[i]['High']
    phase[state-1].min = data.iloc[i]['Low']

    while state > 0:
        i -= 1
        if phases[i] == phases[i+1]:
            phase[state-1].updateMax(data.iloc[i]['High'])
            phase[state-1].updateMin(data.iloc[i]['Low'])
        else:
            state -= 1
            if state == 0:
                break
            phase[state-1].max = data.iloc[i]['High']
            phase[state-1].min = data.iloc[i]['Low']

    up_conditions = [
        # Last phase is an uptrend phase 2 going down
        phases[-1] == -1,
        # Higher Highs
        max(phase[0].max, phase[1].max) < max(phase[2].max, phase[3].max),
        # Higher Lows
        min(phase[0].min, phase[1].min) < min(phase[2].min, phase[3].min),
    ]
    down_conditions = [
        # Last phase is a downtrend phase 2 going up
        phases[-1] == 1,
        # Lower Highs
        max(phase[0].max, phase[1].max) > max(phase[2].max, phase[3].max),
        # Lower Lows
        min(phase[0].min, phase[1].min) > min(phase[2].min, phase[3].min),
    ]

    # Check 2 cycles up
    if all(up_conditions):
        return -1
    # Check 2 cycles down
    elif all(down_conditions):
        return 1
    else:
        return 0

def HH(data, i) -> bool:
    """ Last 2 candles make a Higher High """
    return in_order(data.iloc[i]['High'], data.iloc[i-1]['High'], is_value=3)

def HL(data, i) -> bool:
    """ Last 2 candles make a Higher Low """
    return in_order(data.iloc[i]['Low'], data.iloc[i-1]['Low'], is_value=3)

def LL(data, i) -> bool:
    """ Last 2 candles make a Lower Low """
    return in_order(data.iloc[i-1]['Low'], data.iloc[i]['Low'], is_value=3)

def LH(data, i) -> bool:
    """ Last 2 candles make a Lower High """
    return in_order(data.iloc[i-1]['High'], data.iloc[i]['High'], is_value=3)

def in_order(data1, data2, is_value=0) -> bool:
    """ Check if last candle in data1 is above last candle in data2"""
    if not is_value:
        return data1.iloc[-1] > data2.iloc[-1]
    elif is_value == 1:
        return data1 > data2.iloc[-1]
    elif is_value == 2:
        return data1.iloc[-1] > data2
    elif is_value == 3:
        return data1 > data2

def greenCandle(data, i=-1) -> bool:
    """ Green Candle """
    return data.iloc[i]['Close'] > data.iloc[i]['Open']

def redCandle(data, i=-1) -> bool:
    """ Red Candle """
    return data.iloc[i]['Close'] < data.iloc[i]['Open']

def linear_regression(series, period):
    """
    Calculate the Linear Regression (LINEARREG) of a given series over a specified period.
    
    Parameters:
        series (pd.Series): The input time series (usually close prices).
        period (int): The lookback period for calculating the linear regression.
    
    Returns:
        pd.Series: The linear regression values for the given period.
    """
    x = np.arange(period)  # Create an array of indexes for the lookback period
    
    def linreg(y):
        # Perform linear regression using least squares fit
        slope, intercept = np.polyfit(x, y, 1)  # degree 1 means a linear fit
        return slope * (period - 1) + intercept  # return the value of the regression line at the last point
    
    return series.rolling(window=period).apply(linreg, raw=True)

def SMA(data, period):
    """
    Calculates the Simple Moving Average (SMA) for a given dataset and period.

    Parameters:
    data (pd.Series): The dataset to calculate the SMA on (usually close prices).
    period (int): The window size for the moving average.

    Returns:
    pd.Series: A series of SMA values.
    """
    return data.rolling(window=period).mean()

def squeeze(data, period=20):
    """
    Squeeze Indicator from TradingView by LazyBear.

    Parameters:
    data (pd.DataFrame): OHLCV data with 'High', 'Low', 'Close' columns.
    period (int): The lookback period for calculating the squeeze indicator.

    Returns:
    pd.Series: A series of squeeze indicator values.
    """
    highest_high = data['High'].rolling(period).max()
    lowest_low = data['Low'].rolling(period).min()
    
    # Ensure the SMA uses the 'Close' prices
    midline = (highest_high + lowest_low) / 2
    sma = SMA(data['Close'], period=period)
    
    # Ensure all parts are of the same length and no NaNs are present
    regression_input = (midline + sma) / 2
    regression_input = regression_input.dropna()

    try:
        squeeze = data['Close'] - linear_regression(regression_input, period)
    except Exception as e:
        logging.error(f"Squeeze calculation failed for {data.index[-1]}: {e}")
        squeeze = pd.Series(np.zeros(data.shape[0]), index=data.index)
    
    # Handle NaNs that might result from mismatched lengths
    squeeze = squeeze.reindex(data.index).fillna(0)
    
    return squeeze
