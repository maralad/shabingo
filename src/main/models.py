#!/usr/bin/env python
__author__ = 'Donagh Corcoran'

from django import forms
from django.db import models
from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User
from paypal.standard.ipn.signals import payment_was_successful
from django.conf import settings
import random
import string   
import boto
import logging
import os
import datetime
logger = logging.getLogger('main')

def mylogfunction():
    logger.debug("this is a debug message!")
   
    
class SignUp(models.Model):
    for_you = models.BooleanField(default=True, verbose_name = "Email me Updates")
    first_name= models.CharField(max_length=20, null=True, blank=True)
    last_name= models.CharField(max_length=20, null=True, blank=True)
    email= models.EmailField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
  ## channelurl=models.TextField(max_length=200, validators=[URLValidator()])
    def __unicode__(self):
        return smart_unicode(self.first_name + " " + self.last_name + " | " + self.email)    

def content_file_name(instance, filename):
    f_name=''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(24))
   # #Although this variable assignment seems to do nothing but if its not there the above 
   #f_folder variable does not change and therfore all files go into the one folder for 
   #one day instead of just the files of one upload
    today_folder =datetime.date.today().strftime("%Y/%m/%d")
    path = os.path.join('MEDIA_ROOT','documents',today_folder) 
    
    str_file=str(filename)
    strip_ext=str_file.split('.')      
    ext=strip_ext[-1] 
    filenm = f_name+'.'+ext
    #logger.debug('@@@@@@@@@@@@@@@@@@@@@@@@@:: What path::{0} filenm:: {1} ::@@@@@@@@@@@@@@@@@@@@@@@@@@@'.format(path,filenm))
    return os.path.join(path, filenm)

class Document(models.Model):

    #fff_folder=''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(12))
    docfile1 =models.FileField(max_length=500,upload_to=content_file_name)
    docfile = models.FileField(max_length=500,upload_to=content_file_name)
    docfile2 =models.FileField(upload_to=content_file_name)
    
    category= models.CharField(max_length=100, null=False, blank=False)
    usersname =models.CharField(max_length=100, null=False, blank=False)
    name= models.CharField(max_length=27, null=False, blank=False)
    description=models.CharField(max_length=500, null=False, blank=False)
    isover18s =models.BooleanField(default=False, verbose_name = "Over 18 Content advised?")
    published =models.BooleanField(default=True)
    approved=  models.BooleanField(default=False)
    shares= models.IntegerField(default=0)
    document_type=models.PositiveSmallIntegerField(default=0)
    
    price=models.IntegerField(verbose_name="Price is in Dollars MAX is $999")
    dateUploaded=models.DateTimeField(auto_now_add=True, auto_now=False)
    preview_views=models.IntegerField(verbose_name="Preview Views")
    views=models.IntegerField(verbose_name="Paid Views")
    
    users= models.ManyToManyField(User)
    #Here we need to rename various media so we do not have duplicates
    def rename_prev(self,new_name):
        try:
            self.docfile1.name = new_name
            self.save()
        except Exception as e:
	          logger.debug('Problem with rename_Prev error is : {0}'.format(e))
    
    def rename_thumb(self,new_name):
        try:
            self.docfile2.name = new_name
            self.save()
        except Exception as e:
	          logger.debug('Problem with rename_thumb error is : {0}'.format(e))

            
	
	
    def rename_shab(self, new_name):
        try:
            self.docfile.name=new_name
            self.save()
        except Exception as e:
            logger.debug('Problem with rename_Prev error is : {0}'.format(e))
        

    #def save(self, *args, **kwargs):
     #   super(MyModel, self).save(*args, **kwargs)
      #  if self.docfile:
       #     conn = boto.s3.connection.S3Connection(
        #                        settings.AWS_ACCESS_KEY_ID,
         #                       settings.AWS_SECRET_ACCESS_KEY)
          #  # If the bucket already exists, this finds that, rather than creating.
           # bucket = conn.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            #k = boto.s3.key.Key(bucket)
            #k.key = settings.MEDIA_DIRECTORY + self.docfile
            #k.set_acl('private')

class UploadRaw(models.Model):
    file = models.FileField(max_length=500,upload_to='files/%Y/%m/%d')
    #TODO figure out what we are doing with this
class Payments(models.Model):
    pay_pal_email=models.EmailField(null=False, blank=False)
    userID=models.OneToOneField(User)
    

class Post(models.Model):
    title = models.CharField(max_length=100)
    body =models.TextField()
    created = models.DateTimeField()
    #tags = TaggableManager
    
    def __unicode__(self):
        return self.title
  
    #Here we keep all the Resellers stripe information which is connected to our account 
class Reseller_token(models.Model):
    token=models.CharField(max_length=50, null=False, blank=False)
    userID=models.OneToOneField(User)
    stripe_email=models.EmailField(null=False, blank=False)
    access_token=models.CharField(max_length=50, null=False, blank=False)
    livemode=models.BooleanField(default=False)
    refresh_token =models.CharField(max_length=100, null=False, blank=False)
    token_type=models.CharField(max_length=50, null=False, blank=False)
    stripe_publishable_key=models.CharField(max_length=50, null=False, blank=False)
    stripe_user_id=models.CharField(max_length=50, null=False, blank=False)
    scope= models.CharField(max_length=50, null=False, blank=False)
