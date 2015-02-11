''' -- imports from python libraries -- '''
import os
import csv
import json
# import ast
import datetime
import urllib2
import hashlib
import magic
import subprocess
# import mimetypes
from PIL import Image
from StringIO import StringIO
import io
import time
import re
''' imports from installed packages '''
from django.core.management.base import BaseCommand
# from django.core.management.base import CommandError
from django.contrib.auth.models import User
# from django.http import Http404
from django.template.defaultfilters import slugify

from django_mongokit import get_database
from mongokit import IS

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
''' imports from application folders/files '''

from gnowsys_ndf.settings import GAPPS
# from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES
from gnowsys_ndf.ndf.models import Node, File
from gnowsys_ndf.ndf.models import GSystemType, AttributeType, RelationType
from gnowsys_ndf.ndf.models import GSystem, GAttribute, GRelation
# from gnowsys_ndf.ndf.management.commands.data_entry import create_grelation, create_gattribute
from gnowsys_ndf.ndf.org2any import org2html
# from gnowsys_ndf.ndf.views.file import save_file, getFileSize
from gnowsys_ndf.ndf.views.methods import create_grelation, create_gattribute

##############################################################################


SCHEMA_ROOT = os.path.join(os.path.dirname(__file__), "schema_files")

log_list = []  # To hold intermediate errors
log_list.append("\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################\n")

collection = get_database()[Node.collection_name]
file_gst = collection.GSystemType.one({"name": "File"})
home_group = collection.Group.one({"name": "home", "_type": "Group"})
theme_gst = collection.GSystemType.one({"name": "Theme"})
theme_item_gst = collection.GSystemType.one({"name": "theme_item"})
topic_gst = collection.GSystemType.one({"name": "Topic"})
GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3], '_type': 'GSystemType'})
gsystem_type_name = ""
collection.MetaType() 
collection.Node.one({"_type": u"MetaType", "name": u"wordnet"}) 
# create_meta_type(meta_type)
# metatype_yago_wordnet = collection.Node.find({"_type": "MetaType", "$or":[{"name": "yago"}, {"name": "wordnet"}] })
meta_type_yago = collection.Node.one({"_type": "MetaType", "name" : "yago"})
user_id = 1



def create_meta_type(meta_type_name):

  '''
  Creating meta_type in database
  '''
  a = collection.MetaType()
  a.name = unicode(meta_type_name)
  a.created_by = user_id 
  a.modified_by = user_id
  
  a.contributors = [user_id]
  a.status = u"PUBLISHED"
  a.save() 
  print "succesfully created META_TYPE:",meta_type_name 

if not meta_type_yago:
	# create_meta_type("yago") 
    print "not meta_type_yago"

meta_type_wordnet = collection.Node.one({"_type": "MetaType", "name" : "wordnet"})

if not meta_type_wordnet:
    # create_meta_type("wordnet")
    # meta_type_wordnet = collection.Node.one({"_type": "MetaType", "name" : "wordnet"})
    print "not meta_type_yago"


def create_gsystem_type(gsystem_type_name, tags = None, type_of_id = None):

  '''
  Creating gsystem_type in database
  '''
  a = collection.GSystemType()
  a.name = unicode(gsystem_type_name)
  a.created_by = user_id 
  a.modified_by = user_id
  a.member_of = [meta_type_wordnet._id]
  if tags:
  	a.tags = tags
  if type_of_id:
  	a.type_of = type_of_id
  
  a.contributors = [user_id]
  a.status = u"PUBLISHED"
  #a.save() 
  #print "succesfully created GSYSTEM_TYPE:",gsystem_type_name 
  return a._id




  
class Command(BaseCommand):
    help = "\n\tFor saving data in gstudio DB from NROER schema files. This will create 'File' type GSystem instances.\n\ttsv file condition: The first row should contain DB names.\n"
 
    def handle(self, *args, **options):
        try:
            print "working........" + SCHEMA_ROOT

            # processing each file of passed multiple tsv files as args
            for file_name in args:
                file_path = os.path.join(SCHEMA_ROOT, file_name)
                global gsystem_type_name
                global gsytem_type_id

                if os.path.exists(file_path):

                    file_extension = os.path.splitext(file_name)[1]

                    if "tsv" in file_extension:                        

                        # Process tsv file and convert it to json format at first
                        info_message = "\n- tsv File (" + file_path + ") found!!!"
                        print info_message
                        log_list.append(str(info_message))
                						    
                        try:
                            tsv_file_path = file_path
                            json_file_name = file_name.rstrip("tsv") + "json"
                            json_file_path = os.path.join(SCHEMA_ROOT, json_file_name)
                            json_file_content = ""

                            with open(tsv_file_path, 'rb') as tsv_file:
                                tsv_file_content = csv.DictReader(tsv_file, delimiter="\t")
                                json_file_content = []

                                for row in tsv_file_content:
                                    json_file_content.append(row)

                            with open(json_file_path, 'w') as json_file:
                                json.dump(json_file_content, json_file, indent=4, sort_keys=False)
                            
                            if os.path.exists(json_file_path):
                                file_path = json_file_path
                                is_json_file_exists = True
                                info_message = "\n- JSONType: File (" + json_file_path + ") created successfully.\n"
                                print info_message
                                log_list.append(str(info_message))

                        except Exception as e:
                            error_message = "\n!! tsv-JSONError: " + str(e)
                            print error_message
                            log_list.append(str(error_message))
                            # End of tsv-json coversion

                    elif "json" in file_extension:
                        is_json_file_exists = True

                    else:
                        error_message = "\n!! FileTypeError: Please choose either 'tsv' or 'json' format supported files!!!\n"
                        print error_message
                        log_list.append(str(error_message))
                        raise Exception(error_message)

                    if is_json_file_exists:
                        # Process json file and create required GSystems, GRelations, and GAttributes
                        info_message = "\n------- Task initiated: Processing json-file -------\n"
                        print info_message
                        log_list.append(str(info_message))

                        parse_data_create_gsystem(file_path)
                        
                        # End of processing json file

                        info_message = "\n------- Task finised: Successfully processed json-file -------\n"
                        print info_message
                        log_list.append(str(info_message))
                        # End of creation of respective GSystems, GAttributes and GRelations for Enrollment
                        
                else:
                    error_message = "\n!! FileNotFound: Following path (" + file_path + ") doesn't exists!!!\n"
                    print error_message
                    log_list.append(str(error_message))
                    raise Exception(error_message)

        except Exception as e:
            print str(e)
            log_list.append(str(e))

        finally:
            if log_list:

                log_list.append("\n =====================================\
                    ======================= End of Iteration ============\
                    ================================================\n")
                # print log_list
                log_file_name = args[0].rstrip("tsv") + "log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                # print log_file_path
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)

  # --- End of handle() ---

def parse_data_create_gsystem(json_file_path):
    json_file_content = ""
    
    try:
        with open(json_file_path) as json_file:
            json_file_content = json_file.read()

        json_documents_list = json.loads(json_file_content) 
        #if "ST" in json_file_path: 
        	#for json_document in json_documents_list: 
        	# Process data in proper format
        	#try: 
        		#json_document['name'] = unicode(json_document['name']) 
        		#perform_eval_type("type_of", json_document, type_name, "GSystemType") 
        		#perform_eval_type("member_of", json_document, type_name, "MetaType")
                #perform_eval_type("attribute_type_set", json_document, type_name, "AttributeType")
                #perform_eval_type("relation_type_set", json_document, type_name, "RelationType")
                #perform_eval_type("collection_set", json_document, type_name, "GSystemType")

            #except Exception as e:
            #error_message = "\n While parsing "+type_name+"(" + json_document['name'] + ") got following error...\n " + str(e)
            #log_list.append(error_message)
            #print error_message # Keep it!
        # continue

        # Process data in proper format
        node = collection.GSystem()
        node_keys = node.keys()
        node_structure = node.structure

        json_documents_list_spaces = json_documents_list
        json_documents_list = []

        # Removes leading and trailing spaces from keys as well as values
        for json_document_spaces in json_documents_list_spaces:
            json_document = {}

            for key_spaces, value_spaces in json_document_spaces.iteritems():
                json_document[key_spaces.strip().lower()] = value_spaces.strip()
                
            json_documents_list.append(json_document)
            # print "json_documents_list :", json_documents_list
            
    except Exception as e:
        error_message = "\n While parsing the file ("+json_file_path+") got following error...\n "
        log_list.append(error_message)
        raise error_message

    for i, json_document in enumerate(json_documents_list):

        print "json_document : ", json_document
      
        info_message = "\n\n\n********** Processing row number : ["+ str(i)+ "] **********"
        print info_message
        log_list.append(str(info_message))

        try:
            
            parsed_json_document = {}
            attribute_relation_list = []
            is_wikicategory = False
            temp_wiki_tag = temp_type_of_id = yago = ""

            if json_document.has_key("id"): 
            	temp_value = json_document["id"]
                temp_value = temp_value.strip()
                #temp_value = temp_value.split("_")
                temp_process = temp_value[:-1]
                temp_process = temp_process[1:] 
                #if temp_value.split("_")[0] == "wikicategory":
                # do this
                #elif temp_process.split("_")[0] == "wordnet": 
                # do this 
                print temp_process
            	#print "id", json_document["id"] 
                yago = json_document["id"] + " "

            if json_document["wikicategory_wordnet"]:
                #if re.match("wiki_category_wordnet",json_document):
                #print "wikicategory", json_document["wikicategory_wordnet"]
                # yago += json_document["wikicategory_wordnet"] + " "
                #temp_value1 = temp_value1.split("_")
                temp_value1 = json_document["wikicategory_wordnet"]

                temp_value1 = temp_value1.strip()
                #temp_value1 = temp_value1.split("_")
                temp_process1 = temp_value1[:-1]
                temp_process1 = temp_process1[1:] 
                print "wikicategory_wordnet : ", temp_process1
                
                if temp_process1.split("_")[0] == "wikicategory":
                	is_wikicategory = True
                	temp_wiki_tag = temp_process1.partition("_")[2]
                  # print "wikicategory"
                elif temp_process1.split("_")[0] == "wordnet":
                    is_wikicategory = False
                    gsystem_type_name = temp_process1.partition("_")[2]
                    gsystem_type_name = temp_process1.rpartition("_")[0]
                    #temp_type_of_id = create_gsystem_type(gsystem_type_name)

                    print "wordnet" , gsystem_type_name
                #yago = json_document["wikicategory_wordnet"] + " " 
                
            if json_document["wordnet"]: 
                temp_value2 = json_document["wordnet"]
                temp_value2 = temp_value2.strip()
                #temp_value2 = temp_value.split("_")
                temp_process2 = temp_value2[:-1]
                temp_process2 = temp_process2[1:]
                temp_process2 = temp_process2.partition("_")[2]
                wordnet_gst_name = temp_process2.rpartition("_")[0]
                temp_list = []
                if is_wikicategory: 
                    temp_list.append(temp_wiki_tag)
                    # create_gsystem_type(wordnet_gst_name, temp_wiki_tag)
                else: 
                    temp_list.append(temp_type_of_id)
                    # create_gsystem_type(wordnet_gst_name, temp_type_of_id)

                print "wordnet : ", temp_process2

                #print "wordnet", json_document["wordnet"]
                yago += json_document["wordnet"] + " "

            if json_document["sub_class"]: 
                print "sub_class", json_document["sub_class"] 
                yago += json_document["sub_class"] + " "
		
            info_message = "\n------- Task finised: Parsing done Successfully -------\n"
            print info_message
            log_list.append(str(info_message))

        except Exception as e:
	        error_message = "\n While creating ("+str(json_document['name'])+") got following error...\n " + str(e)
	        print error_message # Keep it!
	        log_list.append(str(error_message))
                

  
       
    

