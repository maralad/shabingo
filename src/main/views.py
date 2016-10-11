#!/usr/bin/env python
__author__ = 'Donagh Corcoran'
"""Django 1.6.4"""
from django.conf import settings
from django.contrib import messages, auth
from forms import MyRegistrationForm
from django.shortcuts import redirect, render, render_to_response, RequestContext, HttpResponseRedirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from models import Document
from forms import DocumentForm
import subprocess
from subprocess import Popen, PIPE
from forms import ContactForm
from django.views.generic import UpdateView, ListView
from django.template.loader import render_to_string
from models import SignUp
from models import Reseller_token
from .forms import SignUpForm
from forms import UploadRawForm
from models import UploadRaw
import datetime
import time
import os
from django.contrib.auth.models import User
from django.core.mail import send_mail
import logging
from paypal.standard.forms import PayPalPaymentsForm
##from django.newforms.widgets import *
from django.core.mail import send_mail, BadHeaderError
import datetime
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.ipn.signals import payment_was_successful

from django import http
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from boto.s3.connection import S3Connection
logger = logging.getLogger('main')
import random
import json
import string
import stripe
from rauth import OAuth2Service



#All the stripe payment keys  and urls
stripe.api_key = settings.LIVE_SECRET_KEY
stripe_connect_service = OAuth2Service(
        name = 'stripe',
        client_id =settings.PROD_CLIENT_ID,
        client_secret = settings.LIVE_SECRET_KEY,
        authorize_url = 'https://connect.stripe.com/oauth/authorize',
        access_token_url = 'https://connect.stripe.com/oauth/token',
        base_url = 'https://api.stripe.com/',
    )

                         
def mylogfunction():
    logger.debug("this is a debug message!")
    
class ItemListView(ListView):
    model = SignUp
    template_name = 'item_list.html'
    
    def get_queryset(self):
        return Item.objects.all()
        
class ItemUpdateView(UpdateView):
    model = SignUp
    form_class = SignUpForm
    template_name = 'item_edit_form.html'
    
    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['pk']
        return super(ItemUpdateView, self).dispatch(*args, **kwargs)
        
    def form_valid(self, form):
        form.save()
        SignUp = Item.objects.get(id=self.item_id)
        return HttpResponse(render_to_string('item_edit_form_success.html', {'item': SignUp}))

def myprofile(request):
  #User profile page...
    if request.method =='POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            
            #messages.success(request, 'Thank you for joining!')
            return HttpResponseRedirect('thank-you')
    else:
        form = MyRegistrationForm()
        strip= Reseller_token.objects.filter(userID_id=request.user.id)

        logger.debug('stripe= {0}'.format(strip))
        
        return render(request, 'myprofile.html', {'form': form, 'stripe':strip})#, 'user':users



def loginsocial(request):
     logger.info('We are in Social Login request={0}'.format(request))
     context = RequestContext(request,
                           {'request': request,
                            'user': request.user})
     return render_to_response('loggedin2.html',
                             context_instance=context)
      
def stripe_auth(request):
    #Here we let reselers set up and connect their stripe accoounts 
    #so they can charge end users
    params = {'response_type': 'code','scope':'read_write'}
    url = stripe_connect_service.get_authorize_url(**params)
    return HttpResponseRedirect(url)

@csrf_exempt
def myvideos(request):
    #Page which retrieves all videos purchased by a user
    try:
        my_vids=Document.objects.filter(users=request.user.id).order_by('-id')#request.user.id
    except: 
        return render_to_response(
        'myvideos.html',
        context_instance=RequestContext(request)
        )
    
    return render_to_response(
        'myvideos.html',
        {'my_vids': my_vids},
        context_instance=RequestContext(request)
        )

@csrf_exempt
def stripe_pay(request):
    #Payment processing by stripe or by sharing    
    documents={}                  #request.user.id
    status=''
    args={}
    if request.method == 'POST':
        seller_name =request.POST['seller']    
        reseller_user =User.objects.get(username=seller_name)
            
        #If user is paying by stripe     
        if  request.POST['stripeToken']!='share':
            token=request.POST['stripeToken']
            documents = Document.objects.filter(usersname=request.user.username)
            try:
                reseller= Reseller_token.objects.get(userID_id=reseller_user.id)
            except Exception as e:
                #if it goes wrong more
                 than likkely the reseller has not connected their
                #stripe account yet.
                #TODO: make exception on exact error
                msg=  'This reseller is not set up for payments currently ...{0}'.format(e)
                logger.debug(msg)
                doc_id=request.POST['doc_id']   #id of the video
                docid=str(doc_id)       
                obj_doc=Document.objects.get(id=doc_id)   #This gets the full record of the video from the database inro obj_doc
                
                #We need to let the reseller know that someone wants to give them 
                #money for their video so send them an email to sort it out!
                args["subject"]="ATTENTION: {0}, A user is trying to pay you for your video".format(seller_name)
                args["message"]="""
                Hi {0},
                A user on Shabingo.com just tried to purchase your video {1}.
                But you have not connected your Stripe account with Shabingo yet.
                So we unfortunately were unable to take payment for you.
                To avoid this happening again plesae click on the following link
                https://shabingo.com/accounts/loggedin2/
                and click the button that says 'Connect with Stripe'.
                Then just follow the simple steps in setting up a stripe payments 
                account and connect it to Shabingo.
                 
                Don't forget to keep sharing and promoting your videos.
                Best regards,
                The Shabingo team.
                """.format(seller_name,obj_doc.name)
                args["username"]=seller_name 
                args["email"]=reseller_user.email
                args["recipients"]="info@shabingo.com"         
                send_email(args)
                return HttpResponse(msg)
            
            #Reseller has set up their Stripe account and are about to get paid :):) Whoopee!
            stripe_acc_id  = reseller.stripe_user_id
            app_price =int(request.POST['price'])
            app_price=app_price*100

            #appp_fee variable below is the commmission that goes to Shabingo.
            #Currently set to 0 :(
            app_fee= 0#(app_price/100)*23 
            str_fee=str(app_fee)
            
            charge = stripe.Charge.create(
              amount=request.POST['price']+'00', # amount in cents goint to reseller
              #amount='100', # testing purposes :)               
              currency="eur",
              source=request.POST['stripeToken'],
              application_fee=app_fee, # amount in cents going to Shabingo        
              stripe_account=stripe_acc_id
            )
    
            status=charge["status"]
     
       
        doc_id=request.POST['doc_id']   #id of the video
        docid=str(doc_id)                          
        
        obj_doc=Document.objects.get(id=doc_id)   #This gets the full record of the video from the database inro obj_doc
        my_user = User.objects.get(id=request.user.id) #This gets the current user(video buyer)
        obj_doc.users.add(my_user) #Here we add the video buyer to the videos list of users
        obj_doc.save()  # And save it
        
        #If all good send an email to the reseller telling them the good news  
        if 	status== "succeeded" or request.POST['stripeToken']=='share':
            
            my_vids=Document.objects.filter(users=request.user.id)#request.user.id
            
            if status== "succeeded":
                args["subject"]="Youve made a sale"
                args["message"]="""
                Congratulations {0},
                A user has bought your video {1}.
                Sit tight and you should get paid between 3 and 7 days.
                Don't forget to keep sharing and promoting your videos.
                Best regards,
                The Shabingo team.
                """.format(reseller_user.first_name,obj_doc.name)

                #If reseller has enabled pay by sharing let the reseller know too
            else:
                args["subject"]="Your video has been shared"
                args["message"]="""
                Congratulations {0},
                A user has shared your video {1}.
                Don't forget to keep sharing and promoting your videos.
                Best regards,
                The Shabingo team.
                """.format(reseller_user.first_name,obj_doc.name)
            
            
            args["username"]=reseller_user.first_name  
            args["email"]=reseller_user.email
            args["recipients"]="info@shabingo.com"         
            send_email(args)
            return HttpResponse("Success")
        
        else: 
            return HttpResponse("Transaction Failed")        
                 
    else:         
        return HttpResponse("no post")

def stripe_callback(request):

    #After reseller connects their stripe account they get redirected
    #to this endpoint from Stripe and Stripe provides us with all 
    #their accout details that we save
    code = request.GET['code'] 
    stripe_cust = Reseller_token()
    stripe_cust.token=code          
    stripe_cust.stripe_email = request.user.email
    stripe_cust.userID = request.user
    logger.info('this is from stripe callback {0}'.format(request))
    data = {
        'grant_type': 'authorization_code',
        'code': code
    }
    resp = stripe_connect_service.get_raw_access_token(method='POST', data=data)
    stripe_payload = json.loads(resp.text)
    
    stripe_cust.access_token=stripe_payload["access_token"]
    stripe_cust.livemode=stripe_payload["livemode"]
    stripe_cust.token_type=stripe_payload["token_type"]
    stripe_cust.stripe_publishable_key=stripe_payload["stripe_publishable_key"]
    stripe_cust.stripe_user_id=stripe_payload["stripe_user_id"]
    stripe_cust.scope=stripe_payload["scope"]
    stripe_cust.refresh_token=stripe_payload["refresh_token"]
    
    
    stripe_cust.save()
    
    return render_to_response('loggedin2.html', locals(), context_instance=RequestContext(request)) 


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('main.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
def login(request, document_id):
    c = { }
    c.update(csrf(request))
    #logger.info('We are in Login request={0}'.format(request))
    
    if document_id>1:
        request.session['login_video'] = document_id
        logger.info('document_id = {0}'.format(document_id))
        
    return render_to_response('login.html', c)

def auth_view(request):
    #If a non registered user clicks on a video to view it they 
    #wil be prompted to log in. So we need to track the value of 
    #the session varable 'login_video' which was set when they  
    #signed up or logged in so we know what video 
    #to redirect them back to after the log in or registration process
    #so it all works seamlessly

    username= request.POST.get('username','')
    email= request.POST.get('email','')
    password= request.POST.get('password','')
    user = auth.authenticate(username=username, email=email, password=password)
    if user is not None:
        auth.login(request, user)
        if 'login_video' in request.session:
            doc_id = request.session['login_video']
            logger.info('document.id = {0}'.format(doc_id))
            video(request, doc_id)
            return redirect('main.views.video', document_id=doc_id)
        else:    
            return render_to_response('loggedin.html',
                              {'full_name':request.user.username})        
       ## return HttpResponseRedirect('accounts/loggedin')
    else:
        return render_to_response('invalid.html')
        ##return HttpResponseRedirect('accounts/invalid')
        
def auth_view_upload(request):

    username= request.POST.get('username','')
    email= request.POST.get('email','')
    password= request.POST.get('password','')
    user = auth.authenticate(username=username, email=email, password=password)
    logger.info('We are in auth_view_upload request={0}'.format(request))
    if user is not None:
        auth.login(request, user)
        return render_to_response('upload.html',
                              {'full_name':request.user.username})        
       ## return HttpResponseRedirect('accounts/loggedin')
    else:
        return render_to_response('invalid.html')
        ##return HttpResponseRedirect('accounts/invalid')
    
def loggedin(request):
    return render_to_response('loggedin.html',
                              {'full_name':request.user.username})

def invalid_login(request):
    return render_to_response('invalid.html')

def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')


   
def home(request):
    mylogfunction()
    logger.debug("this is a debug message from home!")
    if request.method =='POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username= request.POST.get('username','')
            email= request.POST.get('email','')
            subject = 'Hi {0} Welcome to Shabingo'.format(username)
            msg="Hi {0},".format(username)

            #Email text stored in the settings.py file
            msg=msg+settings.WELCOME_EMAIL
            message = msg
        
            recipients = ['info@shabingo.com']
            if email:
                recipients.append(email)            
           
            send_mail(subject, message, 'info@shabingo.com', recipients)
            
            
            #send_mail(subject, message, sender, recipients)
            messages.success(request, 'Thank you for joining!')
            return HttpResponseRedirect('thank-you')

    else:
        form = MyRegistrationForm()
        return render(request, 'signup.html', {'form': form})

    return render(request, 'signup.html', {'form': form})
   
def signup2(request):

    ##Test home page 
    if request.method == 'POST':
        form = UploadRawForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = UploadRaw(file = request.FILES['file'])
            new_file.save()
            return HttpResponseRedirect(reverse('main:home'))
    else:
        form = UploadRawForm()
 
    data = {'form': form}
    return render_to_response('signup2.html', data, context_instance=RequestContext(request))

 
def reg(request):
    
    if request.method =='POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username= request.POST.get('username','')
            email= request.POST.get('email','')
            subject = 'Hi {0} Welcome to Shabingo'.format(username)
            msg="Hi {0},".format(username)
            msg=msg+settings.WELCOME_EMAIL
            message = msg
           
            recipients = ['info@shabingo.com']
            if email:
                recipients.append(email)            
           
            send_mail(subject, message, 'info@shabingo.com', recipients)
         
            return HttpResponseRedirect('thank-you')

    else:
        form = MyRegistrationForm()

    return render(request, 'reg.html', {'form': form})
    


def sellvidsblog(request):
        
    return render_to_response('the-best-place-to-sell-your-video-content-online.html', locals(), context_instance=RequestContext(request))
    
def thankyou(request):
        
    return render_to_response('thankyou.html', locals(), context_instance=RequestContext(request))
    
def loggedin2(request):
    
    return render_to_response('loggedin2.html', locals(), context_instance=RequestContext(request)) 

def sitemap(request):
    
    return render_to_response('sitemap.xml', locals(), context_instance=RequestContext(request)) 

def terms(request):
    
    return render_to_response('terms.html', locals(), context_instance=RequestContext(request))           
     
def aboutus(request):
     return render_to_response('aboutus.html', locals(), context_instance=RequestContext(request))
    

def contactus(request):
     return render_to_response('contactus.html', locals(), context_instance=RequestContext(request))
    
def purevideos(request):
     return render_to_response('purevideos.html', locals(), context_instance=RequestContext(request))
 
def privacypolicy(request):
     return render_to_response('privacypolicy.html', locals(), context_instance=RequestContext(request))   

def goto(request):
     return render_to_response('B85D99C1DB94F102E95052D2438CB4CC.txt', locals(), context_instance=RequestContext(request))


def isNotBadError(errors):
    for err in errors:
        if not err=='This field is required.':
            
            return False
    return True


def delete_record(request, document_id):

    #If a user wants to delete a video
    if request.user.id >0 :
        newdoc = Document.objects.get(id=document_id)
        newdoc.delete()
    return HttpResponseRedirect(reverse('main.views.upload'))


def edit_preview(request, document_id):
        ##This is where a user can go in and edit all the details 
        ##of and existing video that they have uploaded
        ##This is all a bit verbose but at least its clear whats going on
    
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            form.fields['docfile'].required = False
            form.fields['docfile1'].required = False
            form.fields['docfile2'].required = False
            form.fields['category'].required = False
            form.fields['document_type'].required = False
            form.fields['price'].required = False
            form.fields['description'].required = False
            form.fields['name'].required = False

            if form.is_valid():
                
                #Get the particular video uploaded record from the database
                newdoc = Document.objects.get(id=document_id)
                newdoc.usersname = request.user.username                
                
                #Certain fields may or may not have changed
                #If they are present then they will be updated 
                #otherwise they wont

                if request.FILES.get('docfile'):
                    myfile=request.FILES.get('docfile')
                else:
                    myfile=None
                
                if request.FILES.get('docfile1'):
                    myfile1=request.FILES.get('docfile1')
                else:
                    myfile1=None
                
                if request.FILES.get('docfile2'):
                    myfile2=request.FILES.get('docfile2')
                else:
                    myfile2=None
                
                if myfile:
                   newdoc.docfile = myfile
                if myfile1:
                   newdoc.docfile1 = myfile1
                if myfile2:
                   newdoc.docfile2 = myfile2
                   
                              
                newdoc.price=request.POST.get('price','')
                newdoc.category= request.POST.get('category','')
                if request.POST.get('document_type',''):
                    newdoc.document_type=1
                newdoc.isover18s =request.POST.get('isover18s','')
                newdoc.name =request.POST.get('name','')
                newdoc.description =request.POST.get('description','')
                
                #Clean the fields and save the record
                form.clean_content()
                if myfile:
                    newdoc.save(update_fields=['docfile'])
                if myfile1:   
                    newdoc.save(update_fields=['docfile1'])
                if myfile2: 
                    newdoc.save(update_fields=['docfile2'])
                if request.POST.get('price'):
                    newdoc.save(update_fields=['price'])
                if request.POST.get('category'):
                    newdoc.save(update_fields=['category'])
                if request.POST.get('document_type'):
                    newdoc.save(update_fields=['document_type'])
                if request.POST.get('isover18s'):
                    newdoc.save(update_fields=['isover18s'])
                if request.POST.get('name'):
                    newdoc.save(update_fields=['name'])
                
                if request.POST.get('description'):   
                    newdoc.save(update_fields=['description'])
                    
                p =request.POST.get('docfile')
                
                messages.error(request, 'docfile  is: %s ' %p)
                
                
                
                
                messages.error(request, 'Form Errors: %s' %form.errors)
                
           
        document = Document.objects.get(id=document_id)

        form = DocumentForm() 
        
        #Return the updated record to be rendered on the front end
        return render_to_response(
            'edit_preview.html',
            {'document': document, 'form': form},
            context_instance=RequestContext(request)
        )
       
def upload(request):
    # Handle Video upload

    # A lot going on here especially shell commands
    # 3 files get uploaded with various meta info fields
    # Using FFMPEG 2 videos are converted to mp4 regardless of 
    # what they are when uploaded first. Then they get renamed, 
    # saved and the original ones are deleted
    # A poster image for the first frame is also uploaded and 
    # resized using image Magick.
    # Function execute_shell is used a lot sending lots of commands through
    # pythons subprocess synchronously
    # May redo this so it is done asynchronously but afraid people will think
    # Nothing happened and not come back. 
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
                                  
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'], docfile1 = request.FILES['docfile1'],  docfile2 = request.FILES['docfile2'])
            upload_file=request.FILES['docfile']
            upload_file1=request.FILES['docfile1']
            upload_file2=request.FILES['docfile2']
           
            #logger.debug('*************************************New Filename is {0}************************************'.format(newdoc.docfile.name))
            newdoc.usersname = request.user.username
            newdoc.price=request.POST.get('price','')
            newdoc.category= request.POST.get('category','')
            newdoc.isover18s =request.POST.get('isover18s','')
            newdoc.name =request.POST.get('name','')
            newdoc.description =request.POST.get('description','')
            bla=request.POST.get('document_type','')
            logger.debug('bla bla bla ={0}'.format(bla))
            if bla=='on':
                newdoc.document_type =1
            else:
                newdoc.document_type =0
            #Temporarily commented out. lots of error handling on front end
            #form.clean_content()
            newdoc.save()
            logger.debug('File name = {0}'.format(newdoc.name))
            
            new_file=get_new_file(newdoc.docfile.name)            
          
            new_file1=get_new_file(newdoc.docfile1.name)

            #New folders and need to be created
            today_folder =datetime.date.today().strftime("%Y/%m/%d")

            
            str_= str(newdoc.docfile2.name)
            str_file2="_thumb_" +str_.split('/')[-1]
            #create destination of converted files
            prefix='/home/donagh/webapps/shabingo_static/media/'
            output=os.path.join('MEDIA_ROOT','documents',today_folder,new_file)
            output1=os.path.join('MEDIA_ROOT','documents',today_folder,new_file1) 
            output2=os.path.join('MEDIA_ROOT','documents',today_folder,str_file2)
            
            output_file=prefix+output
            output_file1=prefix+output1
            output_file2=prefix+output2
            
            str_file=str(newdoc.docfile.name)
            str_file=prefix+str_file
            str_file1=str(newdoc.docfile1.name)
            str_file1=prefix+str_file1
            str_file2=str(newdoc.docfile2.name)
            str_file2=prefix+str_file2
            
            #The magic of FFMPEG ...  Convert  video to mp4      
            shell_cmd='ffmpeg -i '+str_file+' -vcodec libx264 -acodec libfaac '+ output_file
            #logger.debug('shell_cmd ...{0}'.format(shell_cmd))
            file_details=''
            
            try:
                file_details=execute_shell(shell_cmd)
                newdoc.rename_shab(output)
            except Exception as e:
                logger.debug('Failed to execute shell command ...{0}'.format(e))
            
            #The magic of FFMPEG ...  Convert  video to mp4   
            shell_cmd1='ffmpeg -i '+str_file1+' -vcodec libx264 -acodec libfaac '+ output_file1
          
            file_details=''
            
            
            try:
                file_details=execute_shell(shell_cmd1)
                newdoc.rename_prev(output1)
            except Exception as e:
                logger.debug('Failed to execute shell command ...{0}'.format(e))            
            
            #Resize Poster image uploadeed to keep it all perfect size and limit disk space
            shell_cmd2 ="""convert %s -resize 300x200\! %s
            """%(str_file2,str_file2)
            #logger.debug(' THUM NAIL CONVERSION COMMAND === {0}'.format(shell_cmd2))
            
            try:
                file_details=execute_shell(shell_cmd2)
                #newdoc.rename_thumb(output2)
            except Exception as e:
                logger.debug('Failed to execute shell command ImageMagick with this error...{0}'.format(e))            

            #Remove original uploaded files so we minimize disk storage
            shell_rm_file = "rm %s" %str_file
            shell_rm_file1 = "rm %s" %str_file1
            
            try:
                file_details=execute_shell(shell_rm_file)
                file_details=execute_shell(shell_rm_file1)

            except Exception as e:
                logger.debug('Problem remo ing originally uploaded files with this error: {0}'.format(e))            

            subject = 'ATTENTION: Shabingo Video Upload Approval required.'
            msg='User %s as uploaded video: %s plesae review at : %s and also %s and %s'%(newdoc.usersname,newdoc.name, newdoc.docfile.url, newdoc.docfile1.url, newdoc.docfile2.url)
            message = msg
            sender = ['info@shabingo.com']
            cc_myself = ['zaiga101@yahoo.com']
            recipients = ['donagh_1@yahoo.ie','zaiga101@yahoo.com','info@shabingo.com']
            #recipients.append(sender)
            send_mail(subject, message, 'info@shabingo.com', recipients)

            return HttpResponseRedirect(reverse('main.views.upload'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    #documents = Document.objects.all() # This is madness especially when the amount of videos uploaded grows
    documents = Document.objects.filter(usersname=request.user.username)
    # Render list page with the documents and the form
    return render_to_response(
        'upload.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
def get_new_file(old_file):
    str_file=str(old_file)
    strip_ext=str_file.split('.')      
    strip_ext[-1] = '.mp4'
    new_file=''.join(strip_ext)
    split_file=new_file.split('/')  
    strip_file=split_file[-1]
    strip_file='_out_'+strip_file

    return strip_file



def execute_shell(shell_command ):

    #very effective way of executing shell commands synchronously
    try:
        p = subprocess.Popen(shell_command, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.communicate()[0]
        return out
            
    except Exception as e:
        logger.debug('Error with shell cmd  {0}'.format(e))

        
def approve(request):
    documents = Document.objects.filter(approved=False)
    return render_to_response(
        'approve.html',
        {'documents': documents},
        context_instance=RequestContext(request)
    )    
def videos(request):
   
    documents = Document.objects.filter(published=True,isover18s=0).order_by('-id')
    
    return render_to_response(
        'videos.html',
        {'documents': documents},
        context_instance=RequestContext(request)
    )
def shabingoadult(request):
   
    #Not currently active;; :) Say no more    
    documents = Document.objects.filter(published=True,isover18s=1).order_by('-id')
    
    return render_to_response(
        'shabingoadult.html',
        {'documents': documents},
        context_instance=RequestContext(request)
    )
    
def charts(request):
    
    ##Pie([5,10]).title('Hello Pie').color('red','lime').label('hello', 'world')
    
    return render_to_response('charts.html', locals(), context_instance=RequestContext(request))


def item_list(request):
    
  
    return render_to_response('item_list.html', locals(), context_instance=RequestContext(request))
    

  
def process_form_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    
  #  logr.debug() Put logging data here when tou get the logging class set up
  
    send_mail(form_data[0]['subject'],
            form_data[2]['message'], form_data[1]['sender'],
            ['donagh_1@yahoo.ie'], fail_silently =False)
    
    return form_data
    

def contact(request):
        # Handle file upload
    if request.method =='POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            recipients = ['donaghc@gmail.com']

            if sender:
                recipients.append(sender)
            send_mail(subject, message, sender, recipients)
                 
                  
            messages.success(request, 'Thank you for contacting us. If required we will get back to you within 48 hours!')
            
            return render_to_response('done.html', locals(), context_instance=RequestContext(request))
    args={}
    args.update(csrf(request))
    args['form'] = ContactForm()
    
    return render_to_response('contact.html', args)


def done(request):
        
        return render_to_response('done.html', locals(), context_instance=RequestContext(request))
def upload2(request):
        # Handle file upload
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
                                  
        if form.is_valid():
            
            newdoc = Document(docfile = request.FILES['docfile'], docfile1 = request.FILES['docfile1'],  docfile2 = request.FILES['docfile2'])
            newdoc.usersname = request.user.username
            newdoc.price=request.POST.get('price','')
            newdoc.category= request.POST.get('category','')
            newdoc.isover18s =request.POST.get('isover18s','')
            newdoc.name =request.POST.get('name','')
            newdoc.description =request.POST.get('description','')
   
            
            form.clean_content()
            
               
            newdoc.save()

            return HttpResponseRedirect(reverse('main.views.upload'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'upload2.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )

@csrf_exempt
def show_me_the_money(sender, **kwargs):

    #This is where paypal redirects to after it recieves payment
    #Works perfectly. not currently implemented  but was and works good
    ipn_obj = sender
    
    logger.debug("this is a debug message from show_me_the_money 1st,!"+str(ipn_obj))
   
    payStatus=ipn_obj.POST.get('payment_status','')
    
    intUserid=0
    strUserId=''
    
    restOfStrInvoice=''
    if payStatus=='Completed':
        myDictInvoice = ipn_obj.POST.get('invoice','')
        logger.debug("this is a debug message Pay Pal Dict Invoice="+myDictInvoice)
        for index in range(0, len(myDictInvoice)):
            
            if myDictInvoice[index]=='|':
                intUserid =int(strUserId)
                restOfStrInvoice= myDictInvoice[len(strUserId)+1:]
                break
            strUserId +=myDictInvoice[index]
    
    intDocid =0
    strDocId=''
    
    for index in range(0, len(restOfStrInvoice)):
         
        if restOfStrInvoice[index]=='/':
           intDocid =int(strDocId)
           break
        strDocId +=restOfStrInvoice[index]
        
      
    obj_doc=Document.objects.get(id=intDocid)
    my_user = User.objects.get(id=intUserid)
    obj_doc.users.add(my_user)
    obj_doc.save()
    logger.debug("this is a debug message from show_me_the_money Saved,!"+str(my_user))
               
                 
    return HttpResponse("OKAY")


    

def video(request, document_id):

    #Returns requested preview to user
    document = Document.objects.get(id=document_id)
    
    return render_to_response(
            'video.html',
            {'document': document},
            context_instance=
            RequestContext(
            request))

def video2(request, document_id):


    document = Document.objects.get(id=document_id)


    return render_to_response(
            'video2.html',
            {'document': document},
            context_instance=
            RequestContext(
            request))

#class myvideo(RedirectView):
 #   permanent = False
    
  #  def get_redirect_url(self, **kwargs):
   #     s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                            #settings.AWS_SECRET_ACCESS_KEY,
                            #is_secure=True)
        # Create a URL valid for 60 seconds.
    #    return s3.generate_url(60, 'GET',
                            #bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            #key=kwargs['filepath'],
                            #force_http=True)

#    def get(self, request, *args, **kwargs):
 #       document = get_object_or_404(Document, pk=kwargs['pk'])
  #      u = request.user
#
 #       if u.is_authenticated():
  #          if document.docfile:
   #             filepath = settings.MEDIA_DIRECTORY + document.docfile
    #            url = self.get_redirect_url(filepath=filepath)
                # The below is taken straight from RedirectView.
     #           if url:
      #              if self.permanent:
       #                 return http.HttpResponsePermanentRedirect(url)
        #            else:
         #               return http.HttpResponseRedirect(url)
          #      else:
           #         logger.warning('Gone: %s', self.request.path,
            #                    extra={
             #                       'status_code': 410,
              #                      'request': self.request
               #                 })
                #    return http.HttpResponseGone()
                
 #           else:
  #              raise http.Http404
   #     else:
    #        raise http.Http404
        
    

def myvideo(request, document_id):
    
    #This is what pulls down all your purchased videos into your private area
    if request.user.id:
        document = Document.objects.get(id=document_id)
    else:
        document=none
    return render_to_response(
            'myvideo.html',
            {'document': document},
            context_instance=RequestContext(request))
    
def send_email(args):
            
            #Simple email function
            username= args.get('username','')                
            email= args.get('email','')
            subject = args.get('subject','')
            message = args.get('message','')
            recipients = ['info@shabingo.com']
            if email:
                recipients.append(email)            
           
            send_mail(subject, message, 'info@shabingo.com', recipients)