apikey = ""

from alpha_vantage.timeseries import TimeSeries

ts = TimeSeries(apikey)
# ts = TimeSeries(apikey, output_format='pandas')

# data, meta_data = ts.get_intraday(symbol='MSFT',interval='60min', outputsize='full')
data, meta_data = ts.get_daily(symbol="NSE:HCLTECH", outputsize="full")
