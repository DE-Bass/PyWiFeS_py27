import pickle

#------------------------------------------------------
bias_obs = [
   'T2m3wr-20181119.190031-0039',
   'T2m3wr-20181119.191309-0045',
   'T2m3wr-20181119.191103-0044',
   'T2m3wr-20181119.185825-0038',
   'T2m3wr-20181119.185412-0036',
   'T2m3wr-20181119.185618-0037',
   'T2m3wr-20181119.190650-0042',
   'T2m3wr-20181119.190237-0040',
   'T2m3wr-20181119.190444-0041',
   'T2m3wr-20181119.190856-0043',
    ]

domeflat_obs = [
   'T2m3wr-20181119.181047-0021',
   'T2m3wr-20181119.181806-0024',
   'T2m3wr-20181119.181540-0023',
   'T2m3wr-20181119.161723-0007',
   'T2m3wr-20181119.163454-0015',
   'T2m3wr-20181119.161512-0006',
   'T2m3wr-20181119.162146-0009',
   'T2m3wr-20181119.181314-0022',
   'T2m3wr-20181119.161934-0008',
   'T2m3wr-20181119.182033-0025',
   'T2m3wr-20181119.161149-0005',
    ]

twiflat_obs = [
    ]

dark_obs = [
    ]

arc_obs = [
   'T2m3wr-20181119.123651-0001',
    ]

wire_obs = [
   'T2m3wr-20181119.184646-0035',
   'T2m3wr-20181119.182404-0026',
   'T2m3wr-20181119.183123-0029',
   'T2m3wr-20181119.183801-0031',
   'T2m3wr-20181119.183350-0030',
   'T2m3wr-20181119.184012-0032',
   'T2m3wr-20181119.184223-0033',
   'T2m3wr-20181119.182631-0027',
   'T2m3wr-20181119.182857-0028',
   'T2m3wr-20181119.184435-0034',
    ]

#------------------------------------------------------
sci_obs = [
    # 2018ioa
    {'sci'  : ['T2m3wr-20181119.133304-0003',
               'T2m3wr-20181119.135514-0004',
               'T2m3wr-20181119.131054-0002'],
     'sky'  : []},
    ]

#------------------------------------------------------
std_obs = [
    ]

#------------------------------------------------------
night_data = {
    'bias' : bias_obs,
    'domeflat' : domeflat_obs,
    'twiflat' : twiflat_obs,
    'dark' : dark_obs,
    'wire' : wire_obs,
    'arc'  : arc_obs,
    'sci'  : sci_obs,
    'std'  : std_obs}

f1 = open('wifesR_20181119_metadata.pkl', 'w')
pickle.dump(night_data, f1)
f1.close()
