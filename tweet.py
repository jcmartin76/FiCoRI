#!/usr/bin/python

import os
import tweepy
import sys

# This function pretty much taken directly from a tweepy example.
def setup_api():
  auth = tweepy.OAuthHandler('6qIx6jJ5WxB9fN3H7dg7yE0T4', 
        'tlb7R74SP0kMiLJuJbzpzSB8ir85wPgWdDpUa8Yr90olJB4S08')
  auth.set_access_token('967497555675246593-BiWkgrNs6HaIOU0468cLui1BQt7mSHA',
        'N4gBMN5Ezw3KvtwFM21cxisKlAhdAXmy3pkEOfzTB3T9V')
  return tweepy.API(auth)

# Authorize.
api = setup_api()

# Get the parameters from the command line. The first is the
# name of the image file. The second is the tweet text.
fn = 'images/latest_spectra.jpg'
status = '2018-03-01 radio spectrograph. Posted by the FiCoRI bot.'

# Send the tweet.
api.update_with_media(fn, status=status)

