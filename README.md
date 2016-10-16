Stockcharts is an extensible and intuitive python/bokeh implementation for stock charts.  
This library allows you to add your own indicators by extending the **Indicator** class.

## The main classes

We will not go over the details on these changes.  If you are really interested in the code, you can access my **github account**.  

However, let's have a look at the prototype of the main classes:


**StockChart:** main class - creates stock charts.
~~~
class StockChart:
    def __init__(self, data):
    def set_title(self, title):
    def set_days(self, days):
    def set_look_and_feel(self, look_and_feel):     
    def add_indicator(self, indicator):
    def get_stock_chart(self):
~~~
___

**LookAndFeel:** encapsulates look and feel for this chart.
~~~
class LookAndFeel:
    def __init__(self):        
    def set_color_up(self, color):
    def set_color_down(self, color):
    def set_height(self, height):
    def set_width(self, width):    
~~~

___
**Indicator:** extend this class to add your own indicators.
~~~
class Indicator(object):    
    def __init__(self, data, **kwargs):    
    def add_to_chart(self, stock_data, chart):
~~~

## Example

~~~
df = pd.read_csv("./data/spy.csv", nrows=350)
p= StockChart(df) \
    .set_title("SPY") \
    .set_days(200) \
    .set_look_and_feel(LookAndFeel().set_width(800)) \
    .add_indicator(EmaIndicator(df, period=14)) \
    .add_indicator(BollingerIndicator(df, period=14)) \
    .get_stock_chart()

show(p)
~~~

![spy chart] (https://github.com/maestro27/stockcharts/blob/master/chart_with_indicators.png)
