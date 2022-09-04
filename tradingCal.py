import pandas as pd
import pandas_market_calendars as mcal
from datetime import datetime, timedelta
import inspect


class TradingCal():


    def __init__(self, start=None, end=None):
        """ Instantiates the class with the default settings for date.

            Note - End date will ALWAYS be one year from TODAY's date if it is not set; even if a start date is assgined well into the past
            
            defaults:
                start = today's date
                end = today's date + 365 days 
        
        """
        today = datetime.today()
        self.mcal = mcal.get_calendar('NYSE')

               
        if start == None:
            start = today.strftime('%Y-%m-%d')
        if end == None:
            end = today + timedelta(days=365)
            
        self.start = start
        self.end = end
    

    def set_dates(self, start, end):
        """ Checks if a different start and end date are passed in. If so, it updates the currently assigned values for the instatianted class.
        If a none type is passed in, it uses the currently assigned values for start/end
        """

        if start == None:
            start = self.start
        else:
            self.start = start
        if end == None:
            end = self.end
        else:
            self.end = end
        
        return start, end

    def get_trading_schedule(self, start=None, end=None) -> mcal:
        """ Retrieves the trading schedule times for trading days. This is useful when you need to know if the market closes early.

            e.g. market_open, market_close
        
        """
        
        start, end = self.set_dates(start, end)

        schedule = self.mcal.schedule(start_date=start, end_date=end)

        return schedule

    def get_business_days(self, start=None, end=None) -> mcal:
        """ Retrieves the business days the market is open

        """

        start, end = self.set_dates(start, end)

        bdays = self.mcal.valid_days(start_date=self.start, end_date=self.end)

        return bdays
    
    def build_calendar(self, start=None, end=None) -> pd.DataFrame:
        """ Builds a standard trading calendarom the mcal library


        Returns:
            pd.DataFrame: DataFrame with day + market open + close
        """
        
        start, end = self.set_dates(start, end)

        bdays = self.get_business_days(start=start, end=end)

        schedule = self.get_trading_schedule(start=start, end=end)

        cal_data = {'market_open': schedule.market_open, 'market_close': schedule.market_close}

        df = pd.DataFrame(cal_data)

        return df

    
    def adjust_odd_days(self, df) -> pd.DataFrame:
        """ Takes a market calendar with day of week and adjust the options days (primarily for SPY/QQQ or other Tickers with Dailies) 
        
        For Holidays on Mondays, start of market week is Tuesday so daily options start on Monday. For Fridays, end of week becomes Thursday and those are dajusted. 
        
        Generally there are no Wednesdays, but it is included in the search. Also, the only Friday notated for 2022 is for Good Friday.

        Returns:
            pd.DataFrame: Returns the adjusted DataFrame
        """

        odd_days = df.loc[(df['market_open'].isnull()) & (df['day_of_week'].isin([0,2,4]))].index

        for i in odd_days:
            if i.day_of_week == 4:
                date = i + timedelta(days=-1)
                df.at[date, 'opt'] = True
            else:
                date = i + timedelta(days=1)
                df.at[date, 'opt'] = True

        return df

        
    def build_standard_calendar(self, start=None, end=None, columns: list = None) -> pd.DataFrame:
        """ Builds a standard calendar in a pandas DataFrame. 

            Columns are standard datetime object attributes. 

            Defaults to ['date', 'day_of_week', 'day_name', 'day_of_year']

            MUST have 'date' as a column

            
        Args:
            columns (_type_, optional): . Defaults to None.
        """
        
        start, end = self.set_dates(start, end)

        if columns == None:

            columns = ['date', 'day_of_week', 'day_name', 'day_of_year']

        start = pd.Timestamp(start)
        
        end = pd.Timestamp(end)

        df = pd.date_range(start, end)

        pd_cal = pd.DataFrame(columns=columns)

        for column in columns:
            
            if column == 'date':
                """ If the column is date, we adjust it to a datetime and also set it to be the index."""
                
                pd_cal[column] = getattr(df, column).astype('datetime64[ns]')

                pd_cal.set_index('date', inplace=True)

            elif inspect.ismethod(getattr(df, column)):
                
                pd_cal[column] = getattr(df, column)()

            else:

                pd_cal[column] = getattr(df, column)

        return pd_cal

    
    def build_full_calendar(self, start=None, end=None) -> pd.DataFrame:
        """ Builds the merged calendar between the standard market calendar and the regular pandas date calendar. Does not filter out non market days.

            If you would like to filter out market days, simply just check if the market is open. 
            
            merged_cal['market_open'].isnull()


        Returns:
            pd.DataFrame: Returns the fully built Dataframe with included option flags for daily options days
        """
        standard_cal = self.build_standard_calendar(start=start, end=end)

        cal = self.build_calendar(start=start, end=end)
        
        merged_cal = pd.concat([cal, standard_cal], axis=1)

        merged_cal.loc[((~merged_cal['market_open'].isnull()) & (merged_cal['day_of_week'].isin([0,2,4]))), 'opt'] = True

        merged_cal.loc[(merged_cal['opt'] != True), 'opt'] = False

        #merged_cal = merged_cal.set_index('date')

        merged_cal = self.adjust_odd_days(merged_cal)

        return merged_cal
    

    def return_options_only(df) -> pd.DataFrame:

        df = df[df['opt'] == True]
        #df.index = np.arange(1, len(df) + 1)

        return df

    def return_end_of_week(df):

        eow = df[(df['day_of_week'].isin([3, 4])) & (df['opt'] == True)]

        return eow

