from math import pi
import numpy as np
import pandas as pd
from bokeh.plotting import figure

from bokeh.models import Label
#from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import HoverTool, CustomJS

class Indicator(object):    
    def __init__(self, data, **kwargs):
        self.data = data
        self.params = kwargs
    
    def add_to_chart(self, stock_data, chart):
        pass

class EmaIndicator(Indicator):    
    def __init__(self, data, **kwargs):
        super(EmaIndicator, self).__init__(data, **kwargs)
    
    def add_to_chart(self, stock_data, chart):
        n = self.params['period']
        price = stock_data['Close']
        price = price.fillna(method='ffill')
        EMA = pd.Series(price.ewm(span = n, min_periods = n - 1).mean(), name = 'EMA_' + str(n))
        chart.line(stock_data.Date, EMA, line_dash=(4, 4), color='black', alpha=0.7, legend = 'EMA ' + str(n))
        return chart
    
class BollingerIndicator(Indicator):
    def __init__(self, data, **kwargs):
        super(BollingerIndicator, self).__init__(data, **kwargs)
        
    def add_to_chart(self, stock_data, chart):        
        n = self.params['period']
        price = stock_data['Close']
        price = price.fillna(method='ffill')
        bbupper = price.ewm(span = n, min_periods = n - 1).mean() + 2 * price.rolling(min_periods=n,window=n,center=False).std() 
        bblower = price.ewm(span = n, min_periods = n - 1).mean() - 2 * price.rolling(min_periods=n,window=n,center=False).std()         
        chart.line(stock_data.Date, bbupper, color='red', alpha=0.7, legend = 'bbupper ' + str(n))
        chart.line(stock_data.Date, bblower, color='black', alpha=0.7, legend = 'blower ' + str(n))
        return chart
    
class LookAndFeel:
    def __init__(self):
        self.width = None
        self.height = None
        self.color_up = None
        self.color_down = None
        
    def set_color_up(self, color):
        self.color_up = color
        return self

    def set_color_down(self, color):
        self.color_down = color
        return self

    def set_height(self, height):
        self.height = height
        return self

    def set_width(self, width):
        self.width = width
        return self
    
class StockChart:

    def __init__(self, data):
        self.height = 400
        self.width = 600
        self.days = 100
        self.title = ' '
        self.color_up = 'Green'
        self.color_down = 'Red'
        self.data = data
        self.indicators = []
        
    def set_look_and_feel(self, look_and_feel): 
        if (look_and_feel.height != None):
            self.height = look_and_feel.height
        if (look_and_feel.width != None):        
            self.width = look_and_feel.width
        if (look_and_feel.color_up != None):        
            self.color_up = look_and_feel.color_up
        if (look_and_feel.color_down != None):        
            self.color_down = look_and_feel.color_down            
        return self

        
    def set_title(self, title):
        self.title = title
        return self

    def set_data(self, data):
        self.data = data
        return self
    
    def set_days(self, days):
        self.days = days
        return self    
        
    def add_indicator(self, indicator):
        self.indicators.append(indicator)
        return self
        
    def __reset_date_index(self):
        df = self.data
        df["Date"] = pd.to_datetime(df["Date"])
        new_dates = pd.date_range(df.Date.min(), df.Date.max())
        df.index = pd.DatetimeIndex(df.Date)
        df = df.reindex(new_dates, fill_value=np.nan)
        df['Date'] = new_dates
        return df

    def __get_stock_data_dict(self):
        df = self.data
        df['Date'] =  df['Date'].map(lambda x: x.strftime('%m/%d/%y'))
        df = df.fillna(0)
        df = df.set_index(df['Date'])
        df = df.drop('Date', axis = 1)
        df = df.round(2)
        return df.T.to_dict('dict')
         
    def __add_indicators(self, stock_data, chart):
        for indicator in self.indicators:
            chart = indicator.add_to_chart(stock_data, chart)
        return chart
        
    def get_stock_chart(self):
        # Reset the date index.
        stock_data = self.__reset_date_index()

        # Only keep the number of days requested in chart_params
        stock_data = stock_data.tail(self.days)

        # Make a Bokeh figure
        # Bokeh comes with a list of tools that include xpan and crosshair.
        TOOLS = "xpan,crosshair"
        p = figure(x_axis_type='datetime', tools=TOOLS, plot_width=self.width, plot_height= self.height, title = self.title)
        p.xaxis.major_label_orientation = pi/4
        p.grid.grid_line_alpha=0.3

        mids = (stock_data.Open + stock_data.Close)/2
        spans = abs(stock_data.Close-stock_data.Open)
        inc = stock_data.Close > stock_data.Open
        dec = stock_data.Open >= stock_data.Close
        half_day_in_ms_width = 12*60*60*1000 # half day in 

        # Bokeh glyphs allows you to draw different types of glyphs on your charts....
        # Each candle consists of a rectangle and a segment.  
        p.segment(stock_data.Date, stock_data.High, stock_data.Date, stock_data.Low, color="black")
        # Add the rectangles of the candles going up in price
        p.rect(stock_data.Date[inc], mids[inc], half_day_in_ms_width, spans[inc], fill_color=self.color_up, line_color="black")
        # Add the rectangles of the candles going down in price
        p.rect(stock_data.Date[dec], mids[dec], half_day_in_ms_width, spans[dec], fill_color=self.color_down, line_color="black")

        ############# ADDING INDICATORS ############################
        #p = add_indicators(chart_params["indicators"], stock_data, p)
        p = self.__add_indicators(stock_data, p)

        ############# ADDING HOVER CALLBACK ############################
        # Create a dictionary that I can pass to the javascript callback
        stock_data_dictio = self.__get_stock_data_dict()

        callback_jscode = """
        var stock_dic = %s;         //The dictionary will be replaced here
        var day_im_ms = 24*60*60*1000;

        function formatDate(date) {
            var d = new Date(date),
                month = '' + (d.getMonth() + 1),
                day = '' + d.getDate(),
                year = d.getFullYear();
            if (month.length < 2) month = '0' + month;
            if (day.length < 2) day = '0' + day;
            return [ month, day, year.toString().substring(2)].join('/');
        }

         var d = cb_data.geometry.x;
         try {
          d = Math.floor( d + day_im_ms);
          d = new Date(d);
        } catch(err) {
           d= err; 
        }

        sel_date = formatDate(d);

        date_lbl = sel_date;
        date_lbl = date_lbl + " open:" + stock_dic[sel_date].Open
        date_lbl = date_lbl + " close:" + stock_dic[sel_date].Close
        date_lbl = date_lbl + " high:" + stock_dic[sel_date].High
        date_lbl = date_lbl + " low:" + stock_dic[sel_date].Low
        date_label.text = date_lbl
        """  % stock_data_dictio   # <--- Observe tha dictionary that is to be replaced into the stock_dic variable

        # This label will display the date and price information:
        date_label = Label(x=30, y=self.height-50, x_units='screen', y_units='screen',
                         text='', render_mode='css',
                         border_line_color='white', border_line_alpha=1.0,
                         background_fill_color='white', background_fill_alpha=1.0)

        date_label.text = ""
        p.add_layout(date_label)

        # When we create the hover callback, we pass the label and the callback code.
        callback = CustomJS(args={'date_label':date_label}, code=callback_jscode)
        p.add_tools(HoverTool(tooltips=None, callback=callback))
        ###################################################################   

        return p