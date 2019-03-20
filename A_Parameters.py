from numpy import load



def Parameters():

    change       = [0.003, 0.004]
    epoch        = [350]
    batch        = [72]
    drop         = [0.3, 0.6, 0.8]
    SourceStart  = ["2005-01-01"]
    TestFromTo   = [
                   ["2018-01-02","2018-01-31"],
                   ["2018-02-01","2018-02-28"],
                   ["2018-03-01","2018-03-29"],
                   ["2018-04-03","2018-04-30"],
                   ["2018-05-02","2018-05-31"],
                   ["2018-06-01","2018-06-29"],
                   ["2018-07-03","2018-07-31"],
                   ["2018-08-01","2018-08-31"],
                   ["2018-09-03","2018-09-28"],
                   ["2018-10-02","2018-10-31"],
                   ["2018-11-01","2018-11-30"],
                   ["2018-12-03","2018-12-28"],
                   ]

    P = []
    idx = 0
    for i in change:
        for j in epoch:
            for k in batch:
                for l in drop:
                    for m in SourceStart:
                        for n, o in TestFromTo:
                            #for p in TestTo:
                            pline = [i, j, k, l, m, n, o]
                            P.append(pline)
        
    return (P)



if __name__ == '__main__':
    import quandl
    quandl.ApiConfig.api_key = "ZDfv2NCGxLMv-KNxuWVV"
    P = Parameters()
    SourceStart = "2017-12-01"
    SourceEnd   = "2019-01-01"
    for p in range(len(P)):
        TestFrom     = P[p][5] 
        TestTo       = P[p][6]
        dateindex = quandl.get("HKEX/01055", start_date=SourceStart, end_date=SourceEnd)["Nominal Price"].index
        NoTestFrom   = list(dateindex.strftime('%Y-%m-%d')).index(TestFrom)+1
        NoTestTo     = list(dateindex.strftime('%Y-%m-%d')).index(TestTo)+1
        print ("Test from " + str(TestFrom) + "/" + str(NoTestFrom) + " To " + str(TestTo) + "/" + str(NoTestTo))
