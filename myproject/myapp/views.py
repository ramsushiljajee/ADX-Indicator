from django.shortcuts import render, HttpResponse
import mimetypes
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as mp


from .forms import MyfileUploadForm
from .models import file_upload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def index(request):

    if request.method == 'POST':
        form = MyfileUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            name = form.cleaned_data['file_name']
            the_files = form.cleaned_data['files_data']

            file_upload(file_name=name, my_file=the_files).save()
            
            filename = 'Assignment1-data.csv'
            filepath = BASE_DIR + '//media//' + filename
            
            df = pd.read_csv(filepath)
            
            # TR
            tr1 = pd.DataFrame(df['High'] - df['Low'])
            tr2 = pd.DataFrame(abs(df['High'] - df['Close'].shift(1)))
            tr3 = pd.DataFrame(abs(df['Low'] -  df['Close'].shift(1)))
            frames = [tr1, tr2, tr3]

            tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1).rename('TR')
            tr[0] = None

            df = pd.concat([df, tr], axis = 1, join='inner')

            # +DM1
            plus_dm1 = pd.DataFrame(df['High'] - df['High'].shift(1))
            plus_dm2 = pd.DataFrame(df['Low'].shift(1) - df['Low'])

            frames = pd.concat([plus_dm1, plus_dm2], axis=1)

            def flag_plus_dm(frames):
                if(frames['High'] > frames['Low']):
                    return max(frames['High'], 0)
                else:
                    return 0

            plus_dm = frames.apply(flag_plus_dm, axis=1).rename('+DM1')
            plus_dm[0] = None

            df = pd.concat([df, plus_dm], axis = 1, join='inner')

            # -DM1
            plus_dm1 = pd.DataFrame(df['Low'].shift(1) - df['Low'])
            plus_dm2 = pd.DataFrame(df['High'] - df['High'].shift(1))

            frames = pd.concat([plus_dm1, plus_dm2], axis=1)

            def flag_plus_dm(frames):
                if(frames['Low'] > frames['High']):
                    return max(frames['Low'], 0)
                else:
                    return 0

            plus_dm = frames.apply(flag_plus_dm, axis=1).rename('-DM1')
            plus_dm[0] = None

            df = pd.concat([df, plus_dm], axis = 1, join='inner')

            # TR14, +DM14 and -DM14
            n = np.zeros(len(df))

            # TR14
            c = df.loc[1:14, ["TR"]].sum(axis=0)
            d = pd.Series(c)
            m = pd.Series(n).rename('TR14')
            m.iloc[0:14] = None
            m[14] = d['TR']
            m = pd.concat([df['TR'], m], axis = 1, join='inner')

            # +DM14
            dm1 = df.loc[1:14, ["+DM1"]].sum(axis=0)
            dm2 = pd.Series(dm1)
            dm = pd.Series(n).rename("+DM14")
            dm.iloc[0:14] = None
            dm[14] = dm2["+DM1"]
            dm = pd.concat([df["+DM1"], dm], axis = 1, join='inner')

            # -DM14
            dm4 = df.loc[1:14, ["-DM1"]].sum(axis=0)
            dm5 = pd.Series(dm4)
            minus_dm = pd.Series(n).rename('-DM14')
            minus_dm.iloc[0:14] = None
            minus_dm[14] = dm5["-DM1"]
            minus_dm = pd.concat([df["-DM1"], minus_dm], axis = 1, join='inner')

            for i in range(15, len(df)):
                m['TR14'].loc[i:len(df)+1] = (m['TR14'].shift(1) - (m['TR14'].shift(1) / 14) + m['TR']).round(decimals = 2)
                dm["+DM14"].loc[i:len(df)+1] = (dm["+DM14"].shift(1) - (dm['+DM14'].shift(1) / 14) + dm['+DM1']).round(decimals = 2)
                minus_dm['-DM14'].loc[i:len(df)+1] = (minus_dm["-DM14"].shift(1) - (minus_dm['-DM14'].shift(1) / 14) + minus_dm['-DM1']).round(decimals = 2)

            df = pd.concat([df, m['TR14']], axis = 1, join='inner')
            df = pd.concat([df, dm['+DM14']], axis = 1, join='inner')
            df = pd.concat([df, minus_dm['-DM14']], axis = 1, join='inner')

            # +DI14
            plus_di = pd.Series(n).rename('+DI14')
            plus_di.iloc[0:14] = None

            # -DI14
            minus_di = pd.Series(n).rename('-DI14')
            minus_di.iloc[0:14] = None

            # DI14 Difference
            di_diff = pd.Series(n).rename('DI14 Diff')
            di_diff.iloc[0:14] = None

            # DI14 Sum
            di_sum = pd.Series(n).rename('DI14 Sum')
            di_sum.iloc[0:14] = None

            # DX
            dx = pd.Series(n).rename('DX')
            dx.iloc[0:14] = None

            for i in range(14, len(df)):
                plus_di['+DI14'] = (100 * (df['+DM14'] / df['TR14'])).round(decimals = 2)
                minus_di['-DI14'] = (100 * (df['-DM14'] / df['TR14'])).round(decimals = 2)
                di_diff['DI14 Diff'] = abs(plus_di['+DI14'] - minus_di['-DI14']).round(decimals = 2)
                di_sum['DI14 Sum'] = (plus_di['+DI14'] + minus_di['-DI14']).round(decimals = 2)
                dx['DX'] = (100 * (di_diff['DI14 Diff'] / di_sum['DI14 Sum'])).round(decimals = 2)

            plus = pd.DataFrame()
            plus = plus_di['+DI14'].rename('+DI14')

            minus = pd.DataFrame()
            minus = minus_di['-DI14'].rename('-DI14')

            diff = pd.DataFrame()
            diff = di_diff['DI14 Diff'].rename('DI14 Diff')
    
            sum1 = pd.DataFrame()
            sum1 = di_sum['DI14 Sum'].rename('DI14 Sum')

            dx2 = pd.DataFrame()
            dx2 = dx['DX'].rename('DX')

            df = pd.concat([df, plus], axis = 1, join='inner')
            df = pd.concat([df, minus], axis = 1, join='inner')
            df = pd.concat([df, diff], axis = 1, join='inner')
            df = pd.concat([df, sum1], axis = 1, join='inner')
            df = pd.concat([df, dx2], axis = 1, join='inner')
    
            # ADX
            adx1 = df.loc[14:27, ["DX"]].mean(axis=0)
            adx2 = pd.Series(adx1)
            adx = pd.Series(n).rename('ADX')
            adx.iloc[0:27] = None
            adx[27] = adx2['DX']
            adx = pd.concat([df['DX'], adx], axis = 1, join='inner')

            for i in range(28, len(df)):
                adx['ADX'].loc[i:len(df)+1] = ( ((adx['ADX'].shift(1) * 13) + df['DX'] ) / 14 ).round(decimals = 2)
    
            df = pd.concat([df, adx['ADX']], axis = 1, join='inner')

            # Renaming untitled column(timestramp) to 'Time'
            df.rename(columns={'Unnamed: 0':'Time'}, inplace=True)

            df.to_csv('media/ADX-Solution.csv', index=False, header=True)

            df.plot(x="Time", y=["+DI14", "-DI14", "ADX"], kind="line", figsize=(30, 8))
            dataOut = mp.show
        
            return render(request, 'filedownload.html', {"something": True, "data": dataOut})
            
        else:
            return render(request, 'filedownload.html')
            
    else:
        
        context = {
            'form':MyfileUploadForm()
        }      
        
        return render(request, 'index.html', context)


def filedownloadpage(request):
    return render(request, 'filedownload.html')


def download_file(request):
    filename = 'ADX-Solution.csv'
    filepath = BASE_DIR + '//media//' + filename
    path = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
