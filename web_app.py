#imports
import os
import cherrypy
import redis
from jinja2 import Environment, FileSystemLoader
import operator
import script

#Load jinja2 environment
env = Environment(loader=FileSystemLoader('media'))

class HomePage:
	'''
	Serves home page.
	'''
	@cherrypy.expose
	def index(self, search=""):
		#Get index.html page using jinja.
		tmpl = env.get_template('index.html')

		#Get list of 10 gainers.
		self.gainers = []
		#Get all keys with the specific pattern from redis database.
		for key in r.scan_iter("gain:*"):
			#Get code from key in redis database.
			code = r.get(key)
			#Get dictionary and append to list.
			self.gainers.append(r.hgetall(code).copy())

		#Sort list using percentage gained.
		self.gainers.sort(key=operator.itemgetter('PERCENTAGE'), reverse = True)



		self.searchItems = []
		if search != "":
			search = search.upper().strip()
			#Get all keys with the search string from redis database.
			for key in r.scan_iter("equity:"+search+"*"):
				#Get code from key in redis database.
				code = r.get(key)
				#Get dictionary and append to list.
				self.searchItems.append(r.hgetall(code).copy())

		#Get last updated string from redis database.
		self.last_updated = r.get("latest")
		return tmpl.render(gainers = self.gainers, search = self.searchItems, last_updated = self.last_updated)



#Config info for cherrypy.
config = {'global': {'server.socket_host':  '127.0.0.1',
                     'server.socket_port':  int(os.environ.get('PORT', '8000'))},
          '/favicon.ico': {'tools.staticfile.on':       True,
                           'tools.staticfile.filename': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'favicon.ico')}}


if os.environ.get("REDIS_URL") :
	redis_url = os.environ.get("REDIS_URL")
else:
	redis_url = "localhost"        
r = redis.from_url((redis_url), charset="utf-8", decode_responses=True)
#Initiate link to redis database.
# r = redis.from_url(os.environ.get("REDIS_URL"), charset="utf-8", decode_responses=True)

if __name__ == '__main__':
	#creating csv file and seeting db
	script.setting_data()
	#Start Cherrypy server.
	cherrypy.quickstart(HomePage(), config=config)