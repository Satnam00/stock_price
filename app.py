import pandas          as pd
import pandas          as pd
import numpy           as np

from flask import Flask, render_template, request, Response,  send_file
from nsepy             import get_history
from nsepy.derivatives import get_expiry_date
from nsetools          import Nse
from io import BytesIO

nse = Nse()




def report(s_date, t_date, sym):
    months = [s_date.month, s_date.month + 1, s_date.month + 2, s_date.month + 3, s_date.month + 4]

    expiry_status = True
    expiry = []
    for m in months:
        try:
            x = list(get_expiry_date(year=s_date.year, month=m))
        except:
            comment = ''
            comment = 'Stock futures not available for ' + str(m) + 'th ' + 'Month'
            expiry_status = False

        k = [i.day for i in x]
        k.sort()
        expiry.append([i for i in x if (i.day == k[-1])])

    try:
        x = str(expiry[0][0].year) + '-' + str(expiry[0][0].month) + '-' + str(expiry[0][0].day + 1)
        x = pd.to_datetime(x)
        s1 = x.date()
    except:
        x = str(expiry[0][0].year) + '-' + str(expiry[0][0].month + 1) + '-' + str(1)
        x = pd.to_datetime(x)
        s1 = x.date()
    try:
        x = str(expiry[1][0].year) + '-' + str(expiry[1][0].month) + '-' + str(expiry[1][0].day + 1)
        x = pd.to_datetime(x)
        s2 = x.date()
    except:
        x = str(expiry[1][0].year) + '-' + str(expiry[1][0].month + 1) + '-' + str(1)
        x = str(x)
        x = pd.to_datetime(x)
        s2 = x.date()

    for i in range(5):
        stt = False
        try:
            eq = get_history(symbol=sym, start=s_date, end=t_date)
            f1 = get_history(symbol=sym, start=s_date, end=expiry[0][0], futures=True, expiry_date=expiry[0][0])
            f2 = get_history(symbol=sym, start=s_date, end=expiry[0][0], futures=True, expiry_date=expiry[1][0])

            f3 = get_history(symbol=sym, start=s1, end=expiry[1][0], futures=True, expiry_date=expiry[1][0])
            f4 = get_history(symbol=sym, start=s1, end=expiry[1][0], futures=True, expiry_date=expiry[2][0])

            f5 = get_history(symbol=sym, start=s2, end=expiry[2][0], futures=True, expiry_date=expiry[2][0])
            f6 = get_history(symbol=sym, start=s2, end=expiry[2][0], futures=True, expiry_date=expiry[3][0])
            stt = True
        except:
            pass

        if (stt == True or i == 3):
            break

    eq.reset_index(level=0, inplace=True)
    f1.reset_index(level=0, inplace=True)
    f2.reset_index(level=0, inplace=True)
    f3.reset_index(level=0, inplace=True)
    f4.reset_index(level=0, inplace=True)
    f5.reset_index(level=0, inplace=True)
    f6.reset_index(level=0, inplace=True)

    status = False
    len_ = len(eq['Date']) - (len(f1['Date']) + len(f3['Date']) + len(f5['Date']))
    if (len_ >= 1):
        status = True

    # print('status', status, len_)

    if (status == True and expiry_status == True):
        try:
            x = str(expiry[2][0].year) + '-' + str(expiry[2][0].month) + '-' + str(expiry[2][0].day + 1)
            x = pd.to_datetime(x)
            s3 = x.date()
        except:
            x = str(expiry[2][0].year) + '-' + str(expiry[2][0].month + 1) + '-' + str(1)
            x = pd.to_datetime(x)
            s3 = x.date()

        for i in range(5):
            stt = False
            #             if(i==4):
            #                 print('please try reconnecting with internet')
            try:
                f7 = get_history(symbol=sym, start=s3, end=t_date, futures=True, expiry_date=expiry[3][0])
                f8 = get_history(symbol=sym, start=s3, end=t_date, futures=True, expiry_date=expiry[4][0])
                stt = True
            except:
                continue

            if (stt == True):
                break
        try:
            f7.reset_index(level=0, inplace=True)
            f8.reset_index(level=0, inplace=True)
        except:
            pass

    col = f1.columns
    f135 = pd.DataFrame()
    for i in col:
        lis = []
        lis = list(f1[i])
        for j in f3[i]:
            lis.append(j)
        for k in f5[i]:
            lis.append(k)
        if (status == True and expiry_status == True):
            for m in f7[i]:
                lis.append(m)
        f135[i + str('_nr')] = lis

    col = f2.columns
    f246 = pd.DataFrame()
    for i in col:
        lis = []
        lis = list(f2[i])
        for j in f4[i]:
            lis.append(j)
        for k in f6[i]:
            lis.append(k)
        if (status == True and expiry_status == True):
            for m in f8[i]:
                lis.append(m)
        f246[i + str('_fr')] = lis

    main = pd.DataFrame()
    main = eq

    main['emp'] = np.nan
    col = f135.columns
    com = f246.columns
    for i in col:
        lis = []
        for j in range(len(main['Date'])):
            try:
                lis.append(f135[i][j])
            except:
                lis.append(np.nan)

        main[i] = lis

    main['empt'] = np.nan

    for i in com:
        lis = []
        for j in range(len(main['Date'])):
            try:
                lis.append(f246[i][j])
            except:
                lis.append(np.nan)

        main[i] = lis

    num = 0
    x = main[num:]['Date_nr'].to_list()

    for i in x:
        try:
            if (i <= expiry[2][0]):
                num += 1
        except:
            continue
    main['_____'] = np.nan
    main['Date_'] = main['Date']
    main['Price_'] = main['Close']
    main['Delivery_'] = round((main['Turnover'] * main['%Deliverble']) / 1000000000000, 2)
    main['5DayAvg_'] = main['Delivery_'].rolling(5).mean()
    main['Cumulative OI_'] = main['Open Interest_nr'] + main['Open Interest_fr']
    main['change in OI_'] = main['Cumulative OI_'].sub(main['Cumulative OI_'].shift())
    main['---'] = np.nan
    main['~Price_'] = round((main['Price_'].sub(main['Price_'].shift()) / main['Price_'].shift()) * 100, 2)
    main['~Delivery_'] = round(main['Delivery_'] / main['5DayAvg_'] * 100, 2)
    main['~OI%_'] = round(main['change in OI_'].shift(-1) / main['Cumulative OI_'] * 100, 2).shift()
    pr = []
    de = []
    oi = []

    for i in range(len(main['~Price_'])):
        if (main['~Price_'][i] >= 1):
            pr.append('Rising')
        elif (main['~Price_'][i] <= -1):
            pr.append('Falling')
        else:
            pr.append('Flat')

        if (main['~Delivery_'][i] >= 100):
            de.append('Rising')
        elif (main['~Delivery_'][i] <= -100):
            de.append('Falling')
        else:
            de.append('Flat')

        if (main['~OI%_'][i] >= 2):
            oi.append('Rising')
        elif (main['~OI%_'][i] <= -2):
            oi.append('Falling')
        else:
            oi.append('Flat')

    main['pr'] = pr
    main['de'] = de
    main['oi'] = oi

    temp = pd.DataFrame()
    temp['pr'] = pr
    temp['de'] = de
    temp['oi'] = oi
    con = []
    tr = []

    for i in range(len(temp['pr'])):
        if (temp['pr'][i] == 'Rising'):
            if (temp['de'][i] == 'Rising'):
                if (temp['oi'][i] == 'Rising'):
                    con.append('Strong Long')
                    tr.append('Very Bullish')

                if (temp['oi'][i] == 'Flat'):
                    con.append('Last Leg of Long')
                    tr.append('Cautiously Bullish')

                if (temp['oi'][i] == 'Falling'):
                    con.append('Short Covering')
                    tr.append('Bullish Till Open Interest Falling')

            if (temp['de'][i] == 'Falling'):
                if (temp['oi'][i] == 'Rising'):
                    con.append('Weaker Longs')
                    tr.append('Cautiously Bullish')

                if (temp['oi'][i] == 'Flat'):
                    con.append('No long Position')
                    tr.append('Breaish')

                if (temp['oi'][i] == 'Falling'):
                    con.append('Weak Short Covering')
                    tr.append('Moderately Bearish')

            if (temp['de'][i] == 'Flat'):
                if (temp['oi'][i] == 'Rising'):
                    con.append('New Longs')
                    tr.append('Moderately Bullish and Bullish Immediately After Some Volume Support')

                if (temp['oi'][i] == 'Flat'):
                    con.append('No Interest')
                    tr.append('Likely Bearish')

                if (temp['oi'][i] == 'Falling'):
                    con.append('Weak Short Covering')
                    tr.append('Moderately Bearish')

        if (temp['pr'][i] == 'Falling'):
            if (temp['de'][i] == 'Rising'):
                if (temp['oi'][i] == 'Rising'):
                    con.append('Strong Short')
                    tr.append('Very Bearish')

                if (temp['oi'][i] == 'Flat'):
                    con.append('Last Leg of Short')
                    tr.append('Cautiously Bearish')

                if (temp['oi'][i] == 'Falling'):
                    con.append('Long Covering')
                    tr.append('Bearish Till Open Interest Falling')

            if (temp['de'][i] == 'Falling'):
                if (temp['oi'][i] == 'Rising'):
                    con.append('Weaker Shorts')
                    tr.append('Cautiously Bearish')

                if (temp['oi'][i] == 'Flat'):
                    con.append('No Short Position')
                    tr.append('Bullish')

                if (temp['oi'][i] == 'Falling'):
                    con.append('Weak Long Covering')
                    tr.append('Moderately Bullish')

            if (temp['de'][i] == 'Flat'):
                if (temp['oi'][i] == 'Rising'):
                    con.append('New Shorts')
                    tr.append('Moderately Bearish and Bearish Immediately After Some Volume Support')

                if (temp['oi'][i] == 'Flat'):
                    con.append('No Interest')
                    tr.append('Likely Bullish')

                if (temp['oi'][i] == 'Falling'):
                    con.append('Weak Long Covering')
                    tr.append('Moderately Bullish')
        if (temp['pr'][i] == 'Flat'):
            tr.append(np.nan)
            con.append(np.nan)
    main['Long__'] = np.nan
    main['Short__'] = np.nan
    main['Conclusion_'] = con
    main['Trend_'] = tr

    def count_trend(string, df):
        tmp_count = 0
        tmp_list = []
        for i in df['Trend_']:
            if (i == string):
                tmp_count += 1
            else:
                tmp_count = 0
            tmp_list.append(tmp_count)
        return tmp_list

    main['num_1'] = count_trend('Bullish Till Open Interest Falling', main)
    main['num_2'] = count_trend('Bearish Till Open Interest Falling', main)
    main['num_3'] = count_trend('Very Bullish', main)
    main['num_4'] = count_trend('Very Bearish', main)
    main['num'] = main['num_1'] + main['num_2'] + main['num_3'] + main['num_4']
    main = main.drop(['num_1', 'num_2', 'num_3', 'num_4'], axis=1)

    main['Date_r'] = main['Date']
    main['Open_r'] = main['Open']
    main['High_r'] = main['High']
    main['Low_r'] = main['Low']
    main['Close_r'] = main['Close']
    main['Avg_r'] = main['VWAP']

    name = nse.get_quote(sym)['companyName']
    # naL.append(str(name) + '_' + str(s_date) + '_' + str(t_date)  + '.xlsx')
    #main.to_excel(str(name) + '_' + str(s_date) + '_' + str(t_date) + '.xlsx', index=False)
    return main
    # print('Got The Data for  '+ str(int(((sym+1) / len(symbol))*100)) + '%'+ ' : ' +str(name))


app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/generate", methods=['POST'])
def download_report():
    sym = str(request.form['sym'])
    s_date = str(request.form['start'])
    t_date = str(request.form['end'])
    s_date = pd.to_datetime(s_date)
    t_date = pd.to_datetime(t_date)
    s_date = s_date.date()
    t_date = t_date.date()
    file_name = str(sym) + '_' + str(s_date) + '_' + str(t_date)
    df = report(s_date, t_date, sym)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    output.seek(0)
    return send_file(output, attachment_filename= file_name + '.xlsx', as_attachment=True)
    #print(df.head())
    #return Response(report(s_date, t_date, sym), mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=student_report.xls"})

@app.route("/boot")
def about1():
    name = 'satnam g'
    return render_template('boot.html', name = name)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(port=5000)
