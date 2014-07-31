#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from galaxy_api import *
from common import *
import json
import time
import ndb_json

# Learn2Mine-Specific Imports
import getBadges
import lessonWriter, tutorialWriter, dmWriter, lessonMaker
import skillTree
import issueBadge

# Python imports
import os
import cgi
import urllib
import urllib2
import httplib2
import random
import ast
import string

# Appengine imports
import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import ndb
from apiclient.discovery import build
from apiclient.http import MediaInMemoryUpload

# OAUTH imports
import httplib2
import logging
import pickle
from apiclient.discovery import build
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from oauth2client.appengine import CredentialsProperty
from oauth2client.appengine import StorageByKeyName
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

#Here we are using os to get the path to our templates directory
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])



DEFAULT_LESSONPLAN_NAME = 'default_lessonplan'
DEFAULT_AUTHOR = 'user@example.com'


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

http = httplib2.Http(memcache)
service = build("drive", "v2", http=http) #Google-provided code -> not sure what it does


# Set up an OAuth2Decorator object to be used for authentication.  Add one or
# more of the following scopes in the scopes parameter below. PLEASE ONLY ADD
# THE SCOPES YOU NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
decorator = oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=[
      #'https://www.googleapis.com/auth/drive',
      #'https://www.googleapis.com/auth/drive.apps.readonly',
      'https://www.googleapis.com/auth/drive.metadata.readonly',
      #'https://www.googleapis.com/auth/drive.file',
      #'https://www.googleapis.com/auth/drive.scripts',
      #'https://www.googleapis.com/auth/drive.readonly',
    ],
    message='MISSING_CLIENT_SECRETS_MESSAGE')
    
class OAuthHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        useremail = users.get_current_user().email()
        users.get_current_user()
        user_query = db.Query(User)
        user_query.filter('EMAIL =', useremail)
        if user_query.get() != None:
            self.redirect('/Home')
        else: # We need to establish them in the datastore with lessons etc.
	    #Create a random key for the user, make sure it is unique
	    unique = False
	    while(not unique):
		    randkey = str(random.randint(100000000000000000000,999999999999999999999))
		    unique = True
		    userIterable = db.Query(User).run(batch_size=10000)
		    for user in userIterable:
		    	if randkey == user.SESSION:
				unique = False

	    #Create the initial standings for the user's lessons	    
            new_user = User(EMAIL = useremail,
				UPLOADING = 'stillneedswork',
                                PATTERN = "stillneedswork",
                                CLUSTERING = "stillneedswork",
                                KNN = "stillneedswork", 
                                KMEANS = "stillneedswork",
                                HC = "stillneedswork",
                                CLASSIFICATION = "stillneedswork",
                                NAIVEBAYES = "stillneedswork",
                                SVM = "stillneedswork",
                                NN = "stillneedswork",
                                DTREE = "stillneedswork",
                                REGRESSION = "stillneedswork",
                                OTHER = "stillneedswork",
                                SCALEFILTER = "stillneedswork",
                                MARKETBASKET = "stillneedswork",
                                PCA = "stillneedswork",
				CASE = "stillneedswork",
				CASE1 = "stillneedswork",
				CASE2 = "stillneedswork",
				CASE3 = "stillneedswork",
				SESSION = randkey,
				BADGESDUE = [""],
				BADGESEARNED = [""],
				SKILLSEARNED = [""]
                )
            new_user.put()
            self.redirect('/Home')
        
        
class CredentialsModel(db.Model):
    credentials = CredentialsProperty()
# END OAUTH CODE


## Database entity definitions
class User(db.Model):
    EMAIL = db.StringProperty()
    PATTERN = db.StringProperty()
    CLUSTERING = db.StringProperty()
    UPLOADING = db.StringProperty()
    KNN = db.StringProperty()
    KMEANS = db.StringProperty()
    HC = db.StringProperty()
    CLASSIFICATION = db.StringProperty()
    NAIVEBAYES = db.StringProperty()
    SVM = db.StringProperty()
    NN = db.StringProperty()
    DTREE = db.StringProperty()
    REGRESSION = db.StringProperty()
    OTHER = db.StringProperty()
    SCALEFILTER = db.StringProperty()
    MARKETBASKET = db.StringProperty()
    PCA = db.StringProperty()
    CASE = db.StringProperty()
    CASE1 = db.StringProperty()
    CASE2 = db.StringProperty()
    CASE3 = db.StringProperty()
    SESSION = db.StringProperty()
    BADGESDUE = db.StringListProperty()
    BADGESEARNED = db.StringListProperty()
    SKILLSEARNED = db.StringListProperty()
 #   lessons = db.ListProperty(db.Key) ##found on https://developers.google.com/appengine/articles/modeling
                                        #Rendered unnecessary with the Relationship Model
class Lesson(db.Model):                #possibly useless, we'll see
    NAME = db.StringProperty()
    DESCRIPTION = db.StringProperty()
    
class Leaderboard(db.Model):
    TYPE = db.StringProperty()
    TOP10 = db.StringListProperty()

""" This is what we used to create the Leaderboard instances. These must be entered once into the Interactive Console

knnLeader = Leaderboard(TYPE = "knn", TOP10 = ["user1:0","user2:0","user3:0","user4:0","user5:0","user6:0","user7:0","user8:0","user9:0","user10:0"]
                )


kmeansLeader = Leaderboard(TYPE = "kmeans", TOP10 = ["user1:0","user2:0","user3:0","user4:0","user5:0","user6:0","user7:0","user8:0","user9:0","user10:0"]
                )

nnLeader = Leaderboard(TYPE = "nn", TOP10 = ["user1:0","user2:0","user3:0","user4:0","user5:0","user6:0","user7:0","user8:0","user9:0","user10:0"]
                )

knnLeader.put()
kmeansLeader.put()
nnLeader.put()
"""

class UserLesson(db.Model):
    user = db.ReferenceProperty(User,
                                   required=True,
                                   collection_name='users')
    lesson = db.ReferenceProperty(Lesson,
                                   required=True,
                                   collection_name='lessons')
    status = db.StringProperty()

class newKeyHandler(webapp2.RequestHandler):
	def get(self):
		email = users.get_current_user().email()
		user = db.Query(User).filter("EMAIL =", email).get()
		unique = False
		while(not unique):
			randkey = str(random.randint(100000000000000000000,999999999999999999999))
			unique = True
			userIterable = db.Query(User).run(batch_size=10000)
			for person in userIterable:
			    	if randkey == person.SESSION:
					unique = False
					break		
		user.SESSION = randkey
		user.put()
		self.redirect('/Lessons?lesson=logins')

        
class HomeHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('Home.html')
	useremail = users.get_current_user().email()
	## This block of code checks if the user exists in the datastore, if not, they are redirected to "/", which creates them
	## This code is used in all of the Handlers
	try:
		db.Query(User).filter("EMAIL =", useremail).get().SESSION
		exists = True
	except:
		exists = False 
	if not exists:
		self.redirect("/")
	#Attempt to display user's 'Learn2mine' backpack group, calling our getBadges function
	#The try/except fixes a problem where on first login, users would not be ready in the datastore before
 	#		reaching here
 	#try:
 	#	userBadges = db.Query(User).filter("EMAIL =", useremail).get().BADGESEARNED
 	#	templates_values, writeText = issueBadge(userBadges)
 	#except:
	# 	template_values = {'user':useremail,'badgeDisplay':'Error retrieving badges'}
	# 	print("in the outer except")
 	
	try:
		userBadges = db.Query(User).filter("EMAIL =", useremail).get().BADGESEARNED
		if len(userBadges) > 1:
			badgeDisplay = ''
			for i in range(len(userBadges)-1):
				badgeDisplay = badgeDisplay + "<img width='100px' height='100px' src='images/"+userBadges[i+1]+".png'></img>"
		else:
			badgeDisplay='You have not yet earned any Badges!'

		template_values = {'user':useremail,'badgeDisplay':badgeDisplay}
		#Get the currently logged in user's info
		user_query = db.Query(User)
		user = user_query.filter('EMAIL =', useremail).get()

		#Check if the user is due any badges, if so, issue it with the Openbadges.issue() function
		self.response.write('<script src="https://beta.openbadges.org/issuer.js"></script>')
		user.BADGESDUE = list(set(user.BADGESDUE))
		if len(user.BADGESDUE) > 1:
			self.response.write('<script>window.onload = function(){OpenBadges.issue(["http://portal.cs.cofc.edu/learn2mine/static/badges/'+useremail.split("@")[0]+user.BADGESDUE[1]+'.json"], function(errors, successes) {console.log(errors.reason);window.location = "http://learn2mine.appspot.com/Home"});}</script>')
			if(user.BADGESDUE[1] not in user.BADGESEARNED):
				user.BADGESEARNED.append(user.BADGESDUE.pop(1))
			else:
				user.BADGESDUE.pop(1)
			user.put()
	except:
		badgeDisplay = 'You have not yet earned any badges!'
		template_values = {'user':useremail,'badgeDisplay':badgeDisplay}
	#self.response.write(writeText)
	self.response.write(template.render(template_values))


	# Code to retroactively give users the root badge
	#if "datascienceMastery" not in user.BADGESEARNED:
	#	user.BADGESDUE.append("datascienceMastery")
	#	user.put()

	#If the user requested a new key, generate a new random integer, and make sure it is unique.

class LessonsHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('Lessons.html')        

	#Get current user, to display requested user information
	useremail = users.get_current_user().email()
	try:
		db.Query(User).filter("EMAIL =", useremail).get().SESSION
		exists = True
	except:
		exists = False 
	if not exists:
		self.redirect("/")
	session = db.Query(User).filter('EMAIL =', useremail).get().SESSION
	rstudioUser = useremail.split('@')[0]
	template_values = {'session': session, 'rstudioUser': rstudioUser, 'user':useremail}

	#The lesson's text is created dynamically from Lessonwriter.py, based on the request to the page.
        lesson = self.request.get("lesson")
	lessonHTML = lessonWriter.makePage(lesson, session, rstudioUser)
	if lessonHTML != None:
		self.response.write(lessonHTML)
	else:
		self.response.write('<div class="lesson"><div class="lessontext"><h1>Lessons</h1><p>Welcome to the Lessons page! Here is where you can learn about the various data mining techniques we have to offer you, and try your hand at performing some of the tasks common to dataset analysis. If it\'s your first time here, we recommend looking at the "Getting Started", "Using Galaxy" and "Using RStudio" pages (accessible from the list on the right) to familiarize yourself with the tools we use to help you learn. In order to unlock the lessons you have to complete our tutorial located in the \"Using Galaxy\" section.<br/><br/> Once you\'ve done that, take a look at your profile to see what lessons are available for you to learn and practice! Good Luck!</p></div></div>')
		#write the main lessons page
	self.response.write(template.render(template_values))

class GalaxyToLearn2MineHandler(webapp2.RequestHandler):
    def post(self):
	email = self.request.get("email")
	result = self.request.get("return") # correct or incorrect
        user_query = db.Query(User).filter("EMAIL =", email)
	user = user_query.get()
        badgeName = self.request.get("badgeName")
	if result == "correct" and (badgeName+"Mastery") not in user.BADGESDUE and (badgeName+"Mastery") not in user.BADGESEARNED:
		user.BADGESDUE.append(badgeName + 'Mastery')

	user.put() # Puts the user, considering all alterations


class ProfileHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
		useremail = users.get_current_user().email()
		template = JINJA_ENVIRONMENT.get_template('Profile.html')
		profile = skillTree.makeTemplateValues(useremail)
		profile.update({'user':useremail})
		#profile.update({'basicRLink':'/Lessons?lesson=standardR'})
		tutorial = self.request.get("tutorial")
		if tutorial == "True":
			#profile.update({'basicRLink':'/Lessons?lesson=standardR&tutorial=True'})
			self.response.write(template.render(profile))
			self.response.write('<script type="text/javascript" SRC="./Javascript/javascriptForProfile/profileTutorial.js"></script>')
		else:
			self.response.write(template.render(profile))		


## About and Help Handlers need only display the page, nothing fancy.
class AboutHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
	useremail = users.get_current_user().email()
	try:
		db.Query(User).filter("EMAIL =", useremail).get().SESSION
		exists = True
	except:
		exists = False 
	if not exists:
		self.redirect("/")        
	template_values = {'user': useremail} # Need it to render username on page
        template = JINJA_ENVIRONMENT.get_template('About.html')
        self.response.write(template.render(template_values))

class HelpHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
	useremail = users.get_current_user().email()
	try:
		db.Query(User).filter("EMAIL =", useremail).get().SESSION
		exists = True
	except:
		exists = False 
	if not exists:
		self.redirect("/")
        template = JINJA_ENVIRONMENT.get_template('Help.html')
        template_values = {'user': useremail}
        self.response.write(template.render(template_values))

class SearchHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
	useremail = users.get_current_user().email()
	try:
		db.Query(User).filter("EMAIL =", useremail).get().SESSION
		exists = True
	except:
		exists = False 
	if not exists:
		self.redirect("/")
	searchUser = self.request.get("searchUser")
	searchedUser = '' # Initialize in case they do not type in an actual user
	if(searchUser != ''):
		userLookup = db.Query(User).filter("EMAIL =", searchUser).get()
		badgeDisplay = '' # Empty in case a user does not exist; prevents server error since we post it
		if userLookup != None:
			userBadges = userLookup.BADGESEARNED
			if len(userBadges) > 1:
				for i in range(len(userBadges)-1): # Due to each stringlist property in the db starting with a blank [0] element
					badgeDisplay = badgeDisplay + "<img width='100px' height='100px' src='images/"+userBadges[i+1]+".png'></img>"
			else:
				badgeDisplay='This user has not yet earned any Badges!'
			searchedUser = searchUser.split('@')[0] + '\'s Badges'
			searchedProfile = skillTree.makeTemplateValues(searchedUser)#'dataminer',searchUser)
			self.response.write(searchedProfile) # Creates the Tree
			
		else:
			self.response.write('<p>Sorry! We could not find the user you are looking for. Did you enter their <b>full</b> email address correctly?</p>')	

	else:
		searchedUser='Search' # For first page visit
		badgeDisplay=''       # For first page visit
	template_values = {'user': useremail, 'badgeDisplay':badgeDisplay, "searchedUser":searchedUser}
	template = JINJA_ENVIRONMENT.get_template('Search.html')
        self.response.write(template.render(template_values))

class LeaderboardHandler(webapp2.RequestHandler):
    def get(self):
	useremail = users.get_current_user().email()
	try:
		db.Query(User).filter("EMAIL =", useremail).get().SESSION
		exists = True
	except:
		exists = False 
	if not exists:
		self.redirect("/")
        template = JINJA_ENVIRONMENT.get_template('Leaderboard.html')
        template_values = {		#Titles of the leaderboards
	'user': useremail,
	'knn': 'K-Nearest Neighbor',
	'kmeans': 'K-Means Clustering',
	'nn': 'Neural Network'
	}
	#image_values = {		NOT USED, but might be nice, the Leaderboard page is pretty plain
	#'knn': 'knnTitle.png',
	#'kmeans': 'kmeansTitle.png',
	#'nn': 'nnTitle.png'
	#}
	
	#Get the leaderboard based on the page request and retrive the info from the datastore
	lesson = self.request.get("type")
	leaderboard = db.Query(Leaderboard).filter("TYPE =", lesson).get()
        self.response.write(template.render(template_values))

	#make the leaderboard in the HTML
	self.response.write('<div id="pageslide" style="left: auto; display: block; right: 0px;"><div id="modal"><h2>Leaderboards</h2></div>')

	pageslideKeys = ['knn','kmeans','nn']
	#for key in template_values:
	#	if key != 'user':
	#		self.response.write('<a id="leaderlink" href="?type='+key+'"><div class="lessonlink" id ='+key+'></div></a><br />')
	for key in pageslideKeys:
		self.response.write('<a id="leaderlink" href="?type='+key+'"><div class="lessonlink" id ='+key+'></div></a><br />')	
		
	self.response.write('</div>')
	if lesson != "":
		self.response.write('<div id="leaderboard">')
		self.response.write('<table id="leaderboard" border="1" width="500" bgcolor="#FFFFFF"><h1 style="padding-left:90px">'+template_values[lesson]+'</h1><tr><th>User</th><th>Score</th></tr>')
		for i in range(10):
			self.response.write('<tr><td>'+leaderboard.TOP10[i].split(':')[0]+'</td><td>'+leaderboard.TOP10[i].split(':')[1]+'</td></tr>')
		self.response.write('</table></div>')
	#If no request, generate general welcome to Leaderboard message
	else:
		self.response.write('<div class="container" id="PStext"><h2>Welcome to the Leaderboards!<h2><h3><br /> Here, you can see how your skills stack up against other Learn2Mine users.<br/> Click a lesson from the list on the right to view the top 10 scoring users for that lesson.</div>')
		self.response.write('</h3></div>')


class TutorialLessonHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
		useremail = users.get_current_user().email()
		template = JINJA_ENVIRONMENT.get_template('TutorialLesson.html')
		page = self.request.get("page")
		if(page=="knn"):
			self.redirect("/Tutorial?page=knn")
		elif page == "tutorialProfile":
			self.redirect("/TutorialProfile")
		template_values = tutorialWriter.main(page)
		template_values.update({'user':useremail})
		self.response.write(template.render(template_values))

class DMLessonHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        useremail = users.get_current_user()
        template = JINJA_ENVIRONMENT.get_template('DMLesson.html')
        page = self.request.get("page")
        template_values = dmWriter.getLesson(page)
#        q = UsermadeLesson.query()
#        query = q.filter(UsermadeLesson.name == page).fetch(1)
#	if len(query) > 0:
#            template_values = { 'user':useremail, 'problems':query.problems,'paragraph':query.paragraph,'header':query.header,'reminder':query.reminder }
#        else:
#            template_values = {}
        self.response.write(template.render(template_values))

class TutorialProfileHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
		useremail = users.get_current_user().email()
		template = JINJA_ENVIRONMENT.get_template('TutorialProfile.html')
		wrong = self.request.get("wrong")
		if wrong == "True":
			wrongText = "You clicked the wrong link. Click the Profile link at the top to go to your skill tree"
		else:
			wrongText = ""
		template_values = {'user':useremail, 'wrong':wrongText}
		self.response.write(template.render(template_values))

class TutorialHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        useremail = users.get_current_user().email()
	template = JINJA_ENVIRONMENT.get_template('Tutorial.html')
	page = self.request.get("page")
	if page == "tutorialProfile":
		self.redirect("/TutorialProfile")
	if page == "knnLesson":
		self.redirect("/Lessons?lesson=knn1")
	if page == "tutorial1":
		self.redirect("/TutorialLesson?page=tutorial1")
		template_values = tutorialWriter.main(page)
		template_values.update({'user':useremail})
		self.response.write(template.render(template_values))
		#if wrong == "True":
		#	self.response.write("<p>You clicked the wrong link. Please reread and try again.</p>")

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('Welcome.html')
	self.response.write(template.render())

class GradingHandler(webapp2.RequestHandler):
	def post(self):
		code = self.request.get("code")
		email = self.request.get("email")
		hist_id = self.request.get("hist_id")
		workflow_id = self.request.get("workflow_id")
		user_query = db.Query(User)
		user_query.filter('EMAIL =', email)        
		user = user_query.get()
		# Now we make a galaxy api call
		# This call will grade the student's work
		# We should get an id back from the galaxy api call
		api_key = "16f0632a174c3615588f17f402b5e7c2"
		url = "http://localhost:8081/api/workflows/"

		hist_id = self.request.get("history")
		workflow_id = self.request.get("workflow_id")
		hist_id="0b05a232e89ad8e8"
		other=json.dumps({"email":email,"studentCode":code})
                print "\n\nOther:",other
#		results = workflow_execute_parameters(api_key,url,workflow_id,"hist_id="+hist_id,"param=gradeCode=other="+other)
		results = workflow_execute_parameters(api_key,url,workflow_id,"param=gradeCode=other="+other)

                print "\n\nResults",results
		outputid = results['outputs'][0]
		self.response.write(outputid)

	def get(self):
		outputid = self.request.get("outputid")
		hist_id = self.request.get("hist_id")
		hist_id="a7e42332dab8f5db"
		outputid="a21c530ff78f8d17"
                print "\n\n",outputid
                print "\n\n",hist_id
		url = "http://localhost:8081/api/histories/"+hist_id+"/contents/"+outputid+"/display"
		results = display_result("16f0632a174c3615588f17f402b5e7c2",url)
		self.response.write(json.dumps(results))

class GradeHandler(webapp2.RequestHandler):
	@decorator.oauth_required
	def get(self):
		useremail = users.get_current_user().email()
		template = JINJA_ENVIRONMENT.get_template('Grade.html')
		page = self.request.get("page")
		hist_id = "63cd3858d057a6d1"
		workflow_id = "ff5476bcf6c921fa"
		api_key = "3c7d82a64160fdc165ce6542e0f918d6"
		url = "http://portal.cs.cofc.edu/learn2mine/api/workflows/"
		results = workflow_execute_parameters(api_key,url,workflow_id,"hist_id="+hist_id,"param=return_grades=email="+useremail)
		outputid = results['outputs'][0]

		url = "http://portal.cs.cofc.edu/learn2mine/api/histories/"+hist_id+"/contents/"+outputid+"/display"
		maxNumTries = 10
		numTries = 0
		while numTries < maxNumTries:
			gradeHTML = get_raw(api_key,url)
			if 'img' in gradeHTML:
				break
			time.sleep(5)
			numTries += 1
				
		template_values = {'user':useremail, 'gradeHTML':gradeHTML}
		self.response.write(template.render(template_values))

class UsermadeLesson(ndb.Model):
    """Models an individual User Lesson entry with author, content, and date."""

    name = ndb.StringProperty(indexed=True)
    author = ndb.UserProperty(indexed=True)

    problems = ndb.TextProperty(repeated=True)
    languages = ndb.StringProperty(repeated=True)
    flag = ndb.StringProperty(indexed=True)
    urlKey = ndb.StringProperty(indexed=True)

    publicEdit = ndb.StringProperty()
    publicView = ndb.StringProperty()
    publicExecute = ndb.StringProperty()

    pythonInit = ndb.TextProperty(repeated=True)
    pythonInstruct = ndb.TextProperty(repeated=True)
    pythonFinal = ndb.TextProperty(repeated=True)
    rcodeInit = ndb.TextProperty(repeated=True)
    rcodeInstruct = ndb.TextProperty(repeated=True)
    rcodeFinal = ndb.TextProperty(repeated=True)

    header = ndb.TextProperty(indexed=False)
    paragraph = ndb.TextProperty(indexed=True)
    reminder = ndb.TextProperty(indexed=False)

class Learn2MineLesson(ndb.Model):
    """Models an individual L2M Lesson entry with author, content, and date."""

    name = ndb.StringProperty(indexed=True)
    author = ndb.UserProperty(indexed=True)

    problems = ndb.TextProperty(repeated=True)
    languages = ndb.StringProperty(repeated=True)

    pythonInit = ndb.TextProperty(repeated=True)
    pythonInstruct = ndb.TextProperty(repeated=True)
    pythonFinal = ndb.TextProperty(repeated=True)
    rcodeInit = ndb.TextProperty(repeated=True)
    rcodeInstruct = ndb.TextProperty(repeated=True)
    rcodeFinal = ndb.TextProperty(repeated=True)

    header = ndb.TextProperty(indexed=False)
    paragraph = ndb.TextProperty(indexed=True)
    reminder = ndb.TextProperty(indexed=False)

class LessonCreatorHandler(webapp2.RequestHandler):
    @decorator.oauth_required

    def post(self):
        lessonName = self.request.get("lesson2delete")
        thisUser = users.get_current_user()
        time.sleep(0.2)
        query = UsermadeLesson.query()
        userLessons = query.filter(UsermadeLesson.author == thisUser)
        thisLesson = userLessons.filter(UsermadeLesson.name == lessonName).fetch(1)[0]
        thisLesson.key.delete()
        self.redirect('/LessonCreator')

    def get(self):

        thisUser = users.get_current_user()
        if thisUser:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        time.sleep(0.2)
        query = UsermadeLesson.query()
        userLessons = query.filter(UsermadeLesson.author == thisUser).fetch(10)
        lessonArray = []
        for lesson in userLessons:
            lessonArray.append(lesson.name)

        template_values = { 'url': url, 'url_linktext': url_linktext, 'user': thisUser, 'existingLessons': lessonArray }

        template = JINJA_ENVIRONMENT.get_template('LessonCreator.html')
        self.response.write(template.render(template_values))

class LessonPreviewHandler(webapp2.RequestHandler):
    @decorator.oauth_required

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('LessonPreview.html')
        thisUser = users.get_current_user()
        lessonName = self.request.get("page")
        if lessonName != "":
            query = UsermadeLesson.query()
            userLessons = query.filter(UsermadeLesson.author == thisUser)
            userLessonQuery = userLessons.filter(UsermadeLesson.name == lessonName).fetch(1)
            if len(userLessonQuery) > 0:
                userLesson = userLessonQuery[0]
            else:
                template_values = {'user':thisUser,'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return

        elif self.request.get("public") != "":
            public = self.request.get("public")
            query = UsermadeLesson.query()
            userLessonQuery = query.filter(UsermadeLesson.urlKey == public).fetch(1)
            if len(userLessonQuery) > 0:
                foundLesson = userLessonQuery[0]
            else:
                template_values = {'user':thisUser,'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return
            if foundLesson.publicView == "True":
                userLesson = foundLesson
            else:
                if foundLesson.author == thisUser:
                    userLesson = foundLesson
                else:
                    template_values = {'user':thisUser,'errorCatch':"yes"}
                    self.response.write(template.render(template_values))
                    return

        if userLesson:
            template_values = {
                'user':thisUser, 'problems':userLesson.problems, 'languages': userLesson.languages, 'paragraph':userLesson.paragraph, 'header':userLesson.header, 'reminder':userLesson.reminder
            }

        else:
            template_values = {'user':thisUser,'errorCatch':"yes"}
        self.response.write(template.render(template_values))

class LessonModifyHandler(webapp2.RequestHandler):
    @decorator.oauth_required

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('LessonModify.html')
        thisUser = users.get_current_user()
        if self.request.get("page") != "":
            lessonName = self.request.get("page")
            counter = 0
            while counter < 100:
                query = UsermadeLesson.query()
                userLessons = query.filter(UsermadeLesson.author == thisUser)
                lessonplanQuery = userLessons.filter(UsermadeLesson.name == lessonName).fetch(1)
                if len(lessonplanQuery) > 0:
                    break
                counter += 1
            try:
                userLesson = lessonplanQuery[0]
            except IndexError:
                template_values = {'user':thisUser,'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return

        elif self.request.get("public") != "":
            public = self.request.get("public")
            query = UsermadeLesson.query()
            queryLesson = query.filter(UsermadeLesson.urlKey == public).fetch(1)
            if len(queryLesson) > 0:
                if queryLesson[0].publicEdit == "True":
                    userLesson = queryLesson[0]
                elif queryLesson[0].author == thisUser:
                    userLesson = queryLesson[0]
                else:
                    template_values = {'user':thisUser,'errorCatch':"yes"}
                    self.response.write(template.render(template_values))
                    return
            else:
                template_values = {'user':thisUser,'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return

        if len(userLesson.languages) == 1:
            if userLesson.languages[0] == "Python":
                template_values = { 'init_code': userLesson.pythonInit[:], 'final_code': userLesson.pythonFinal[:], 'instruct_code': userLesson.pythonInstruct[:] }
            else:
                template_values = { 'init_code': userLesson.rcodeInit[:], 'final_code': userLesson.rcodeFinal[:], 'instruct_code': userLesson.rcodeInstruct[:] }
        else:
            template_values = { 'Python_init_code': userLesson.pythonInit[:], 'Python_final_code': userLesson.pythonFinal[:], 'Python_instruct_code': userLesson.pythonInstruct[:], 'R_init_code': userLesson.rcodeInit[:], 'R_final_code': userLesson.rcodeFinal[:], 'R_instruct_code': userLesson.rcodeInstruct[:] }
        template_values.update({ 'problems': userLesson.problems, 'lessonName': userLesson.name, 'questionCount': len(userLesson.problems), 'fullLesson': userLesson.header, 'paragraph': userLesson.paragraph, 'user': thisUser, 'languages': userLesson.languages, 
'urlKey': userLesson.urlKey, 'publicModify': userLesson.publicEdit, 'publicViewing': userLesson.publicView, 'publicExecute': userLesson.publicExecute, 'author': userLesson.author })

        self.response.write(template.render(template_values))

    def post(self):
        lessonName = self.request.get("lessonName")
        urlKey = self.request.get("urlKey")
        thisUser = users.get_current_user()

        query = UsermadeLesson.query()
        if self.request.get("creator") == "create":
            query = UsermadeLesson.query()
            userLessons = query.filter(UsermadeLesson.author == thisUser)
            existingLesson = userLessons.filter(UsermadeLesson.name == lessonName).fetch(1)

        else:
            thisLesson = query.filter(UsermadeLesson.urlKey == urlKey).fetch(1)[0]
            if thisLesson.publicEdit == "True":
                existingLesson = query.filter(UsermadeLesson.urlKey == urlKey).fetch(1)
            elif thisLesson.publicEdit == "False" and thisLesson.author == thisUser:
                existingLesson = query.filter(UsermadeLesson.urlKey == urlKey).fetch(1)
            else:
                self.redirect('/LessonModify?page=Unavailable')

        questionCount = self.request.get("questionCount")

        if str(self.request.get("modify")) == "True":
            userLesson = existingLesson[0]

            if self.request.get("publicEdit") == "yes":
                userLesson.publicEdit = "True"
            elif self.request.get("publicEdit") == "no":
                userLesson.publicEdit = "False"

            if self.request.get("publicView") == "yes":
                userLesson.publicView = "True"
            elif self.request.get("publicView") == "no":
                userLesson.publicView = "False"

            if self.request.get("publicExecute") == "yes":
                userLesson.publicExecute = "True"
            elif self.request.get("publicExecute") == "no":
                userLesson.publicExecute = "False"

            if self.request.get("addRcode") == "yes" and "R" not in userLesson.languages:
                userLesson.languages.append("R")
            if self.request.get("addPython") == "yes" and "Python" not in userLesson.languages:
                userLesson.languages.append("Python")
            if self.request.get("removeRcode") == "yes" and "R" in userLesson.languages:
                userLesson.languages.remove("R")
                userLesson.rcodeFinal = [""] * len(userLesson.problems)
                userLesson.rcodeInstruct = [""] * len(userLesson.problems)     
                userLesson.rcodeInit = [""] * len(userLesson.problems)  
            if self.request.get("removePython") == "yes" and "Python" in userLesson.languages:
                userLesson.languages.remove("Python")
                userLesson.pythonFinal = [""] * len(userLesson.problems)
                userLesson.pythonInstruct = [""] * len(userLesson.problems)
                userLesson.pythonInit = [""] * len(userLesson.problems)

            deleteIndices = self.request.get_all("removeQuestion")
            deleteIndices = map(int, deleteIndices)
            for index in sorted(deleteIndices, reverse=True):
                del userLesson.problems[index]
                if len(userLesson.pythonFinal) > 0:
                    del userLesson.pythonInit[index]
                    del userLesson.pythonInstruct[index]
                    del userLesson.pythonFinal[index]
                if len(userLesson.rcodeFinal) > 0:
                    del userLesson.rcodeInit[index]
                    del userLesson.rcodeInstruct[index]
                    del userLesson.rcodeFinal[index]

            questionAdd = False

            try:
                addQuestions = int(self.request.get("addQuestions"))
                questionAdd = True
            except ValueError:
                pass

            if questionAdd:
                userLesson.problems = userLesson.problems[:] + ([""] * addQuestions)
                userLesson.rcodeFinal = userLesson.rcodeFinal[:] + ([""] * addQuestions)
                userLesson.rcodeInstruct = userLesson.rcodeInstruct[:] + ([""] * addQuestions)
                userLesson.rcodeInit = userLesson.rcodeInit[:] + ([""] * addQuestions)
                userLesson.pythonFinal = userLesson.pythonFinal[:] + ([""] * addQuestions)
                userLesson.pythonInstruct = userLesson.pythonInstruct[:] + ([""] * addQuestions)
                userLesson.pythonInit = userLesson.pythonInit[:] + ([""] * addQuestions)
            userLesson.put()

        # If not modifying lesson
        else:
            if len(existingLesson) > 0:
                newLesson = False
                userLesson = existingLesson[0]
                tempLanguages = userLesson.languages
            else:
                newLesson = True
                userLesson = UsermadeLesson(id=''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(20)]))
                userLesson.urlKey = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(20)])
                userLesson.publicEdit = "False"
                userLesson.publicView = "False"
                userLesson.publicExecute = "False"
                userLesson.name = lessonName
                userLesson.author = thisUser
                userLesson.reminder = 'Enter your code in the box provided if the answer is not correct, the difference between the answer produces by running the correct solution and yours will be shown.'
                userLesson.problems= [""] * int(questionCount)
                userLesson.pythonInstruct= [""] * int(questionCount)
                userLesson.pythonInit= [""] * int(questionCount)
                userLesson.pythonFinal= [""] * int(questionCount)
                userLesson.rcodefinal= [""] * int(questionCount)
                userLesson.rcodeInstruct= [""] * int(questionCount)
                userLesson.rcodeInit = [""] * int(questionCount)
                userLesson.paragraph = ""
                userLesson.header = ""
                tempLanguages = []
                if self.request.get("python") == "yes":
                    tempLanguages.append("Python")
                if self.request.get("rcode") == "yes":
                    tempLanguages.append("R")
            userLesson.languages = tempLanguages[:]
            if len(questionCount) == 1:
                if not newLesson:
                    userLesson.problems = self.request.get_all("problem")
                    userLesson.pythonInstruct = self.request.get_all("Python-instruct")
                    userLesson.pythonInit = self.request.get_all("Python-init")
                    userLesson.pythonFinal = self.request.get_all("Python-final")
                    userLesson.rcodeFinal = self.request.get_all("R-final")
                    userLesson.rcodeInstruct = self.request.get_all("R-instruct")
                    userLesson.rcodeInit = self.request.get_all("R-init")
                    userLesson.header = self.request.get("fullLesson")
                    userLesson.paragraph = self.request.get("paragraph")
                    userLesson.put()
        userLesson.put()

        if thisUser == userLesson.author:
            self.redirect('/LessonModify?page='+str(lessonName))
        else:
            self.redirect('/LessonModify?public='+str(userLesson.urlKey))

#Handles page redirects
app = webapp2.WSGIApplication([
    ('/Home', HomeHandler),
    ('/', WelcomeHandler),
    ('/oauth', OAuthHandler),
    (decorator.callback_path, decorator.callback_handler()),
    ('/Lessons', LessonsHandler),
    ('/Profile', ProfileHandler),
    ('/About', AboutHandler),
    ('/Help', HelpHandler),
    ('/Leaderboard', LeaderboardHandler),
    ('/Grade', GalaxyToLearn2MineHandler),
    ('/newKey', newKeyHandler),
    ('/Search', SearchHandler),
    ('/Tutorial', TutorialHandler),
    ('/TutorialLesson', GradeHandler),
    ('/TutorialProfile', TutorialProfileHandler),
    ('/DMLesson', DMLessonHandler),
    ('/Grader', GradeHandler),
    ('/LessonModify', LessonModifyHandler),
    ('/OnsiteGrader', GradingHandler),
    ('/LessonCreator', LessonCreatorHandler),
    ('/LessonPreview', LessonPreviewHandler)
], debug=True)
