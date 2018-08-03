# import libraries 
import json
import urllib
import datetime
from bs4 import BeautifulSoup
from datetime import timedelta
from titlecase import titlecase
from contextlib import closing
from slackclient import SlackClient # pip install SlackClient
from urllib.request import urlopen
from selenium.webdriver import Firefox # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait


# Todays Current Date
date = datetime.datetime.now()
date = date.strftime("%a, %b %d, %Y")
dayOfWeek	= datetime.datetime.now()

# First day of this week (Monday)
today = datetime.datetime.now().date()
Monday = today - timedelta(days=today.weekday())
Monday = Monday.strftime("%m-%d-%Y")

# Day of the Week Today
now 	= datetime.datetime.now()
today 	= now.strftime("%A")

# Website URLS
byte_URL 	= "http://dining.guckenheimer.com/clients/npcholdings/fss/fss.nsf/weeklyMenuLaunch/9W4S24~" + Monday + "/$file/cafehome.htm"
cloud_URL 	= "https://legacy.cafebonappetit.com/weekly-menu/206683"
foodTruck_URL = "https://workday--simpplr.na6.visual.force.com/apex/Simpplr__SiteContent?origin=gs&searchTerm=food%20truck%20schedule#/site/a7x80000000003dAAA/page/a7t80000000D3LiAAK"
if dayOfWeek.strftime("%w") == 5: # On Fridays provide the Food Truck Mafia URL
	foodTruck_URL = "https://www.thefoodtruckmafia.com/upcoming"

# Other Variables
displayPrice = True
displayCals  = False

class slackBot():
	# Bot Login and Channel Details
	SLACK_TOKEN   = ""
	SLACK_CHANNEL = ""
	# Restaurant Titles
	byteTitle 	= "*Byte Café* <" + byte_URL 	 +	"|:cookies:>\n"
	truckTitle 	= "*Food Truck* <"+ foodTruck_URL +	"|:truck:>\n"
	cloudTitle 	= "*Cloud Café* <"+ cloud_URL 	 +	"|:cloud:>\n"

	def __init__(self):
		self.sc = SlackClient(self.SLACK_TOKEN)
		message = ""

	def botSendMessage(self):
		############ Send the Message to Slack as Bot ######################
		print("\nPosting in Channel: %s\n\nPOSTING...\n" %(self.SLACK_CHANNEL))
		self.sc.api_call(
			"chat.postMessage", channel=self.SLACK_CHANNEL, username="Mr. Bot",
			attachments=json.dumps(self.message),  icon_emoji=':robot_face:'	
		)

	def buildMessage(self):
		self.message = [
			{
				### Byte ###
				"fallback" 	: "Lunch Options for Today ("+date+")",
				"color" 	: "#00c0ff",
				#"pretext" : ":b:eep :b:oop Su:b:stitute :robot_face:\n*Lunch Options for Today ("+date+")*",
				"pretext" 	: ":b:eep :b:oop :robot_face:\n*Lunch Options for Today ("+date+")*",
				"text" 		: ""+self.byteTitle+byteScrapper.getByteFoods()+"",
				"footer" 	: "_*Breakfast:* 7:30AM - 10:00AM  *Lunch:* 11:00AM - 2:00PM_",
				"footer_icon" : ":robot_face:"
			},
			{
				### Food Truck ###
				"fallback" 	: "Info for Food Truck",
				"color" 	: "#f44646",
				#"text" 		: ""+self.truckTitle+"",
				"text" 		: ""+self.truckTitle+"",
				"footer" 	: "_Normally closes at 2:00PM_",
				"footer_icon" : ":robot_face:",
				"fields" 	: [
					{
						"value" : "_~*This is a Placeholder, not a real truck*~_",
						"short" : True
					}
				]
			},
			{
				### Cloud ###
				"fallback" 	: "Info for Cloud Cafe",
				"color" 	: "#3ba0bb",
				"text" 		: ""+self.cloudTitle+">>>",
				"fields" 	: [
					{
						"value" : ">>>*Breakfast* :bowl_with_spoon:" + str(cloudScraper.getCloudFoods("breakfast")) + "",
						"short" : True
					},
					{
						"value" : ">>>*Soup* :stew:"+ str(cloudScraper.getCloudFoods("soup")) +" *Ⓥ*",
						"short" : True
					},
					{
						"value" : ">>>*Global* :world_map:" + str(cloudScraper.getCloudFoods("global")) + "",
						"short" : True
					},
					{
						"value" : ">>>*Grill* :grill:"+ str(cloudScraper.getCloudFoods("grill")) +" *ⓋⓄ*",
						"short" : True
					},
					{
						"value" : ">>>*Wok* :fire:"+ str(cloudScraper.getCloudFoods("wok")) +"",
						"short" : True
					},
					{
						"value" : ">>>*Wok Sides* :smile:"+ str(cloudScraper.getCloudFoods("wokSides")) +"\n _*-*_ _*R i c e*_ Stuff\n _*- *_ Vegetable Stuff *ⓋⓄ*",
						"short" : True
					}
				],
				"footer" : "_*Breakfast:* 7:30AM - 10:00 AM  *Lunch:* 11:00AM - 2:00PM_",
			}
		]
	#def buildMessage(self):

	def buildMessageOriginal(self):
		byteText 			= self.byteTitle 			+ "" + byteScrapper.getByteFoods()
		truckText 			= self.truckTitle 			+ "_~*This is a Placeholder, not a real truck*~_\n\n"
		cloudTextSoup 		= ">*Soup* :stew:" 			+ str(cloudScraper.getCloudFoods("soup"))
		cloudTextGrill		="\n\n>*Grill* :grill: " 	+ str(cloudScraper.getCloudFoods("grill"))
		cloudTextGlobal		="\n\n>*Global* :world_map:"+ str(cloudScraper.getCloudFoods("global"))
		cloudTextWok		="\n\n>*Wok* :fire: " 		+ str(cloudScraper.getCloudFoods("wok"))
		cloudTextWokSides	="\n\n>*Wok Sides* :sideways_smile: " + str(cloudScraper.getCloudFoods("wokSides"))
		theText = ">>>" + byteText + "\n\n" + truckText + self.cloudTitle + cloudTextSoup + cloudTextGrill + cloudTextGlobal + cloudTextWok + cloudTextWokSides + ""
		
		# The Message should be formatted as follows
		##	>>>*Byte Café* :cookies:
		##	Taqueria! Serving Tacos, Burritos, Taco Salads and MORE!        

		##	*Food Truck* :truck:
		##	_~*This is a Placeholder, not a real truck*~_

		##	*Cloud Café* :cloud:
		##	>*Soup* :stew:
		##	> New England Style Clam Chowder _*($2.40)*_
		##	> Creamy Tomato Basil Soup _*($2.40)*_

		##	>*Grill* :grill:
		##	> Fennel and Orange Tilapia _*($7.50)*_

		##	>*Global* :world_map:
		##	> Beef and Pork Meatloaf _*($7.50)*_
		##	> Garbanzo and Tomato Stew _*($6.50)*_

		##	>*Wok* :fire:
		##	> Filipino Style Barbeque Chicken _*($7.50)*_
		##	> Vegetable Stew _*($6.50)*_

		##	>*Wok Sides* :sideways_smile:
		##	> Vegetable Pancit _*($2.50)*_
		##	> Wok Sides

		self.message = [
			{
				### Byte ###
				"fallback" 	: "Lunch Options for Today ("+date+")",
				#"pretext" : ":b:eep :b:oop Su:b:stitute :robot_face:\n*Lunch Options for Today ("+date+")*",
				"pretext" 	: ":b:eep :b:oop :robot_face:\n*Lunch Options for Today ("+date+")* \n" + theText + "",
			}
		]
	#def buildMessageOriginal(self):
#class slackBot():

class byteFoods():
	def __init__(self):
		self.byteItem1 = ""
	def scrapeByteFoods(self):
		# Open the page
		byte_Page = urlopen(byte_URL)
		soup = BeautifulSoup(byte_Page, 'html.parser')
		# Search for a "Strong" tag that contains the day of the week
		menu = soup.find_all('strong')
		for x in menu:
			if x.text.split(":")[0] == today:
				self.byteItem1 = x.text.split(":")[1][1:]
	def getByteFoods(self):
		return self.byteItem1

class cloudFoods():
	# Food Category IDs for HTML Scraping
	breakfastID	= "td-15121-"+ dayOfWeek.strftime("%w")
	soupID  	= "td-15182-"+ dayOfWeek.strftime("%w")
	grillID 	= "td-15132-"+ dayOfWeek.strftime("%w")
	globalID	= "td-15133-"+ dayOfWeek.strftime("%w")
	wokID 		= "td-15134-"+ dayOfWeek.strftime("%w")
	woksideID 	= "td-15183-"+ dayOfWeek.strftime("%w")
	foodIDs 	= [soupID, grillID, globalID, wokID, woksideID, breakfastID]

	# Strings Containing all food items for each category
	itemStrings		= ["","","","","",""]

	def __init__(self):
		self.scrapeCloudFoods
		
	def scrapeCloudFoods(self, URL, method):
		###########################################################
		# Loop through all Food Categories, and store the results #
		###########################################################
		# Open the page
		cloud_Page = urlopen(URL)
		thePage = BeautifulSoup(cloud_Page, 'lxml')
		for categoryID, numTimes in zip(self.foodIDs, range(0, len(self.foodIDs))):
			self.itemStrings[numTimes] = ""
			itemContainer = thePage.find('div', attrs={'id': categoryID})
			theFoods 	= itemContainer.find_all('span', attrs={'class': 'weelydesc'})
			theDetails 	= itemContainer.find_all('div', attrs={'class': 'menu-item'})

			#print(itemContainer.prettify())
			print("%s: %s" % (categoryID, len(list(theDetails))))
			#print(theDetails)

			print("===============================")
			print("=== Printing All %s HTML ===" % (categoryID))
			print("===============================")
			for item, details in zip(theFoods, theDetails):
				if method == "old":
					self.itemStrings[numTimes] += "\n> " + str(titlecase(item.text.capitalize()))
				else: 
					self.itemStrings[numTimes] += "\n_*-*_ " + str(titlecase(item.text.capitalize()))
				price = details.find('span', attrs={'class': 'font-size-90'})
				if (price) and (displayPrice):
					print(price.text)
					self.itemStrings[numTimes] += " _*($" + str(price.text) + ")*_"
				cals  = details.find('span', attrs={'class': 'well-being-kcal'})
				if cals and (displayCals):
					print(cals.text)
					self.itemStrings[numTimes] += " _*[" + str(cals.text.replace(' ', '')) + "]*_"
					

			print(self.itemStrings[numTimes])

	def getCloudFoods(self, which):
		foodGroupsIDs	= {'soup':0, 'grill':1, 'global':2, 'wok':3, 'wokSides':4, 'breakfast':5}
		print("This is the Which: %s" % (foodGroupsIDs[which]))
		print("This is the ID: %s" % (which))
		return str(self.itemStrings[foodGroupsIDs[which]])
#class cloudFoods():
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~ Begin Program  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
print("~~~~~~~~~~~~~~~~~~~~~~~~")
print("   Starting SlackBot!")
print("~~~~~~~~~~~~~~~~~~~~~~~~")
#############################################
## Initialize Classes
#############################################
byteScrapper = byteFoods()
cloudScraper = cloudFoods()
theBot = slackBot()

#############################################
## Scrape Cloud Cafe
#############################################
cloudScraper.scrapeCloudFoods(cloud_URL, "")

#############################################
## Scrape Byte Cafe
#############################################
byteScrapper.scrapeByteFoods()

#############################################
## Build and Send Slack Message with Bot (Nice Bot Formatted Layout that isn't possible as a user)
#############################################
#theBot.buildMessage()
#theBot.botSendMessage()

#############################################
## rescrape Cloud and put in old HanBot Format
#############################################
cloudScraper.scrapeCloudFoods(cloud_URL, "old")
theBot.buildMessageOriginal()
theBot.botSendMessage()