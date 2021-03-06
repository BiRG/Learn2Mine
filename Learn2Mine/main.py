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
from __future__ import division
#from bioblend import galaxy
from galaxy_api import *
from common import *
import json
import time
import ndb_json
import copy

# Learn2Mine-Specific Imports
import getBadges
import lessonWriter, tutorialWriter, dmWriter, lessonMaker
import skillTree
import issueBadge

# Python imports
import fnmatch
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

                badgeDisplay = ''
                lessonKeys = User2Lesson.query().filter(User2Lesson.user == users.get_current_user()).fetch(100)
                if len(lessonKeys) > 1:
                        for key in lessonKeys:
                                if len(key.badge) > 0:
                                        badgeDisplay = badgeDisplay + "<img width='100px' height='100px' src='/Badge?id=" + key.badge + "'></img>"
						
                else:
                        badgeDisplay = 'You have not yet earned any badges'
                self.response.write('<script src="https://beta.openbadges.org/issuer.js"></script>')
                template_values = {'user':useremail,'badgeDisplay':badgeDisplay}
                self.response.write(template.render(template_values))
	"""
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
	"""



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
		template = JINJA_ENVIRONMENT.get_template('ProfileGraph.html')
	        userLessons = UsermadeLesson.query().filter(UsermadeLesson.publicView == "True").fetch(1000)
        	lessonHeaderArray = []
        	lessonParagraphArray = []
		imgArray = []
        	urlKeyArray = []
		for lesson in userLessons:
		        badgeQuery = LessonBadge.query().filter(LessonBadge.lesson == lesson.urlKey).fetch(1)
		        if len(badgeQuery) > 0:
		            imgArray.append(badgeQuery[0].lesson)
			else:
		            imgArray.append("")

			lessonHeaderArray.append(lesson.header)
			lessonParagraphArray.append(lesson.paragraph)
			urlKeyArray.append(lesson.urlKey)
		template_values = { 'user': useremail, 'lessonHeaders': lessonHeaderArray, 'lessonParagraphs': lessonParagraphArray, 'urlKeys': urlKeyArray, 'imgs': imgArray}

		self.response.write(template.render(template_values))


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

class LessonHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        thisUser = users.get_current_user()
        template = JINJA_ENVIRONMENT.get_template('Lesson.html')
	if self.request.get("key") != "":
            page = self.request.get("key")
            queryResult = UsermadeLesson.query().filter(UsermadeLesson.urlKey == page).fetch(1)
            public = True
	elif self.request.get("page") != "":
            page = self.request.get("page")
            queryResult = DMLesson.query().filter(DMLesson.name == page).fetch(1)
            public = False
        else:
            template_values = {'user':thisUser.email(),'errorCatch':"yes"}
            self.response.write(template.render(template_values))
            return


        if len(queryResult) > 0:
            thisLesson = queryResult[0]
        else:
            template_values = {'user':thisUser.email(),'errorCatch':"yes"}
            self.response.write(template.render(template_values))
            return

        returnLanguages = []
        if "Python" in thisLesson.languages:
            returnLanguages.append("python")
        if "R" in thisLesson.languages:
            returnLanguages.append("rcode")

        existingUserLessonKey = User2Lesson.query().filter(User2Lesson.user == users.get_current_user()).filter(User2Lesson.lessonID == page).fetch(1)
        if not existingUserLessonKey:
            userLessonKey = User2Lesson()
            userLessonKey.python = [""] * len(thisLesson.problems)
            userLessonKey.rcode = [""] * len(thisLesson.problems)
            userLessonKey.historyID = [""] * len(thisLesson.problems)
            userLessonKey.outputID = [""] * len(thisLesson.problems)
            userLessonKey.mostRecent = [""] * len(thisLesson.problems)
            userLessonKey.history = [""] * len(thisLesson.problems)
            userLessonKey.user = users.get_current_user()
            userLessonKey.lessonID = page
            userLessonKey.badge = ""
            userLessonKey.experience = 0
            userLessonKey.returnStatements = ["No submission"] * len(thisLesson.problems)
            userLessonKey.put()
        else:
            userLessonKey = existingUserLessonKey[0]
        returnVals = userLessonKey.returnStatements[:]
        experience = userLessonKey.experience
        printProblems = []
        for problem in thisLesson.problems:
           #printProblems.append("<br />".join(problem.split("\n")))
           printProblems.append(problem)

	template_values = {'user':thisUser.email(), 'problems':printProblems,'lesson':thisLesson,'languages':returnLanguages,'urlKey':page,'result':returnVals,'exp':experience, 'badge':userLessonKey.badge, 'public':public,'mostRecent':userLessonKey.mostRecent}
        if public:
            template_values.update({'urlKey':page})
        else:
            template_values.update({'page':page})
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
		studentCode = self.request.get("studentCode")
		email = str(users.get_current_user())
		if not self.request.get("urlKey"):
			type = "DM"
			thisLesson = DMLesson.query().filter(DMLesson.name == self.request.get("page")).fetch(1)[0]
			page = self.request.get("page")

		else:
			type = "Public"
			thisLesson = UsermadeLesson.query().filter(UsermadeLesson.urlKey == self.request.get("urlKey")).fetch(1)[0]
			page = self.request.get("urlKey")

		language = self.request.get("language")
		problem = self.request.get("question")
		if "Python Code" in language:
			language = "python"
			instructCode = thisLesson.pythonInstruct[int(problem)-1]
			initCode = thisLesson.pythonInit[int(problem)-1]
			finalCode = thisLesson.pythonFinal[int(problem)-1]
		elif "R Code" in language:
			language = "rcode"
			instructCode = thisLesson.rcodeInstruct[int(problem)-1]
			initCode = thisLesson.rcodeInit[int(problem)-1]
			finalCode = thisLesson.rcodeFinal[int(problem)-1]

		newQuery = GalaxyParams.query()
		if not newQuery.fetch(1):
			galaxy = GalaxyParams()
			galaxy.api_key = "5b70f416e0a2685d6b63b7c12559b212"
			galaxy.url = "http://localhost:8081/api/"
			galaxy.workflow_id = "fb85969571388350"
			galaxy.put()
			time.sleep(0.2)

		# Now we make a galaxy api call
		# This call will grade the student's work
		# We should get an id back from the galaxy api call

		galaxyInstance = GalaxyParams.query().fetch(1)[0]
		api_key = galaxyInstance.api_key
		workflow_id = galaxyInstance.workflow_id
		url = galaxyInstance.url
		historyid = page

		other=json.dumps({"email":email,"studentCode":studentCode, "instructorCode":instructCode, "initializationCode":initCode, "finalizationCode":finalCode, "language":language, "badgeName":""})
		results = workflow_execute_parameters(api_key,url+'workflows/',workflow_id,historyid,"param=gradeCode=other="+other)

		outputID = results['outputs'][0]
		hist_id = results['history']

		userLesson = User2Lesson.query().filter(User2Lesson.user == users.get_current_user()).filter(User2Lesson.lessonID == page).fetch(1)[0]

		if language == "python":
			userLesson.python[int(problem)-1] = studentCode
		elif language == "rcode":
			userLesson.rcode[int(problem)-1] = studentCode

		userLesson.history[int(problem)-1] = studentCode
		userLesson.mostRecent[int(problem)-1] = studentCode
		userLesson.historyID[int(problem)-1] = hist_id
		userLesson.outputID[int(problem)-1] = outputID
		userLesson.put()
                url = str(galaxyInstance.url) + "histories/" + hist_id + "/contents/" + outputID + "/display"
                results = display_result(galaxyInstance.api_key,url)
		if results == "Running":
			if any(string in userLesson.returnStatements[int(problem)-1] for string in ["Congratulations!","- previous correct", "you have previously solved this problem"]):
				returnStatement = "Job running - previous correct"
			elif any(string in userLesson.returnStatements[int(problem)-1] for string in ["code you entered is incorrect","- previous incorrect","submission is incorrect"]):
				returnStatement = "Job running - previous incorrect"
			else:
				returnStatement = "Job running"
		else:
			returnAdd = "<br><a href=\"javascript:toggleDiv('returnAdd"+str(int(problem)-1)+"');\" style=\"background-color: #ccc; padding: 5px 10px;\">Show/Hide Details</a><br>"
			if results['return'] == "correct":
				returnAdd += "<div id='returnAdd"+str(int(problem)-1)+"' style='display: none;'>" + "<br />".join(results['student_stdout'].split("\n")) + "</div>"
				returnStatement = "Congratulations! You've solved this problem.<br>" + returnAdd
			else:
				returnAdd += "<div id='returnAdd"+str(int(problem)-1)+"' style='display: none;'>" + "<br />".join(results['difference_stdout'].split("\n")) + "</div>"
				if "previous correct" in userLesson.returnStatements[int(problem)-1]:
					returnStatement = "Your submission is incorrect, but you won't be penalized as<br>you have previously solved this problem.<br>" + returnAdd
				else:
					returnStatement = "The code you entered is incorrect.<br>" + returnAdd
			userLesson.returnStatements[int(problem)-1] = returnStatement
			returnVals = userLesson.returnStatements[:]
			experience = len(fnmatch.filter(returnVals,'*solved this problem.*'))/len(thisLesson.problems)
			if int(problem) == len(thisLesson.problems) and thisLesson.flag == "True" and " solved this problem." in userLesson.returnStatements[int(problem)-1]:
				experience = 100
			else:
				experience = experience*100
			userLesson.experience = experience
			if experience == 100:
				userLesson.badge = self.request.get("urlKey")
		userLesson.returnStatements[int(problem)-1] = returnStatement
		returnLanguages = []
		if "Python" in thisLesson.languages:
			returnLanguages.append("python")
		if "R" in thisLesson.languages:
			returnLanguages.append("rcode")
		userLesson.put()
		time.sleep(0.5)
		if type == "DM":
			self.redirect("/DMLesson?page="+page+"#q"+problem)
		else:
			self.redirect("/PublicLesson?key="+page+"#q"+problem)
			
class GradeRefreshHandler(webapp2.RequestHandler):
	def post(self):
                if not self.request.get("urlKey"):
			type = "DM"
			page = self.request.get("page")
	                thisLesson = DMLesson.query().filter(UsermadeLesson.name == page).fetch(1)[0]

		else:
			type = "Public"
			page = self.request.get("urlKey")
	                thisLesson = UsermadeLesson.query().filter(UsermadeLesson.urlKey == page).fetch(1)[0]

		problem = self.request.get("question")
                userLesson = User2Lesson.query().filter(User2Lesson.user == users.get_current_user()).filter(User2Lesson.lessonID == page).fetch(1)[0]
                galaxyInstance = GalaxyParams.query().fetch(1)[0]
                hist_id = userLesson.historyID[int(problem)-1]
                output_id = userLesson.outputID[int(problem)-1]
                url = str(galaxyInstance.url) + "histories/" + hist_id + "/contents/" + output_id + "/display"
		try:
                	results = display_result(galaxyInstance.api_key,url)
		except:
			returnStatement = 'Cannot get status of this submission. Please clear and try again.'
			results = "ERROR"

		if results == "Running":
                        if any(string in userLesson.returnStatements[int(problem)-1] for string in ["Congratulations!","- previous correct"]):
                                returnStatement = "Job running - previous correct"
			elif any(string in userLesson.returnStatements[int(problem)-1] for string in ["code you entered is incorrect","- previous incorrect","submission is ioncorrect"]):
                                returnStatement = "Job running - previous incorrect"
                        else:
                                returnStatement = "Job running"
                elif results != "ERROR":
			returnAdd = "<br><a href=\"javascript:toggleDiv('returnAdd"+str(int(problem)-1)+"');\" style=\"background-color: #ccc; padding: 5px 10px;\">Show/Hide Details</a><br>"
                        if results['return'] == "correct":
				returnAdd += "<div id='returnAdd"+str(int(problem)-1)+"' style='display: none;'>" + "<br />".join(results['student_stdout'].split("\n")) + "</div>"
                                returnStatement = "Congratulations! You've solved this problem.<br>" + returnAdd
                        else:
				returnAdd += "<div id='returnAdd"+str(int(problem)-1)+"' style='display: none;'>" + "<br />".join(results['difference_stdout'].split("\n")) + "</div>"
                                if "previous correct" in userLesson.returnStatements[int(problem)-1]:
                                        returnStatement = "Your submission is incorrect, but you won't be penalized as<br>you have previously solved this problem.<br>" + returnAdd
                                else:
					returnStatement = "The code you entered is incorrect.<br>" + returnAdd
                        userLesson.returnStatements[int(problem)-1] = returnStatement
                        returnVals = userLesson.returnStatements[:]
                        experience = len(fnmatch.filter(returnVals,'*solved this problem.*'))/len(thisLesson.problems)
			if int(problem) == len(thisLesson.problems) and thisLesson.flag == "True" and " solved this problem." in userLesson.returnStatements[int(problem)-1]:
				experience = 100
			else:
				experience = experience*100
                        userLesson.experience = experience
			if experience == 100:
				userLesson.badge = self.request.get("urlKey")
                userLesson.returnStatements[int(problem)-1] = returnStatement
		userLesson.put()
		time.sleep(0.75)
                if type == "DM":
                        self.redirect("/DMLesson?page="+page+"#q"+problem)
                else:
                        self.redirect("/PublicLesson?key="+page+"#q"+problem)

class DeleteGalaxyHistory(webapp2.RequestHandler):
	def post(self):
                if not self.request.get("urlKey"):
			type = "DM"
			page = self.request.get("page")
		else:
			type = "Public"
			page = self.request.get("urlKey")
		problem = self.request.get("question")
		userLesson = User2Lesson.query().filter(User2Lesson.user == users.get_current_user()).filter(User2Lesson.lessonID == page).fetch(1)[0]
#		galaxyInput = GalaxyParams.query().fetch(1)[0]
#		instance = galaxy.GalaxyInstance(url=galaxyInput.url, key=galaxyInput.api_key)
#		instance.histories.delete_history(id=userLesson.historyID[int(problem)-1])
		userLesson.historyID[int(problem)-1] = ""
		userLesson.outputID[int(problem)-1] = ""
		userLesson.returnStatements[int(problem)-1] = "No submission"
		userLesson.put()
		time.sleep(0.5)
		if type == "DM":
			self.redirect("/DMLesson?page="+page+"#q"+problem)
		else:
			self.redirect("/PublicLesson?key="+page+"#q"+problem)

class GalaxyParams(ndb.Model):
    """Models an individual User Lesson entry with author, content, and date."""

    url = ndb.StringProperty(indexed=True)
    api_key = ndb.StringProperty(indexed=True)
    workflow_id = ndb.StringProperty(indexed=True)

class Learn2MineClass(ndb.Model):
    """Models an individual User Lesson entry with author, content, and date."""

    instructor = ndb.UserProperty(indexed=True)
    students = ndb.UserProperty(repeated=True)
    PublicLessonplan = ndb.StringProperty(repeated=True)
    DMLessonplan = ndb.StringProperty(repeated=True)
    className = ndb.StringProperty(indexed=True)
    classKey = ndb.StringProperty(indexed=True)

class User2Lesson(ndb.Model):
    user = ndb.UserProperty(indexed=True)
    lessonID = ndb.StringProperty(indexed=True)
    historyID = ndb.StringProperty(repeated=True)
    outputID = ndb.StringProperty(repeated=True)
    experience = ndb.FloatProperty()
    badge = ndb.StringProperty(indexed=True)
    mostRecent = ndb.TextProperty(repeated=True)
    history = ndb.TextProperty(repeated=True)
    python = ndb.TextProperty(repeated=True)
    rcode = ndb.TextProperty(repeated=True)
    returnStatements = ndb.TextProperty(repeated=True)

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
    paragraph = ndb.TextProperty(indexed=False)

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

class LessonBadge(ndb.Model):
    badge = ndb.BlobProperty()
    lesson = ndb.StringProperty()

class LessonCreatorHandler(webapp2.RequestHandler):
    @decorator.oauth_required

    def post(self):
        lessonName = self.request.get("lesson2delete")
        thisUser = users.get_current_user()
        thisLesson = UsermadeLesson.query().filter(UsermadeLesson.author == thisUser).filter(UsermadeLesson.name == lessonName).fetch(1)[0]
        thisLesson.key.delete()
	time.sleep(0.2)
        self.redirect('/LessonCreator')

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('LessonCreator.html')
        thisUser = users.get_current_user()

        time.sleep(0.2)
        userLessons = UsermadeLesson.query().filter(UsermadeLesson.author == thisUser).fetch(1000)
        lessonArray = []
        for lesson in userLessons:
            lessonArray.append(lesson.name)
        template_values = { 'user': thisUser.email(), 'existingLessons': lessonArray }
        self.response.write(template.render(template_values))

class LessonPreviewHandler(webapp2.RequestHandler):
    @decorator.oauth_required

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('LessonPreview.html')
        thisUser = users.get_current_user()
        lessonName = self.request.get("page")
        if lessonName != "":
            userLessonQuery = UsermadeLesson.query().filter(UsermadeLesson.author == thisUser).filter(UsermadeLesson.name == lessonName).fetch(1)
            if len(userLessonQuery) > 0:
                userLesson = userLessonQuery[0]
            else:
                template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return
        elif self.request.get("key") != "":
            key = self.request.get("key")
            userLessonQuery = UsermadeLesson.query().filter(UsermadeLesson.urlKey == key).fetch(1)
            if len(userLessonQuery) > 0:
                foundLesson = userLessonQuery[0]
            else:
                template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return
            if foundLesson.publicView == "True":
                userLesson = foundLesson
            else:
                if foundLesson.author == thisUser:
                    userLesson = foundLesson
                else:
                    template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                    self.response.write(template.render(template_values))
                    return

        if userLesson:
            printProblems = []
            for problem in userLesson.problems:
                #printProblems.append("<br />".join(problem.split("\n")))
                printProblems.append(problem)
            template_values = {
                'user':thisUser.email(), 'problems':printProblems, 'languages': userLesson.languages, 'paragraph':userLesson.paragraph, 'header':userLesson.header
            }

        else:
            template_values = {'user':thisUser.email(),'errorCatch':"yes"}
        self.response.write(template.render(template_values))

class LessonModifyHandler(webapp2.RequestHandler):
    @decorator.oauth_required

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('LessonModify.html')
        thisUser = users.get_current_user()
        if self.request.get("page") != "":
            lessonName = self.request.get("page")
            lessonplanQuery = UsermadeLesson.query().filter(UsermadeLesson.author == thisUser).filter(UsermadeLesson.name == lessonName).fetch(1)
            if len(lessonplanQuery) > 0:
                userLesson = lessonplanQuery[0]
            else:
                template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return

        elif self.request.get("key") != "":
            public = self.request.get("key")
            queryLesson = UsermadeLesson.query().filter(UsermadeLesson.urlKey == public).fetch(1)
            if len(queryLesson) > 0:
                if queryLesson[0].publicEdit == "True":
                    userLesson = queryLesson[0]
                elif queryLesson[0].author == thisUser:
                    userLesson = queryLesson[0]
                else:
                    template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                    self.response.write(template.render(template_values))
                    return
            else:
                template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return

        else:
            template_values = {'user':thisUser.email(),'errorCatch':"yes"}
            self.response.write(template.render(template_values))
            return

        badgeQuery = LessonBadge.query().filter(LessonBadge.lesson == userLesson.urlKey).fetch(1)
        badge = None
        if len(badgeQuery) > 0:
            badge = badgeQuery[0].lesson
        template_values = {'lesson':userLesson, 'user':thisUser,'img':badge}
        self.response.write(template.render(template_values))

    def post(self):
        lessonName = self.request.get("lessonName")
        urlKey = self.request.get("urlKey")
        thisUser = users.get_current_user()

        if self.request.get("creator") == "create":
            existingLesson = UsermadeLesson.query().filter(UsermadeLesson.author == thisUser).filter(UsermadeLesson.name == lessonName).fetch(1)

        else:
            thisLesson = UsermadeLesson.query().filter(UsermadeLesson.urlKey == urlKey).fetch(1)[0]
            if thisLesson.publicEdit == "True" or (thisLesson.publicEdit == "False" and thisLesson.author == thisUser):
                existingLesson = UsermadeLesson.query().filter(UsermadeLesson.urlKey == urlKey).fetch(1)
            else:
                template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                self.response.write(template.render(template_values))
                return

        questionCount = self.request.get("questionCount")

        newBadge = self.request.get('pic')
        if newBadge:
            badgeQuery = LessonBadge.query().filter(LessonBadge.lesson == urlKey).fetch(1)
            if len(badgeQuery) == 0:
                lessonBadge = LessonBadge()
                lessonBadge.badge = str(newBadge)
                lessonBadge.lesson = urlKey
            else:
                lessonBadge = badgeQuery[0]
                lessonBadge.badge = str(newBadge)
            lessonBadge.put()

        if str(self.request.get("modify")) == "True":
            userLesson = existingLesson[0]

            if self.request.get("publicEdit") == "yes":
                userLesson.publicEdit = "True"
            else:
                userLesson.publicEdit = "False"

            if self.request.get("publicView") == "yes":
                userLesson.publicView = "True"
            else:
                userLesson.publicView = "False"

            if self.request.get("publicExecute") == "yes":
                userLesson.publicExecute = "True"
            else:
                userLesson.publicExecute = "False"

            if self.request.get("addRcode") == "yes" and "R" not in userLesson.languages:
                userLesson.languages.append("R")
            if self.request.get("addPython") == "yes" and "Python" not in userLesson.languages:
                userLesson.languages.append("Python")
            if self.request.get("removeRcode") == "yes" and "R" in userLesson.languages:
                userLesson.languages.remove("R")
                userLesson.rcodeFinal = [""] * len(userLesson.problems)
                userLesson.rcodeInstruct = [""] * int(questionCount)
                userLesson.rcodeInit = [""] * int(questionCount)
            if self.request.get("removePython") == "yes" and "Python" in userLesson.languages:
                userLesson.languages.remove("Python")
                userLesson.pythonFinal = [""] * int(questionCount)
                userLesson.pythonInstruct = [""] * int(questionCount)
                userLesson.pythonInit = [""] * int(questionCount)

            deleteIndices = self.request.get_all("removeQuestion")
            deleteIndices = map(int, deleteIndices)
            for index in sorted(deleteIndices, reverse=True):
                del userLesson.problems[index]
                if len(userLesson.pythonFinal) > 0:
                    del userLesson.pythonInit[index],userLesson.pythonInstruct[index],userLesson.pythonFinal[index]
                if len(userLesson.rcodeFinal) > 0:
                    del userLesson.rcodeInit[index],userLesson.rcodeInstruct[index],userLesson.rcodeFinal[index]
                for lesson in User2Lesson.query().filter(User2Lesson.lessonID == urlKey).fetch(1000):
                    del lesson.returnStatements[index]
                    del lesson.python[index]
                    del lesson.rcode[index]
                    del lesson.historyID[index]
                    del lesson.outputID[index]
                    del lesson.mostRecent[index]
                    del lesson.history[index]
                    lesson.put()

            questionAdd = False

            try:
                addQuestions = int(self.request.get("addQuestions"))
                questionAdd = True
            except ValueError:
                pass

            if self.request.get("masterProblem") == "True":
                userLesson.flag = "True"
            else:
                userLesson.flag = "False"

            if questionAdd:
                userLesson.problems = userLesson.problems[:] + [""]*addQuestions
		if "R" in userLesson.languages:
                    userLesson.rcodeFinal = userLesson.rcodeFinal[:] + [""]*addQuestions
                    userLesson.rcodeInstruct = userLesson.rcodeInstruct[:] + [""]*addQuestions
                    userLesson.rcodeInit = userLesson.rcodeInit[:] + [""]*addQuestions
		if "Python" in userLesson.languages:
                    userLesson.pythonFinal = userLesson.pythonFinal[:] + [""]*addQuestions
                    userLesson.pythonInstruct = userLesson.pythonInstruct[:]+ [""]*addQuestions
                    userLesson.pythonInit = userLesson.pythonInit[:] + [""]*addQuestions
                for lesson in User2Lesson.query().filter(User2Lesson.lessonID == urlKey).fetch(1000):
                    lesson.returnStatements = lesson.returnStatements[:] + ["No submission"]*addQuestions
                    lesson.python = lesson.python[:] + [""]*addQuestions
                    lesson.rcode = lesson.rcode[:] + [""]*addQuestions
                    lesson.historyID = lesson.historyID[:] + [""]*addQuestions
                    lesson.outputID = lesson.outputID[:] + [""]*addQuestions
                    lesson.mostRecent = lesson.mostRecent[:] + [""]*addQuestions
                    lesson.history = lesson.history[:] + [""]*addQuestions
                    lesson.experience = 100*(len(fnmatch.filter(lesson.returnStatements,'*solved this problem.*'))/len(userLesson.problems))
                    lesson.put()
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
		userLesson.flag = "False"
                userLesson.publicEdit = "False"
                userLesson.publicView = "False"
                userLesson.publicExecute = "False"
                userLesson.name = lessonName
                userLesson.author = thisUser
                userLesson.problems = [""] * int(questionCount)
                userLesson.pythonInstruct = [""] * int(questionCount)
                userLesson.pythonInit = [""] * int(questionCount)
                userLesson.pythonFinal = [""] * int(questionCount)
                userLesson.rcodeInit = [""] * int(questionCount)
                userLesson.rcodeFinal = [""] * int(questionCount)
                userLesson.rcodeInstruct = [""] * int(questionCount)
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
                    userLesson.rcodeInit = self.request.get_all("R-init")
                    userLesson.rcodeInstruct = self.request.get_all("R-instruct")
                    userLesson.header = self.request.get("fullLesson")
                    userLesson.paragraph = self.request.get("paragraph")
                    userLesson.put()
        userLesson.put()
        time.sleep(0.2)

        if thisUser == userLesson.author:
            self.redirect('/LessonModify?page='+str(lessonName))
        else:
            self.redirect('/LessonModify?key='+str(userLesson.urlKey))

class ClassPortalHandler(webapp2.RequestHandler):
	@decorator.oauth_required

	def get(self):
		template = JINJA_ENVIRONMENT.get_template('Class.html')
	        thisUser = users.get_current_user()
		instructing = Learn2MineClass.query().filter(Learn2MineClass.instructor == thisUser).fetch(10000)
		enrolledQuery = Learn2MineClass.query().fetch(10000)
		enrolledClasses = []
		for thisClass in enrolledQuery:
			if thisUser in thisClass.students:
				enrolledClasses.append([thisClass.className,thisClass.classKey])
		instructingClasses = []
		for lesson in instructing:
			instructingClasses.append(lesson.className)
		template_values = {'user':thisUser.email(), 'instructingClasses':instructingClasses, 'enrolledClasses': enrolledClasses}
	        self.response.write(template.render(template_values))

	def post(self):
		self.redirect('/Class')

class ClassCreatorHandler(webapp2.RequestHandler):
	@decorator.oauth_required

	def get(self):
		template = JINJA_ENVIRONMENT.get_template('ClassCreator.html')
	        thisUser = users.get_current_user()
		DMLessonQuery = Learn2MineLesson.query().fetch(1)
		DMLessons = []
		for DMLesson in DMLessonQuery:
			DMLessons.append([DMLesson.header, DMLesson.name])
		PublicLessons = []
		for PublicLesson in UsermadeLesson.query().filter(UsermadeLesson.publicExecute == "True").fetch(100):
			PublicLessons.append([PublicLesson.header, PublicLesson.urlKey])		
        	if thisUser:   
        	    url = users.create_logout_url(self.request.uri)
        	    url_linktext = 'Logout'
		template_values = {'user':thisUser.email(), 'url_linktext':url_linktext, 'AddDMLessons':DMLessons,'AddPublicLessons':PublicLessons}
	        self.response.write(template.render(template_values))

	def post(self):
		thisUser = users.get_current_user()
		DMLessons = self.request.get_all("addDMLesson")
		PublicLessons = self.request.get_all("addPublicLesson")
		className = self.request.get("className")
		newClass = Learn2MineClass()
		newClass.PublicLessonplan,newClass.DMLessonplan,newClass.students = ([],)*3
		newClass.PublicLessonplan.extend(PublicLessons)
		newClass.DMLessonplan.extend(DMLessons)
		newClass.instructor = thisUser
		newClass.className = className
		newClass.classKey = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(20)])
		newClass.put()
		self.redirect('/ClassManager?class='+className)

class ClassManagerHandler(webapp2.RequestHandler):
        @decorator.oauth_required
	def get(self):
		time.sleep(0.4)
		template = JINJA_ENVIRONMENT.get_template('ClassManager.html')
	        thisUser = users.get_current_user()
		className = self.request.get("class")
		existingClassQuery = Learn2MineClass.query().filter(Learn2MineClass.instructor == thisUser).filter(Learn2MineClass.className == className).fetch(1)
		if len(existingClassQuery) > 0:
			thisClass = existingClassQuery[0]
		else:
			template_values = {'user':thisUser.email(),'errorCatch':"yes"}
			self.response.write(template.render(template_values))
			return
		removeDMLessons = []
		removePublicLessons = []
		time.sleep(1)
		for lesson in thisClass.DMLessonplan:
			removeDMLessons.append([Learn2MineLesson.query().filter(Learn2MineLesson.name == lesson).fetch(1)[0].header,lesson])
		for lesson in thisClass.PublicLessonplan:
			try:
				header = UsermadeLesson.query().filter(UsermadeLesson.urlKey == lesson).fetch(1)[0].header
			except:
				header = 'DELETED'	
			removePublicLessons.append([header,lesson])
		addDMLessons = []
		addPublicLessons = []
		for lesson in UsermadeLesson.query().filter(UsermadeLesson.publicExecute == "True").fetch(100):
			if [lesson.header,lesson.urlKey] not in removePublicLessons:
				addPublicLessons.append([lesson.header,lesson.urlKey])
		for lesson in Learn2MineLesson.query().fetch(1000):
			if [lesson.header,lesson.name] not in removeDMLessons:
				addDMLessons.append([lesson.header,lesson.name])
		template_values = {'user':thisUser.email(), 'class':className, 'RemovePublicLessons':removePublicLessons, 'RemoveDMLessons':removeDMLessons, 'AddPublicLessons':addPublicLessons, 
		'AddDMLessons':addDMLessons, 'classKey':thisClass.classKey }
	        self.response.write(template.render(template_values))

	def post(self):
		thisUser = users.get_current_user()
		if self.request.get("deleteClass"):
			className = self.request.get("class")
			thisClass = Learn2MineClass().query().filter(Learn2MineClass.instructor == thisUser).filter(Learn2MineClass.className == className).fetch(1)[0]
			thisClass.key.delete()
			self.redirect('/Class')
			return
		AddDMLessons = self.request.get_all("addDMLessons")
		AddPublicLessons = self.request.get_all("addPublicLesson")
		RemoveDMLessons = self.request.get_all("removeDMLessons")
		RemovePublicLessons = self.request.get_all("removePublicLesson")
		className = self.request.get("class")
		newClassName = self.request.get("newClassName")
		thisClass = Learn2MineClass().query().filter(Learn2MineClass.instructor == thisUser).filter(Learn2MineClass.className == className).fetch(1)[0]
		for lesson in AddPublicLessons:
			thisClass.PublicLessonplan.append(lesson)
		for lesson in AddDMLessons:
			thisClass.DMLessonplan.append(lesson)
		for lesson in RemovePublicLessons:
			thisClass.PublicLessonplan.remove(lesson)
		for lesson in RemoveDMLessons:
			thisClass.DMLessonplan.remove(lesson)
		if newClassName:
			thisClass.className = newClassName
			className = newClassName
		thisClass.put()
		self.redirect('/ClassManager?class='+className)

class EnrollmentHandler(webapp2.RequestHandler):
	@decorator.oauth_required
	def get(self):
		classKey = self.request.get("key")
		thisUser = users.get_current_user()
		if not classKey:
                        template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                        self.response.write(template.render(template_values))
                        return
		template = JINJA_ENVIRONMENT.get_template('EnrollClass.html')
		classQuery = Learn2MineClass.query().filter(Learn2MineClass.classKey==classKey).fetch(1)
		if len(classQuery) == 0:
                        template_values = {'user':thisUser.email(),'errorCatch':"yes"}
                        self.response.write(template.render(template_values))
                        return
		thisLesson = classQuery[0]
		if thisUser in thisLesson.students:
	                self.redirect('/Class')
		template_values = {'user':thisUser.email(), 'className':thisLesson.className,'classInstructor':thisLesson.instructor.email(), 'classKey':classKey }
		self.response.write(template.render(template_values))
	def post(self):
		classKey = self.request.get("key")
		thisUser = users.get_current_user()
		enrollmentStatus = self.request.get("join")
                thisClass = Learn2MineClass.query().filter(Learn2MineClass.classKey == classKey).fetch(1)[0]
		classStudents = thisClass.students
		if enrollmentStatus == "Yes" and thisUser not in classStudents:
			classStudents.append(thisUser)
			thisClass.put()
			time.sleep(0.5)
	                self.redirect('/GradeViewer?key='+classKey)
		else:
	                self.redirect('/Class')

class GradeViewerHandler(webapp2.RequestHandler):
	@decorator.oauth_required

	def get(self):
		template = JINJA_ENVIRONMENT.get_template('GradeViewer.html')
		thisUser = users.get_current_user()

		classKey = self.request.get("key")
		if not classKey:
			template_values = {'user':thisUser.email(),'errorCatch':"yes"}
			self.response.write(template.render(template_values))
			return
		thisClassQuery = Learn2MineClass.query().filter(Learn2MineClass.classKey == classKey).fetch(1)
		if len(thisClassQuery) == 0:
			template_values = {'user':thisUser.email(),'errorCatch':"yes"}
			self.response.write(template.render(template_values))
			return
		thisClass = thisClassQuery[0]
		lessonplanResults = []
		for DMLesson in thisClass.DMLessonplan:
			lessonGrades = User2Lesson.query().filter(User2Lesson.user == thisUser).filter(User2Lesson.lessonID == DMLesson.name).fetch(1)
			if len(lessonGrades) == 0:
				userGrades = (["No submission"] * len(Learn2MineLesson.query().filter(Learn2MineLesson.name == DMLesson).fetch(1)[0].problems))
			else:
				userGrades = lessonGrades[0].returnStatements
			score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
                        lessonplanResults.append([Learn2MineLesson.query().filter(Learn2MineLesson.name == DMLesson).fetch(1)[0].header,DMLesson,userGrades,"DM",score])
		for PublicLesson in thisClass.PublicLessonplan:
			lessonGrades = User2Lesson.query().filter(User2Lesson.user == thisUser).filter(User2Lesson.lessonID == PublicLesson).fetch(1)
			if len(lessonGrades) == 0:
				userGrades = (["No submission"] * len(UsermadeLesson.query().filter(UsermadeLesson.urlKey == PublicLesson).fetch(1)[0].problems))
			else:
				userGrades = lessonGrades[0].returnStatements
			score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
                        lessonplanResults.append([UsermadeLesson.query().filter(UsermadeLesson.urlKey == PublicLesson).fetch(1)[0].header,PublicLesson,userGrades,"public",score])
		maxProblemCount = 0
		for lesson in lessonplanResults:
			if len(lesson[2]) > maxProblemCount:
				maxProblemCount = len(lesson[2])
		template_values = {'user':thisUser.email(), 'class':thisClass.className, 'lessonplanResults':lessonplanResults, 'maxProblemCount':maxProblemCount,'key':classKey }
		self.response.write(template.render(template_values))

	def post(self):
		thisUser = users.get_current_user()
		key = self.request.get("key")
		findClass = Learn2MineClass.query().filter(Learn2MineClass.classKey == key).fetch(1)[0]
		findClass.students.remove(thisUser)
		findClass.put()
		time.sleep(0.3)
		self.redirect('/Class')

class ClassGradeViewerHandler(webapp2.RequestHandler):
	@decorator.oauth_required

	def get(self):
		template = JINJA_ENVIRONMENT.get_template('ClassGradeViewer.html')
		thisUser = users.get_current_user()
		findClass = self.request.get("class")
		if not findClass:
			template_values = {'user':thisUser.email(),'errorCatch':"yes"}
			self.response.write(template.render(template_values))
			return
		thisClassQuery = Learn2MineClass.query().filter(Learn2MineClass.className == findClass).filter(Learn2MineClass.instructor == thisUser).fetch(1)
		if len(thisClassQuery) == 0:
			template_values = {'user':thisUser.email(),'errorCatch':"yes"}
			self.response.write(template.render(template_values))
			return
		thisClass = thisClassQuery[0]
		publicLessons = []
		DMLessons = []
		studentGrades = []
		if self.request.get("page"):
			name = self.request.get("page")
			lessonClass = UsermadeLesson.query().filter(UsermadeLesson.urlKey == key).fetch(1)[0]
			lesson = lessonClass.header
			for student in thisClass.students:
				lessonGrades = User2Lesson.query().filter(User2Lesson.user == student).filter(User2Lesson.lessonID == name).fetch(1)
				if len(lessonGrades) == 0:
					userGrades = (["No submission"] * len(Learn2MineLesson.query().filter(Learn2MineLesson.name == name).fetch(1)[0].problems))
				else:
					userGrades = lessonGrades[0].returnStatements
				score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
				if lessonClass.flag == "True" and " solved this problem." in userGrades[-1]:
					score = 100
				studentGrades.append([userGrades,score])
			template_values = {'class':findClass, 'grades':studentGrades, 'user':thisUser.email(),'students':thisClass.students,'lesson':lesson, 'DM':"yes"}

		elif self.request.get("key"):
			key = self.request.get("key")
			lessonClass = UsermadeLesson.query().filter(UsermadeLesson.urlKey == key).fetch(1)[0]
			lesson = lessonClass.header
			for student in thisClass.students:
				lessonGrades = User2Lesson.query().filter(User2Lesson.user == student).filter(User2Lesson.lessonID == key).fetch(1)
				if len(lessonGrades) == 0:
					userGrades = (["No submission"] * len(UsermadeLesson.query().filter(UsermadeLesson.urlKey == key).fetch(1)[0].problems))
				else:
					userGrades = lessonGrades[0].returnStatements
				score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
				if lessonClass.flag == "True" and " solved this problem." in userGrades[-1]:
					score = 100
				studentGrades.append([userGrades,score])
			template_values = {'class':findClass, 'grades':studentGrades, 'user':thisUser.email(),'students':thisClass.students,'lesson':lesson, 'public':"yes"}
		else:
			lessonScores = []
			publicCount = 0
			DMCount = 0
			for student in thisClass.students:
				thisLessonScore = []
				if student == thisClass.students[0] and len(publicLessons) == 0:
					for lesson in thisClass.PublicLessonplan:
						publicLessons.append([UsermadeLesson.query().filter(UsermadeLesson.urlKey==lesson).fetch(1)[0].header,lesson])
						publicCount += 1
						lessonGrades = User2Lesson.query().filter(User2Lesson.user == student).filter(User2Lesson.lessonID==lesson).fetch(1)
						if len(lessonGrades) == 0:
							userGrades = (["No submission"] * len(UsermadeLesson.query().filter(UsermadeLesson.urlKey == lesson).fetch(1)[0].problems))
						else:
							userGrades = lessonGrades[0].returnStatements
						score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
						thisLesson = UsermadeLesson.query().filter(UsermadeLesson.urlKey == lesson).fetch(1)[0]
						if thisLesson.flag == "True" and " solved this problem." in userGrades[-1]:
							score = 100
						thisLessonScore.append(score)

#					for lesson in thisClass.DMLessonplan:
#						DMLessons.append([Learn2MineLesson.query().filter(Learn2MineLesson.name==lesson).fetch(1)[0].header,lesson])
#						DMCount += 1
#						lessonGrades = User2Lesson.query().filter(User2Lesson.user == student).filter(User2Lesson.lessonID == lesson).fetch(1)
#						if len(lessonGrades) == 0:
#							userGrades = (["No submission"] * len(Learn2MineLesson.query().filter(Learn2MineLesson.name == lesson).fetch(1)[0].problems))
#						else:
#							userGrades = lessonGrades[0].returnStatements
#						score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
#						thisLessonScore.append(score)
				else:
					for lesson in thisClass.PublicLessonplan:
						lessonGrades = User2Lesson.query().filter(User2Lesson.user == student).filter(User2Lesson.lessonID == lesson).fetch(1)
						if len(lessonGrades) == 0:
							userGrades = (["No submission"] * len(UsermadeLesson.query().filter(UsermadeLesson.urlKey == lesson).fetch(1)[0].problems))
						else:
							userGrades = lessonGrades[0].returnStatements
						score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
						thisLesson = UsermadeLesson.query().filter(UsermadeLesson.urlKey == lesson).fetch(1)[0]
						if thisLesson.flag == "True" and " solved this problem." in userGrades[-1]:
							score = 100
						thisLessonScore.append(score)

#					for lesson in thisClass.DMLessonplan:
#						lessonGrades = User2Lesson.query().filter(User2Lesson.user == student).filter(User2Lesson.lessonID == lesson).fetch(1)
#						if len(lessonGrades) == 0:
#							userGrades = (["No submission"] * len(Learn2MineLesson.query().filter(Learn2MineLesson.name == lesson).fetch(1)[0].problems))
#						else:
#							userGrades = lessonGrades[0].returnStatements
#						score = int((len([i for i, result in enumerate(userGrades) if 'solved this problem' in result])/len(userGrades))*100)
#						thisLessonScore.append(score)
				lessonScores.append([thisLessonScore,int(sum(thisLessonScore)/len(thisLessonScore))])
			if len(thisClass.students) == 0:
				outputMsg = "You do not have any students enrolled in your class yet"
				template_values = {'errorCatch':"yes",'user':thisUser.email(),'outputMsg':outputMsg}
				self.response.write(template.render(template_values))
				return
			gradeSums = [0] * len(lessonScores[0][0])
			for studentGrades in lessonScores:
                                index = 0
                                for grade in studentGrades[0]:
                                        gradeSums[index] += grade
                                        index += 1
			gradeAverages = [int(x/len(lessonScores)) for x in gradeSums]
			template_values = {'class':findClass, 'grades':lessonScores, 'user':thisUser.email(),'students':thisClass.students, 'publicLessons':publicLessons,'DMLessons':DMLessons,'averages':gradeAverages}
		self.response.write(template.render(template_values))

class BadgeViewHandler(webapp2.RequestHandler):
    def get(self):
        image_id = self.request.get('id')
        lessonBadge = LessonBadge.query().filter(LessonBadge.lesson==image_id).fetch(1)[0]
        self.response.headers['content-type'] = 'image/png'
        self.response.out.write(lessonBadge.badge)

class UpdateHandler(webapp2.RequestHandler):
	def get(self):
		# Code for update to be run
		self.redirect("/Home")

class FlareHandler(webapp2.RequestHandler):
	@decorator.oauth_required
	def get(self):
#              template = JINJA_ENVIRONMENT.get_template('Flare.html')
               useremail = users.get_current_user().email()
               f = urllib.urlopen("http://learn2mine.appspot.com/stylesheets/flare.json")
               contents = f.read()

               self.response.write(contents)

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
    ('/TutorialProfile', TutorialProfileHandler),
    ('/DMLesson', LessonHandler),
    ('/PublicLesson', LessonHandler),
    ('/LessonModify', LessonModifyHandler),
    ('/OnsiteGrader', GradingHandler),
    ('/LessonCreator', LessonCreatorHandler),
    ('/LessonPreview', LessonPreviewHandler),
    ('/RefreshGrade', GradeRefreshHandler),
    ('/Class', ClassPortalHandler),
    ('/ClassCreator', ClassCreatorHandler),
    ('/ClassManager', ClassManagerHandler),
    ('/GradeViewer', GradeViewerHandler),
    ('/ClassGradeViewer', ClassGradeViewerHandler),
    ('/EnrollClass', EnrollmentHandler),
    ('/Badge', BadgeViewHandler),
    ('/ClearHistory', DeleteGalaxyHistory),
    ('/UpdateCode', UpdateHandler),
    ('/flare', FlareHandler)
], debug=True)
