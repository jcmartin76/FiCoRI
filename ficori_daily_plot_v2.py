#!/Users/oliveros/anaconda/bin/python

import matplotlib
matplotlib.use('Agg')

import numpy
import numpy as np
import datetime

import matplotlib.dates as mdates 
import matplotlib.pyplot as plt

from matplotlib import rcParams
rcParams['text.usetex'] = True

import os
from shutil import copyfile

import tweepy

import socket

##############
# This function is the twitter API setup.
def setup_api():
  auth = tweepy.OAuthHandler('6qIx6jJ5WxB9fN3H7dg7yE0T4', 
        'tlb7R74SP0kMiLJuJbzpzSB8ir85wPgWdDpUa8Yr90olJB4S08')
  auth.set_access_token('967497555675246593-BiWkgrNs6HaIOU0468cLui1BQt7mSHA',
        'N4gBMN5Ezw3KvtwFM21cxisKlAhdAXmy3pkEOfzTB3T9V')
  return tweepy.API(auth)

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def easyAverage(datetimeList): #----> Func Declaration
    sumOfTime=sum(map(datetime.datetime.timestamp,datetimeList))
    '''
    timestamp function changes the datetime object to a unix timestamp sort of a format.
    So I have used here a map to just change all the datetime object into a unix time stamp form , added them using sum and store them into sum variable.
    '''
    length=len(datetimeList) #----> Self Explanatory

    averageTimeInTimeStampFormat=datetime.datetime.fromtimestamp(sumOfTime/length)
    '''
    fromtimestamp function returns a datetime object from a unix timestamp.
    '''

    timeInHumanReadableForm=datetime.datetime.strftime(averageTimeInTimeStampFormat,"%Y-%m-%d %H:%M:%S") #----> strftime to change the datetime object to string.
    return averageTimeInTimeStampFormat
    #timeInHumanReadableForm

###### Processing program
def processing_data(idate):

    #idate = datetime.datetime.today() - datetime.timedelta(1)
    #idate = datetime.datetime(2018,5,21)

    date_format = mdates.DateFormatter('%H')
    props = dict(boxstyle='round', facecolor='orange', alpha=0.5)
    api = setup_api()

    #if os.path.exists('/Users/oliveros/Sync/ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(idate.year,idate.month,idate.day)):
    if os.path.exists(Syndirory+'ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(idate.year,idate.month,idate.day)):
        print('Spectra already plotted %s'%datetime.datetime.today())

    else:
        try:
            print('Preparing Spectra')
            filea = directory+'Data_Auto_Ant_A_%d%02d%02d.dat.gz'%(idate.year,idate.month,idate.day)
            fileb = directory+'Data_Auto_Ant_B_%d%02d%02d.dat.gz'%(idate.year,idate.month,idate.day)
            filec = directory+'Data_Cross_phase_Ant_AB_%d%02d%02d.dat.gz'%(idate.year,idate.month,idate.day)
            print("%s\n%s\n%s\n"%(filea,fileb,filec))
            
        #   Read and load data and time 
            timestamp = numpy.loadtxt(filea, delimiter=' ',dtype='str', usecols=(0,1))
            dataa = numpy.loadtxt(filea, delimiter=' ',dtype='float',usecols=range(2,1026))

            dataa = np.array([np.mean(data1a,axis=0) for data1a in chunkIt(dataa,1439)])
            dataa.shape
        #   Timestamp array definition and fix
            timestamp = numpy.apply_along_axis(lambda d: d[0] + ' ' + d[1], 1, timestamp)
            dates_list=[]
            for date in timestamp:
                try:
                    stDate = date
                    dates_list.append(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f'))
            #            print(stDate,' try')

                except:
                    stDate = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(microseconds=1)
                    dates_list.append(stDate)

            dates_list = np.array([easyAverage(data1a) for data1a in chunkIt(dates_list,1439)])
        #    print(dates_list)
        #   Frequency array definition
            B_f = 800
            Fr=numpy.linspace(0,B_f,dataa.shape[1])

            fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=True)
            fig.text(0.93, 0.76,'Antenna West', horizontalalignment='center',verticalalignment='center',rotation='vertical',bbox=props,fontsize=8)
            fig.text(0.93, 0.50,'Antenna East', horizontalalignment='center',verticalalignment='center',rotation='vertical',bbox=props,fontsize=8)
            fig.text(0.93, 0.23,'Cross Correlation', horizontalalignment='center',verticalalignment='center',rotation='vertical',bbox=props,fontsize=8)

            ax1.pcolormesh(dates_list, Fr, numpy.transpose(numpy.log10(dataa)), cmap='jet',vmin=5.75,vmax=7.5)
            ax1.set_title(r"FiCoRI - Observatorio Astron\'omico Nacional")

            dataa = 0
            dataa = numpy.loadtxt(fileb, delimiter=' ',dtype='float',usecols=range(2,1026))
            dataa = np.array([np.mean(data1a,axis=0) for data1a in chunkIt(dataa,1439)])

            fig.subplots_adjust(hspace=0.1)
            ax2.pcolormesh(dates_list, Fr, numpy.transpose(numpy.log10(dataa)), cmap='jet',vmin=5.0,vmax=7.5)
            ax2.set_ylabel('Frequency [MHz]')


            dataa = 0
            dataa = np.abs(numpy.loadtxt(filec, delimiter=' ',dtype='complex',usecols=range(2,1026)))
            dataa = np.array([np.mean(data1a,axis=0) for data1a in chunkIt(dataa,1439)])

            fig.subplots_adjust(hspace=0.1)
            ax3.pcolormesh(dates_list, Fr, numpy.transpose(numpy.log10(numpy.abs(dataa))), cmap='jet',vmin=5.0,vmax=7.5)
            plt.xlabel('Time (UTC) %d-%02d-%02d'%(dates_list[0].year,dates_list[0].month,dates_list[0].day))
            ax3.xaxis.set_major_formatter(date_format)

            plt.savefig(Syndirory+'ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(dates_list[0].year,dates_list[0].month,dates_list[0].day),format='jpg',dpi=300)

            plt.close("all")

            copyfile(Syndirory+'ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(dates_list[0].year,dates_list[0].month,dates_list[0].day), Syndirory+'ficori_test/images/latest_spectra.jpg')
            if namehost == 'sue.ssl.berkeley.edu':
                copyfile('/Users/oliveros/Sync/ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(dates_list[0].year,dates_list[0].month,dates_list[0].day),'/Users/oliveros/Box Sync/ficori_spectra/daily/ficori_plot_%d%02d%02d.jpg'%(dates_list[0].year,dates_list[0].month,dates_list[0].day))
                copyfile('/Users/oliveros/Sync/ficori_test/images/latest_spectra.jpg','/Users/oliveros/Box Sync/ficori_spectra/latest_spectra.jpg')

            # Send the tweet.
            fn = Syndirory+'ficori_test/images/latest_spectra.jpg'
            status = '%d-%02d-%02d radio spectrum. Posted by the FiCoRI bot.'%(dates_list[0].year,dates_list[0].month,dates_list[0].day)
#
            api.update_with_media(fn, status=status)
            print('tweet posted')

        except:
            print("General Error: Possible problem with the data files")

#Main#

###### Directories
namehost = socket.gethostname()

if namehost == 'raspberrypi':
    directory = '/media/pi/ficori_hdd/'
    Syndirory = '/home/pi/Sync/'

if namehost == 'sue.ssl.berkeley.edu':
    directory = '/Users/oliveros/Box Sync/ficori/'
    Syndirory = '/Volumes/Mnemosyne/Sync/'

print(namehost, directory, Syndirory)

### Para operaciones normales usar los siguientes comandos
###
date = datetime.datetime.today() - datetime.timedelta(1)
processing_data(date)

### Si se estan reprocesando los espectos se deben descomentar  
### las siguientes lineas
###
### Reprocessing

#date_array = [datetime.datetime.today() - datetime.timedelta(x) for  x in range (15)]
#date_array = date_array[1::]
#date_array.sort()

#for date in date_array:
#    processing_data(date)

