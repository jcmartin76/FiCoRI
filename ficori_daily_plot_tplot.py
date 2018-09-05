import numpy
import numpy as np
import datetime

import pytplot
import calendar

import os
import imgkit

from shutil import copyfile

import tweepy

import socket

##############
# This function is the twitter API setup.
#def setup_api():
#  auth = tweepy.OAuthHandler('6qIx6jJ5WxB9fN3H7dg7yE0T4', 
#        'tlb7R74SP0kMiLJuJbzpzSB8ir85wPgWdDpUa8Yr90olJB4S08')
#  auth.set_access_token('967497555675246593-BiWkgrNs6HaIOU0468cLui1BQt7mSHA',
#        'N4gBMN5Ezw3KvtwFM21cxisKlAhdAXmy3pkEOfzTB3T9V')
#  return tweepy.API(auth)

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
def processing_data(idate, directory, Syndirory):

    '''if os.path.exists('/Users/oliveros/Sync/ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(idate.year,idate.month,idate.day)):'''
    if os.path.exists(Syndirory+'ficori_test/images/ficori_plot_%d%02d%02d.html'%
(idate.year,idate.month,idate.day)):
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
            tt = [calendar.timegm(i.timetuple()) for i in dates_list]             


            dataa = numpy.loadtxt(filea, delimiter=' ',dtype='float',usecols=range(2,1026))
            dataa = np.array([np.mean(data1a,axis=0) for data1a in chunkIt(dataa,1439)])

            datab = numpy.loadtxt(fileb, delimiter=' ',dtype='float',usecols=range(2,1026))
            datab = np.array([np.mean(data1a,axis=0) for data1a in chunkIt(datab,1439)])

            dataab = np.abs(numpy.loadtxt(filec, delimiter=' ',dtype='complex',usecols=range(2,1026)))
            dataab = np.array([np.mean(data1a,axis=0) for data1a in chunkIt(dataab,1439)])

            print('Data loaded...')

            #   Frequency array definition
            Fr=numpy.linspace(780000,800780000,1024)/1000000.

            pytplot.store_data('Auto West', data={'x':tt,'y':dataa,'v':Fr})
            pytplot.store_data('Auto East', data={'x':tt,'y':datab,'v':Fr})
            pytplot.store_data('Cross W-E', data={'x':tt,'y':dataab,'v':Fr})

            del dataa,datab,dataab

            #Options Antenna West
            pytplot.options('Auto West', 'spec', 1)
            pytplot.options('Auto West', 'Colormap', 'rainbow')
            pytplot.options('Auto West', 'ylog', 0)
            pytplot.options('Auto West', 'ytitle', 'Frequency (MHz)')
            pytplot.options('Auto West', 'ztitle', 'Power (a.u.)')
            #pytplot.options('Auto West', 'Colorbar', 0)

            #Options Antenna West
            pytplot.options('Auto East', 'spec', 1)
            pytplot.options('Auto East', 'Colormap', 'rainbow')
            pytplot.options('Auto East', 'ylog', 0)
            pytplot.options('Auto East', 'ytitle', 'Frequency (MHz)')
            pytplot.options('Auto East', 'ztitle', 'Power (a.u.)')
            #pytplot.options('Auto East', 'Colorbar', 0)

            #Options Cross E-W
            pytplot.options('Cross W-E', 'spec', 1)
            pytplot.options('Cross W-E', 'Colormap', 'rainbow')
            pytplot.options('Cross W-E', 'ylog', 0)
            pytplot.options('Cross W-E', 'ytitle', 'Frequency (MHz)')
            pytplot.options('Cross W-E', 'ztitle', 'Power (a.u.)')
            #pytplot.options('Cross W-E', 'Colorbar', 0)

            pytplot.tplot([0,1,2],bokeh=True,save_file=Syndirory+'ficori_test/images/latest_spectra.html'%(dates_list[0].year,dates_list[0].month,dates_list[0].day))

            #Converting html output to jpg
            imgkit.from_file(
            Syndirory+'ficori_test/images/latest_spectra.html'%(dates_list[0].year,dates_list[0].month,dates_list[0].day),
            Syndirory+'ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(dates_list[0].year,dates_list[0].month,dates_list[0].day))

            #Last Spectra copy

            #copyfile(Syndirory+'ficori_test/images/ficori_plot_%d%02d%02d.html'%(dates_list[0].year,dates_list[0].month,dates_list[0].day), 
            #Syndirory+'ficori_test/images/latest_spectra.html')

            copyfile(Syndirory+'ficori_test/images/ficori_plot_%d%02d%02d.jpg'%(dates_list[0].year,dates_list[0].month,dates_list[0].day), 
            Syndirory+'ficori_test/images/latest_spectra.jpg')

            
            # Send the tweet.
            fn = Syndirory+'ficori_test/images/latest_spectra.jpg'
            status = '%d-%02d-%02d radio spectrum, testing new imaging algorithm. Posted by the FiCoRI bot.'%(dates_list[0].year,dates_list[0].month,dates_list[0].day)

            api.update_with_media(fn, status=status)
            print('tweet posted')
            
        except:
            print('There was an error, data maybe corrupt or not yet on server')

def main():                      # Define the main function
    ###### dates range definition

    # testing value
    date = [datetime.datetime.today() - datetime.timedelta(5)]

    # For nomal ops 
    #date = datetime.datetime.today() - datetime.timedelta(1)

    # For reprocessing

    #date_array = [datetime.datetime.today() - datetime.timedelta(x) for  x in range (15)]
    #date_array = date_array[1::]
    #date_array.sort()

    ###### Directories
    namehost = socket.gethostname()

    if namehost == 'raspberrypi':
        directory = '/media/pi/ficori_hdd/'
        Syndirory = '/home/pi/Sync/'

    if namehost == 'sue.ssl.berkeley.edu':
        directory = '/Users/oliveros/Box Sync/ficori/'
        Syndirory = '/Volumes/Mnemosyne/Sync/'

    if namehost == 'ra':
        directory = './'
        Syndirory = './'

    print(namehost, directory, Syndirory)

    ##### Calling processing function
    print(len(date))
    if len(date) == 1:
        processing_data(date[0], directory, Syndirory)
    else:
        for date in date_array:
            processing_data(date, directory, Syndirory)

#Running main
main()

