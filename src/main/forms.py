#!/usr/bin/env python
__author__ = 'Donagh Corcoran'

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from models import UploadRaw

from .models import SignUp
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import logging

class UploadRawForm(forms.ModelForm):

    class Meta:
        model = UploadRaw
        
        
class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

class DocumentForm(forms.Form):# Here is where we save the videos
    price= forms.IntegerField(max_value=1000, min_value=1,
                              label='1. Set Price in $',
                              help_text='*')
        
    docfile = forms.FileField(allow_empty_file= True,
        label='3 Upload Full Shabingo (Full Video)',
        help_text='*')
    
    docfile1 = forms.FileField(allow_empty_file= True,
        label='2. Upload Preview of Video',
        help_text='*')
        
    docfile2=forms.FileField(allow_empty_file= True,
        label='4. Upload a Poster for your Preview.',
        help_text='*')
         
    name= forms.CharField(max_length=27, widget=forms.TextInput,help_text='* Max 27 characters.')
    
    description=forms.CharField(max_length=500, widget=forms.Textarea,help_text='*')
    
    RADIO_CHOICES = (
        ('none', "No Category"),
        ('one', "Music"),
        ('two', "Movie"),
        ('three', "Tutorial "),
    )
    category=forms.ChoiceField(
        choices=RADIO_CHOICES,
        widget=forms.RadioSelect(),
        label ='7. Select a Category for your upload',
        required=False,
        initial=False
        )
  
    isover18s =  forms.BooleanField(
        label='8. Is over 18 content advised?', 
        required=False,#TODO use this to sort out error problem
        initial=False
     )
     
    document_type   = forms.BooleanField(
        label='Allow users to pay by sharing also ?',
        required=False,
        initial=False
    )
    #dateUploaded= forms.DateTimeField(input_formats=None)
    
    #preview_views=forms.HiddenInput
    #views=forms.HiddenInput
        
    def clean_content(self):
        
        #Here we do some extra checks to make sure
        #the correct media files are being uploaded and that they do not
        #exceed the byte size limit
        #In addition to this we also have more validation on the 
        #front end in jquery
        if self.cleaned_data['docfile']:
            content = self.cleaned_data['docfile']
        else: content=None    
        if self.cleaned_data['docfile1']:
            content1= self.cleaned_data['docfile1']
        else: content1=None
        if self.cleaned_data['docfile2']:
             content2 =self.cleaned_data['docfile2']
        else: content2=None
        if content:
            content_type = content.content_type.split('/')[0]
            
            if content_type in settings.CONTENT_TYPES:
                if content._size > settings.MAX_UPLOAD_SIZE:
                    
                    raise forms.ValidationError(_('Please keep Full Shabingo Video Filesize under %s. Current filesize %s')
                                                % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat
                                                   (content._size)))
            else:
                
                #logger.debug('Forms- File Not supported: Raise Error')
                raise forms.ValidationError(_('File type is not supported, Preferred videos formats: .mp4 or .mov')
                                            ,code='Wrong File Format')
        if content1 :    
            content_type = content1.content_type.split('/')[0]
        
            if content_type in settings.CONTENT_TYPES:
                if content1._size > settings.MAX_UPLOAD_1_SIZE:
                    
                    raise forms.ValidationError(_('Please keep Video Preview filesize under %s. Current filesize %s')
                                                % (filesizeformat(settings.MAX_UPLOAD_1_SIZE), filesizeformat
                                                   (content1._size)))
            else:
                
                #logger.debug('Forms- File Not supported: Raise Error')
                raise forms.ValidationError(_('File type is not supported, Preferred videos formats: .mp4 or .mov')
                                            ,code='Wrong File Format')
        
        if content2 :
            content_type = content2.content_type.split('/')[0]
            
            if content_type in settings.CONTENT_TYPES:
                if content2._size > settings.MAX_UPLOAD_2_SIZE:
                    
                    raise forms.ValidationError(_('Please keep Poster filesize under %s. Current filesize %s')
                                                % (filesizeformat(settings.MAX_UPLOAD_2_SIZE), filesizeformat
                                                   (content2._size)))
            else:
                
                #logger.debug('Forms- File Not supported: Raise Error')
                raise forms.ValidationError(_('File type is not supported, Preferred videos formats: .png or .jpg')
                                            ,code='Wrong File Format')
       
        #return content

        
        
    
class MyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
   ## urlchannel= forms.CharField(max_length=200, label='URL link to current Video Channel if any:')
    
    class Meta:
        model = User
        fields=('username', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        User= super(MyRegistrationForm, self).save(commit=False)
        User.email = self.cleaned_data["email"]
        if commit:
            User.save()
        
        return User
    

class SignUpForm(forms.ModelForm):
    
    class Meta:
        model = SignUp
        


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'cols': 23, 'rows': 1}))
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 23, 'rows': 10}))
    sender = forms.EmailField(widget=forms.Textarea(attrs={'cols': 23, 'rows': 1}))
    cc_myself = forms.BooleanField(required=False)
    
    
    

    
    
    
    
