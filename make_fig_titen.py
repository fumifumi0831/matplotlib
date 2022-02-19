#!/usr/bin/env python
# coding: utf-8

# In[87]:


# パラメータ自動推定
'''
ダム操作シミュレーションによる事前放流確保容量の計算

検討条件：
-流入量0m3/s
-ダムHVを考慮
-最大放流量は洪水量
-放流施設の敷高を考慮
-放流の原則を考慮
'''
#%%
import os
from re import U
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from scipy import interpolate
import numpy.random as random
import datetime as dt
import matplotlib.dates as mdates

#%matplotlib


# mpl.rcParams['font.family'] = 'IPAexGothic'
mpl.rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
mpl.rcParams['font.size'] = '8'


# In[88]:


def makedirs(path):
  if not os.path.isdir(path):
      os.makedirs(path)


# In[91]:


def drawfighydro(df,outpng,title,maindir,titenset_xy):
  outfile = outpng   
  yminQ,ymaxQ,dy=titenset_xy
#dfのデータフレームのA列目とB列目を参照
  xmin = df.index[0]
  xmax = df.index[-1]
  ymin2=yminQ; ymax2=ymaxQ
  
  fig = plt.figure(figsize=(8,5))
  fig.patch.set_facecolor('xkcd:white')#背景を白色にするため追記

  #ダム流量
  ax = plt.subplot(111)
  ax.set_title(title,fontsize=10) 
    
  #x軸を時間軸に変更
  ax.xaxis_date()
  
  ax.set_xlabel('時刻')
  
  #x軸の範囲(limit)を指定
  ax.set_xlim(xmin,xmax)
  #y軸の範囲(limit)を指定
  ax.set_ylabel('流量 (m$^3$/s)')
  ax.set_ylim(ymin2,ymax2)

  #multiplelocateorは時間軸に○おきごとmajorは表示する目盛り、minorは目盛りのみ
  ax.yaxis.set_major_locator(tick.MultipleLocator(dy))
  ax.yaxis.set_minor_locator(tick.MultipleLocator(int(dy/5)))
  ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
  ax.xaxis.set_major_locator(tick.MultipleLocator(1))
  ax.xaxis.set_minor_locator(tick.MultipleLocator(1/24))

  ax.grid()

  fontsize = 9

  ax.plot(df.index,df['case0010'],'-', lw=1.5, color='magenta', label='case0010') 
  ax.plot(df.index,df['case0000'],'-', lw=1.5, color='darkblue', label='case0000')
  ax.legend(loc='center left')

  plt.savefig(outfile, dpi=200, bbox_inches='tight', pad_inches=0.1)
  plt.show()
  plt.clf()
  plt.close()


# In[ ]:


def main():
    #パス取得
    maindir = os.getcwd()
    datadir = os.path.join(maindir,'out.d')

    #保存するディレクトリ作成
    date='22.02.18'
    pngdir  = os.path.join(maindir,'png.d',date)
    csvdir  = os.path.join(maindir,'csv.d',date)
    makedirs(pngdir)
    makedirs(csvdir)
 
#     prefixs=['.Kkeikaku_Dgenkyo.Dgenkyo_zyoman.','.Kkeikaku_Dgenkyo.Dgenkyo_seigen.','.Kkeikaku_Dgenkyo.Dgenkyo_seigen_allkaizen.','.Kkeikaku_Dgenkyo.Dgenkyo_unnyou.','.Kkeikaku_Dgenkyo.Dgenkyo_unnyou_allkaizen.','.Kkeikaku_Dgenkyo.Dgenkyo_seigen_Qtama.']
#     prefix_dics={'.Kkeikaku_Dgenkyo.Dgenkyo_zyoman.':['case1000'],
#                  '.Kkeikaku_Dgenkyo.Dgenkyo_seigen.':['case0000','case0020','case0120','case0121','case0030','case0130','case0131','case0040','case0140','case0141','case0050','case0060','case0070'],
#                  '.Kkeikaku_Dgenkyo.Dgenkyo_seigen_allkaizen.':['case0100'],
#                  '.Kkeikaku_Dgenkyo.Dgenkyo_unnyou.':['case0010'],
#                  '.Kkeikaku_Dgenkyo.Dgenkyo_unnyou_allkaizen.':['case0110'],
#                  '.Kkeikaku_Dgenkyo.Dgenkyo_seigen_Qtama.':['case0021']
#                 }

#     cases=['case1000','case0000','case0020','case0120','case0121','case0030','case0130','case0131','case0040','case0140','case0141','case0050','case0060','case0070','case0100','case0010','case0110','case0021']


#     cases_dics={'case1000':'全ダム常時満水位等から開始',
#                 'case0000':'全ダム制限水位等から開始',
#                 'case0020':'鎧畑ダムのみ運用水位等から開始',
#                 'case0120':'鎧畑ダム改善操作・全ダム制限水位から開始',
#                 'case0121':'鎧畑ダム改善操作・鎧畑のみ運用水位等から開始',
#                 'case0030':'岩見ダムのみ運用水位等から開始',
#                 'case0130':'岩見ダム改善操作・全ダム制限水位から開始',
#                 'case0131':'岩見ダム改善操作・岩見のみ運用水位等から開始',
#                 'case0040':'大松川ダムのみ運用水位等から開始',
#                 'case0140':'大松川ダム改善操作・全ダム制限水位等から開始',
#                 'case0141':'大松川ダム改善操作・大松川のみ運用水位等から開始',
#                 'case0050':'皆瀬ダムのみ運用水位等から開始',
#                 'case0060':'玉川ダムのみ運用水位等から開始',
#                 'case0070':'協和ダムのみ運用水位等から開始',
#                 'case0100':'改善操作・全ダム制限水位等から開始',
#                 'case0010':'全ダム運用水位等から開始',
#                 'case0110':'改善操作・全ダム運用水位等から開始',
#                 'case0021':'鎧畑ダムのみ運用水位等から開始（玉川ダム100m3/s放流）' ,            
#                 }
    hakeis=['19690728','19810822','19870816','20020810','20170722','20170823','20180517']
    hakeis_dics={'19690728':'昭和44年7月型','19810822':'昭和56年8月型','19870816':'昭和62年8月型','20020810':'平成14年8月型',
                 '20170722':'平成29年7月型','20170823':'平成29年8月型','20180517':'平成30年5月型'}

    hakeis_datetimes={'19690728':dt.datetime(1969,7,27,9,0),
                      '19810822':dt.datetime(1981,8,21,9,0),
                      '19870816':dt.datetime(1987,8,16,9,0),
                      '20020810':dt.datetime(2002,8, 7,9,0),
                      '20170722':dt.datetime(2017,7,22,0,0),
                      '20170823':dt.datetime(2017,8,23,0,0),
                      '20180517':dt.datetime(2018,5,17,0,0),
                      }
#                       [yminQ, ymaxQ, dy]
    titenset_dics = {11:[0.0,1000,100],
                     15:[0.0,1500,100],
                     17:[0.0,3000,200],
                     29:[0.0,2000,200],
                     48:[0.0,2400,200],
                     53:[0.0,2400,200],
                     54:[0.0,4000,500],
                     75:[0.0,300,50],
                     77:[0.0,100,10],
                     79:[0.0,100,10],
                     81:[0.0,4000,500],
                     82:[0.0,12000,1000],
                     86:[0.0,1000,100],
                     94:[0.0,5000,500],
                     97:[0.0,5000,500],
                     99:[0.0,4000,500],
                     105:[0.0,4000,500],
                     110:[0.0,5000,500],
                     111:[0.0,12000,1000],
                     115:[0.0,1000,100],
                     124:[0.0,1000,100],
                     127:[0.0,12000,1000],
                     130:[0.0,1000,100],
                   }
    
    kibos = ['jisseki','W100','W150','W100_1.2','W150_1.2']
    kibo_dics = {'jisseki':'実績','W100':'W=1/100','W150':'W=1/150',
               'W100_1.2':'W=1/100の1.2倍','W150_1.2':'W=1/150の1.2倍'}
    base_dics = {'Tsubakigawa':'椿川地点'}

    
    usecols  = [11, 15 ,17, 29, 48, 53, 54, 75, 77, 79, 81, 82, 86, 94, 97, 99, 105, 110, 111, 115, 124, 127, 130]
    colname_dics = {11:'柳田橋',
                    15:'雄物川橋',
                    17:'横手川',
                    29:'長野',
                    48:'皆瀬川（成瀬川合流前）',
                    53:'安養寺',
                    54:'岩崎橋',
                    75:'大松川ダム下流',
                    77:'相野々ダム下流',
                    79:'金沢ダム下流',
                    81:'横手川下流端',
                    82:'大曲橋',
                    86:'丸子川',
                    94:'玉川（小保内川合流後）',
                    97:'広久内',
                    99:'角館',
                    105:'長野',
                    110:'玉川橋',
                    111:'神宮寺',
                    115:'樽岡川下流端',
                    124:'淀川下流端',
                    127:'椿川基準点',
                    130:'岩見川下流端'}
        
    for hakei in hakeis:
        starttime = hakeis_datetimes[hakei]
        for kibo in kibos:  
            for usecol in usecols: 

                #inputするファイルの指定
                infilename = hakei+'_'+'Tsubakigawa'+'_'+kibo+'_'+str(usecol)+'_'+colname_dics[usecol]+'.csv'
                print(infilename)

                #inputするcsvファイルの指定
                incsv = os.path.join(datadir,'titen',infilename)

                #csvファイルの読み込み
                df = pd.read_csv(incsv,header=None,skiprows=1,
                                 usecols=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],
                                 names=['case1000','case0000','case0020','case0120','case0121','case0030','case0130','case0131','case0040','case0140','case0141','case0050','case0060','case0070','case0100','case0010','case0110','case0021'],
                                 encoding='SJIS')

                #outputするdirを選択
                outfilename = hakei+'_'+'Tsubakigawa'+'_'+kibo+'_'+str(usecol)+'_'+colname_dics[usecol]
                subpngdir = os.path.join(pngdir,'titen')
                print(subpngdir)
                outpng = os.path.join(subpngdir,outfilename+'.png')
                print(outpng)

                #グラフに必要なタイトルとx軸の時刻の指定
                title = '降雨波形:'+hakeis_dics[hakei]+'('+kibo_dics[kibo]+'), '+colname_dics[usecol]
                starttime = hakeis_datetimes[hakei]
                df['datetime'] = starttime

                #グラフのx軸に必要な時刻の読み込み
                for i in range(len(df)): #最終行まで一時間刻みで読み込む
                    df['datetime'][i] = starttime + dt.timedelta(hours=i) #一行ごとに一時間分だけ値を更新する    
                df = df.set_index(['datetime'])

                #グラフのリミットを決める
                titenset_xy = titenset_dics[usecol]

                #描画のサブルーチンに飛ぶ
                drawfighydro(df,outpng,title,maindir,titenset_xy)

#             # ika kesite
#             dfmax=dfall.max()
#             dfmax['cond'] = prefix
#             dfmax['hakei'] = hakei
#             dfmax['kibo']  = kibo
#             dfmax['titen'] = colname_dics[usecol]
#             dfmax['case'] =  case
#               # dfmax['fname'] = infilename
#               # dfmax['basepoint'] = basepoint
#             dfmaxall = pd.concat([dfmaxall,dfmax.T],axis=1)
#             # dftable = dfmaxall.T.set_index(['hakei','kibo','case'])
#             # dfmaxall_all = pd.concat([dfmaxall_all,dftable],axis=0)
#           dfmaxall.to_csv(outmaxcsv,encoding='SJIS',float_format='%10.2f')

if __name__ == '__main__':
    main()


# In[15]:


hakei=['19690728']
for hake in hakei:
    print(type(hake))


type('Tsubakigawa')


# In[19]:


type(str(11))


# In[ ]:




