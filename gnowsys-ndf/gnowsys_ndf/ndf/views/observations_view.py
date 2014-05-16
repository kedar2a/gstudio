''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json, ast
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''

from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.templatetags.ndf_tags import group_type_info


#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]


def all_observations(request, group_id, app_id=None):

	app = collection.Node.find_one({"_id":ObjectId(app_id)})
	app_name = app.name
	app_collection_set = []

	for each in app.collection_set:

		app_set_element = collection.Node.find_one({'_id':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
		
		# app_element = collection.Node.find_one({"_id":each})
		if app_set_element:

			locs = len(app_set_element.location)
			locations = app_set_element.location

			# app_element_content_objects = collection.Node.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
			# obj_count = app_element_content_objects.count()
				
			app_collection_set.append({ 
									"id":str(app_set_element._id),
									"name":app_set_element.name,
									"locations": json.dumps(locations),
									"total_locations": locs
								  })

	# print "\napp_name : ", app_name, "\napp_set_id : ", app_set_id

	# print "\n app_collection_set : ", app_collection_set

    # if app_set_id:
    #     classtype = ""
    #     app_set_template = "yes"
    #     systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
    #     systemtype_name = systemtype.name
    #     title = systemtype_name
    #     if request.method=="POST":
    #         search = request.POST.get("search","")
    #         classtype = request.POST.get("class","")
    #         nodes = list(collection.Node.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [systemtype._id]}}))
    #     else :
    #         nodes = list(collection.Node.find({'member_of': {'$all': [systemtype._id]},'group_set':{'$all': [ObjectId(group_id)]}}))
    #     nodes_dict = []
    #     for each in nodes:
    #         nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})
    # else :
    #     app_menu = "yes"
    #     title = app_name

	# request.session.flush()
	request.session.set_test_cookie()

	return render_to_response("ndf/observations.html",
							 	{
							 		'app_collection_set': app_collection_set,
							 		'groupid':group_id, 'group_id':group_id,
							 		'app_name':app_name, 'app_id':app_id,
							 		'template_view': 'landing_page_view',
							 		'map_type': 'all_app_markers'
							 	},
							 	context_instance=RequestContext(request) 
							 )

def observations_app(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	client_ip = request.META['REMOTE_ADDR']
	request.session.set_test_cookie()

	# getting django user id
	user_id = int(request.user.id)  if request.user.id 	else request.session.set_expiry(0)
	user_name = unicode(request.user.username) if request.user.username  else "" # getting django user name
	

	app = collection.Node.find_one({"_id":ObjectId(app_id)})
	app_name = app.name
	app_collection_set = []

	for each in app.collection_set:

		app_set_element = collection.Node.find_one({'_id':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
		
		# app_element = collection.Node.find_one({"_id":each})
		if app_set_element:

			locs = len(app_set_element.location)
			locations = app_set_element.location
			# app_element_content_objects = collection.Node.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
			# obj_count = app_element_content_objects.count()
				
			app_collection_set.append({ 
									"id":str(app_set_element._id),
									"name":app_set_element.name,
									"locations": json.dumps(locations),
									"total_locations": locs
								  })

	
	# for each in app.collection_set:
		
	# 	app_element = collection.Node.ifnd_one({"_id":each})
	# 	obj_count = ""
	# 	if app_element:
	# 		app_element_content_objects = collection.Node.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
	# 		obj_count = app_element_content_objects.count()
				
	# 	app_collection_set.append({"id":str(app_element._id),"name":app_element.name, "obj_count": obj_count})

	return render_to_response("ndf/observations.html",
							 	{
							 		'app_collection_set': app_collection_set,
							 		'groupid':group_id, 'group_id':group_id,
							 		'app_name':app_name, 'app_id':app_id, 'app_set_id':app_set_id, 'app_set_name_slug':slug,
							 		'user_name':user_name, 'client_ip':client_ip,
							 		'template_view': 'app_set_view'
							 	},
							 	context_instance=RequestContext(request) 
							 )


def save_observation(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	user_type = request.POST["user"]
	user_session_id = request.POST["user_session_id"]
	marker_geojson = request.POST["marker_geojson"]
	marker_geojson = ast.literal_eval(marker_geojson)

	is_cookie_supported = request.session.test_cookie_worked()
	operation_performed = ""
	unique_token = str(ObjectId())

	app_set_element = collection.Node.find_one({'_id':ObjectId(app_set_id), 'group_set':{'$all': [ObjectId(group_id)]}})
	
	# to update existing location
	if "ref" in marker_geojson['properties']:
		marker_ref = marker_geojson['properties']['ref']

		if app_set_element:

			# for anonymous user
			anonymous_flag = False

			if (user_type == "anonymous" and is_cookie_supported):

				cookie_added_markers = request.session.get('anonymous_added_markers')

				if (cookie_added_markers != None) and (cookie_added_markers[:cookie_added_markers.find(",")] == user_session_id):
					if cookie_added_markers.find(marker_ref) > 0:
						anonymous_flag = True
					else:
						operation_performed = "You have not created this marker or you had lost your session !"
				else:
					operation_performed = "You have not created this marker or you are had lost your session !"
			else:
				operation_performed = "You have not created this marker or we think you had disabled support for cookies !"


			if (user_type == "authenticated") or anonymous_flag:
			
				for each in app_set_element.location:
					
					if each['properties']['ref'] == marker_ref:
						app_set_element.location.remove(each)
						app_set_element.location.append(marker_geojson)
						app_set_element.save()
						unique_token = marker_ref
						operation_performed = "edit"

	
	# to create/add new location
	else:

		marker_geojson['properties']['ref'] = unique_token

		if app_set_element:
			app_set_element.location.append(marker_geojson)
			app_set_element.save()
			operation_performed = "create_new"
			
		# for anonymous user
		if user_type == "anonymous" and is_cookie_supported:
			cookie_added_markers = request.session.get('anonymous_added_markers')

			if cookie_added_markers == None or cookie_added_markers[:cookie_added_markers.find(",")] != user_session_id:
				cookie_added_markers = user_session_id + "," + unique_token 

			elif cookie_added_markers[:cookie_added_markers.find(",")] == user_session_id:
				cookie_added_markers += "," + unique_token

			request.session['anonymous_added_markers'] = cookie_added_markers
	
	# print "\n create/save :  ", request.session.items()
			
	response_data = [len(app_set_element.location), unique_token, operation_performed]
	response_data = json.dumps(response_data)

	return StreamingHttpResponse(response_data)



def delete_observation(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	user_type = request.POST["user"]
	user_session_id = request.POST["user_session_id"]
	marker_geojson = request.POST["marker_geojson"]

	marker_geojson = ast.literal_eval(marker_geojson)
	marker_ref = marker_geojson['properties']['ref']

	is_cookie_supported = request.session.test_cookie_worked()
	operation_performed = ""

	app_set_element = collection.Node.find_one({'_id':ObjectId(app_set_id), 'group_set':{'$all': [ObjectId(group_id)]}})

	# for anonymous user
	anonymous_flag = False

	if (user_type == "anonymous" and is_cookie_supported):

		cookie_added_markers = request.session.get('anonymous_added_markers')

		if (cookie_added_markers != None) and (cookie_added_markers[:cookie_added_markers.find(",")] == user_session_id):
			if cookie_added_markers.find(marker_ref) > 0:
				anonymous_flag = True
			else:
				operation_performed = "You have not created this marker or you had lost your session !"
		else:
			operation_performed = "You have not created this marker or you had lost your session !"
	else:
		operation_performed = "You have not created this marker or we think you had disabled support for cookies !"


	if (user_type == "authenticated") or anonymous_flag:
			
		for each in app_set_element.location:
			
			if each['properties']['ref'] == marker_ref:
				app_set_element.location.remove(each)
				app_set_element.save()

				operation_performed = "marker_deleted"	

	response_data = [len(app_set_element.location), operation_performed]
	response_data = json.dumps(response_data)

	return StreamingHttpResponse(response_data)
