import quandl
import talib
quandl.ApiConfig.api_key = "PUT YOUR QUANDL KEY HERE"



def SourceData(SourceStart, SourceEnd):
    
    Data1 = {
            "close " : quandl.get("LBMA/GOLD", start_date=SourceStart, end_date=SourceEnd)["USD (PM)"].dropna(),
            }

    Data2 = {
            "MA    " : talib.MA(Data1["close "], timeperiod=30, matype=0),
            "EMA   " : talib.EMA(Data1["close "], timeperiod=30),
            "CMO   " : talib.CMO(Data1["close "], timeperiod=14),
            "MACD1 " : talib.MACD(Data1["close "], fastperiod=12, slowperiod=26, signalperiod=9)[0],
            "MACD2 " : talib.MACD(Data1["close "], fastperiod=12, slowperiod=26, signalperiod=9)[1],
            "MACD3 " : talib.MACD(Data1["close "], fastperiod=12, slowperiod=26, signalperiod=9)[2],
            }

    Data3 = {
            "Crude " : quandl.get("EIA/PET_RWTC_D", start_date=SourceStart, end_date=SourceEnd),
            "CNY   " : quandl.get("FED/RXI_N_B_CH", start_date=SourceStart, end_date=SourceEnd)["Value"],
            "Uncer " : quandl.get("FRED/WLEMUINDXD", start_date=SourceStart, end_date=SourceEnd),
            "Unccn " : quandl.get("FRED/CHIEPUINDXM", start_date=SourceStart, end_date=SourceEnd),
            "VIX   " : quandl.get("CHRIS/CBOE_VX1", start_date=SourceStart, end_date=SourceEnd)["Open"],
            "AAII  " : quandl.get("AAII/AAII_SENTIMENT", start_date=SourceStart, end_date=SourceEnd)["Bullish"],
            }
            

    DataDic = {**Data1, **Data2, **Data3}
    data_cont = list(DataDic.values())
    data_name = list(DataDic.keys())

    return (data_cont, data_name)



if __name__ == '__main__':
    SourceStart = "2017-12-01"
    SourceEnd   = "2019-01-01"
    data_cont, data_name = SourceData(SourceStart, SourceEnd)
