# general imports
import numpy as np
import pandas as pd
import pytz


def processInputDataFrame(inputDict):
    '''makes sure dataframes to be merged have the same input types.
    :param inputDict [Dictionary] consting of date and time column names and formats'''

    def convertDateTimeFormat(f):
        '''converts a string date or time format to a python date or time format to be used in to_datetime
        :param f [string] string date or time format'''

        def doubleToSingle(d):
            return d[0]

        sep = ' '
        if len(f.split('/')) > 1:
            sep = '/'
        elif len(f.split('-')) > 1:
            sep = '-'
        elif len(f.split(':')) > 1:
            sep = ':'
        f = list(map(doubleToSingle, f.split(sep)))
        value = sep.join(map('%{0}'.format, f))
        return value

    try:
        #find Date column
        #convert the date to datetime
        df = inputDict['df']
        if not inputDict['dateChannel.format']: # == 'infer':
            df['DATE'] = df[inputDict['dateChannel.value']].apply(pd.to_datetime,infer_datetime_format=True, errors='coerce')

        else:
            if (inputDict['dateChannel.value'] == inputDict['timeChannel.value']) | (inputDict['timeChannel.value'] == None) | (inputDict['timeChannel.value'] == '') : #datetime are rolled into 1 column
                df['DATE'] = pd.to_datetime(df[inputDict['dateChannel.value']],infer_datetime_format=True,errors='coerce')
            else: #has a seperate time value
                df['DATE'] = pd.to_datetime(df[inputDict['dateChannel.value']],
                                            infer_datetime_format=True, errors='coerce')
                #add in the time column
                df['DATE'] = df['DATE'] + df[inputDict['timeChannel.value']].apply(pd.to_timedelta, errors='coerce')
            # remove rows that did not work
            df = df.drop(df.index[pd.isnull(df['DATE'])])
        #else:
            #df['DATE'] = df['DATE'] + df[timeColumnName].apply(lambda t: pd.to_datetime(t,format=convertDateTimeFormat(timeColumnFormat)))
    
        # convert data columns to numeric
        for idx, col in enumerate(inputDict['componentChannels.headerName.value']):
            try:
                df[col] = df[col].apply(pd.to_numeric, errors='coerce')
            except:
                df[col] = df[col.replace('_',' ')].apply(pd.to_numeric, errors='coerce')
            # change col name to the desired name - component name + attribute type
            df = df.rename(columns={col:inputDict['componentChannels.componentName.value'][idx] + inputDict['componentChannels.componentAttribute.value'][idx]})

        # convert to utc time
        df = dstFix(df,inputDict['timeZone.value'],inputDict['inputDST.value'])
    
        # order by datetime

        df = df.sort_values(['DATE']).reset_index(drop=True)
        df.index=df['DATE']
        df = df.drop('DATE',axis=1)
        return df
    except KeyError as k:
        print('The required key %s was not included in the input dictionary' %k)
        return

def dstFix(df,tz,useDST):
    try:
        timeZone = pytz.timezone(tz)
        df['DATE']=df['DATE'].apply(lambda d: timeZone.localize(d,is_dst=useDST))
        df['DATE']=df['DATE'].dt.tz_convert('UTC')
    except Exception as e:
        print(str(e))
        print(type(e))

    return df
