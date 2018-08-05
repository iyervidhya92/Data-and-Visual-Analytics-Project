#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, url_for
import flask
from flask_login import LoginManager, login_user, login_required
# from flask.ext.sqlalchemy import SQLAlchemy
# import logging
# from logging import Formatter, FileHandler
from forms import *
from user import User
import os
import json

import geojson
from geopy import distance
from shapely import geometry
import pandas as pd
import numpy as np

from sklearn.cluster import KMeans

from googleplaces import GooglePlaces, types, lang

adjacency_df = pd.read_csv("adjacency.txt",skipinitialspace=True)

def findPlaces(coord,time):
    time = time*100
    day = 'Monday'
    coor = {'lat':coord[1], 'lng':coord[0]}
    #takes in coor as a dict with 2 fields, 'lat' and 'lng', time as an int in 24 hour time, and day as a string
    time=int(time) # just in case
    week={'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
    week_key=week[day] # converts to value used by google API output
    API_Key='AIzaSyAhBLfamR61QMJyemNPMyI2CY1Jzy2OJVo' # should sub out
    google_places=GooglePlaces(API_Key) 
    if 0600 < time < 2000:
        query_result=google_places.nearby_search(lat_lng=coor,radius=100,types=[types.TYPE_RESTAURANT]) # only looks for restaurants
    else:
        query_result=google_places.nearby_search(lat_lng=coor,radius=100,types=[types.TYPE_BAR])
    if query_result.has_attributions:
        print query_result.html_attributions

    best_rated_open=''
    curr_best_rate=0
    coor_best_open=[]
    print len(query_result.places)
    for place in query_result.places:
        place.get_details()
        #print place.name
        #print place.rating
        #if ~hasattr(place,'details'):
        #   continue
    
        #   print place.details['opening_hours']
        if not('opening_hours' in place.details):
            continue
        else:
            hours=place.details['opening_hours']
            hours=hours['periods']
            open_time=0000; # set defaults in case info is missing for a place
            close_time=0000;
            for h in hours:
                if h['open']['day'] == week_key: #finds the open/close times for the specified day
                    if len(h)>1:
                        open_time=int(h['open']['time'])
                        close_time=int(h['close']['time'])
                        break
        #if len(hours[0])>1:
        #   if int(hours[0]['open']['time']) <= time < int(hours[0]['close']['time']):
            if open_time <= time < close_time:
                if place.rating > curr_best_rate:
                        #print 'Made it!'
                        curr_best_rate=place.rating
                        coor_best_open=place.geo_location
                        best_rated_open=place

    #print best_rated_open
    #print coor_best_open
    if best_rated_open=='': # if no valid results, output the original coordinates
        return [coord, '--']

    # return best_rated_open # object with all data stored. See notes at bottom for full list
    return [[float(best_rated_open.geo_location['lng']),float(best_rated_open.geo_location['lat'])], best_rated_open.name]

def black_box_route_finder(NO_OF_BUSES,MAX_ADD_PICKUPS,MAX_TOTAL_EDGES,WEIGHT, HOD , CONGESTION_THRESHOLD, Adjacency_df):

######Details of Parameters######

#NO_OF_BUSES = Total number of buses 
#MAX_ADD_PICKUPS = max number of additional close by (adjacent) pick ups allowed before servicing first destination
#MAX_TOTAL_EDGES = total congested edges that will be serviced / hour of day 
#WEIGHT = weight for choosing representative point for clustering
#HOD = hod for which the routes are being generated 
#CONGESTION_THRESHOLD = sigma/mu limit to be called congested
#LIST_OF_BUS_ROUTES is a dictionary returned where each element is a bus route in the form of a list


    LIST_OF_BUS_ROUTES = {}
##Loading geojson file and getting lat-long for each zone
    with open("san_francisco_taz.json") as f:
        gj = geojson.load(f)
        
   
    my_centroid_long = {}
    my_centroid_lat = {}

    for feature in gj['features'] :
        coordinate_list = list(geojson.utils.coords(feature) )   
        mypolygon = geometry.Polygon(coordinate_list)
        long = mypolygon.centroid.x
        lat = mypolygon.centroid.y
        my_centroid_long[int(feature.properties['MOVEMENT_ID'])] = long
        my_centroid_lat[int(feature.properties['MOVEMENT_ID'])] = lat
       
    hourly_file = "Test/test" +str(HOD)+".csv"
    # print(hourly_file)
    Data_Frame = pd.read_csv(hourly_file,skipinitialspace=True)

    Data_Frame['source_centroid_long'] = Data_Frame['sourceid'].map(my_centroid_long)
    Data_Frame['source_centroid_lat'] = Data_Frame['sourceid'].map(my_centroid_lat)
    Data_Frame['destination_centroid_long'] = Data_Frame['dstid'].map(my_centroid_long)
    Data_Frame['destination_centroid_lat'] = Data_Frame['dstid'].map(my_centroid_lat)
    Data_Frame['edge_long_effective'] = Data_Frame['dstid'].map(my_centroid_lat)
    Data_Frame['edge_lat_effective'] = Data_Frame['dstid'].map(my_centroid_lat)

    Data_Frame['edge_long_effective'] = Data_Frame['source_centroid_long'] + (Data_Frame['destination_centroid_long'] - Data_Frame['source_centroid_long'] )*WEIGHT
    Data_Frame['edge_lat_effective'] = Data_Frame['source_centroid_lat'] + (Data_Frame['destination_centroid_lat'] - Data_Frame['source_centroid_lat'] )*WEIGHT
    Data_Frame = Data_Frame.dropna()

    edge_id = []
    # count = 0

    Data_Frame['long_lat_node_source'] = list(zip(Data_Frame.source_centroid_long, Data_Frame.source_centroid_lat))
    Data_Frame['long_lat_node_dest'] = list(zip(Data_Frame.destination_centroid_long, Data_Frame.destination_centroid_lat))
    Data_Frame['congested']= (Data_Frame['standard_deviation_travel_time']/Data_Frame['mean_travel_time'] >=CONGESTION_THRESHOLD)
    
    ###Filtering based on hod selected and congestion
    Data_Frame = Data_Frame[ (Data_Frame['hod'] == HOD) ]
    Data_Frame = Data_Frame[ Data_Frame['congested'] ]

    # for row in Data_Frame['sourceid']:
    #     edge_id.append(count)
    #     count= count + 1
    # edge_id = 
    # Data_Frame.assign(0, 'edge_id', range(len(df)))
    Data_Frame['edge_id'] = range(len(Data_Frame))

        
#####KMeans clustering
    # Data_Frame['edge_id'] = edge_id
    df = Data_Frame.values
    #X_train = np.array(scale(df.data))
    new = Data_Frame.filter(['edge_long_effective','edge_lat_effective'], axis=1)
    X_train = new.values
    k_means = KMeans(n_clusters=NO_OF_BUSES)
    k_means.fit(X_train)
    Data_Frame['route_labels'] = (k_means.labels_)
  
    for cluster in range(NO_OF_BUSES):
        Busi = Data_Frame.loc[Data_Frame['route_labels'] == cluster]
        points  = list(Busi.long_lat_node_source)
        points1  = list(Busi.long_lat_node_dest)
        points.extend(points1)

        points  = (np.asarray(points))

        edges = []
        for i in range(len(points1)) :
            edges.append([i,i+len(points1)])
        edges = np.array(edges)
        x = points[:,0].flatten()
        y = points[:,1].flatten()
        thisClusterX = x[edges.T]
        thisClusterY = y[edges.T]

    ###################Route Planning Bus#########################
    
    
    for cluster in range(NO_OF_BUSES):
        Busi = Data_Frame.loc[Data_Frame['route_labels'] == cluster]
        backup_Bus = Busi
        route_bus_i = []
        edge_list = []
        edge1 = []
        Busi['Flag'] = 0


        for itr1 in range(Busi.shape[0]) :
            source_arr = []
            target_arr = []
            
            if(len(route_bus_i) == MAX_TOTAL_EDGES) :
                break
            
            
            if(Busi.iloc[itr1]['Flag'] != 1) :
                source1 = Busi.iloc[itr1]['sourceid']
                dst1 = Busi.iloc[itr1]['dstid']
                edge1 = Busi.iloc[itr1]['edge_id']
                
                source_arr.append(Busi.iloc[itr1]['long_lat_node_source'])
                target_arr.append(Busi.iloc[itr1]['long_lat_node_dest'])
                edge_list.append(edge1)
                Busi.iloc[itr1, Busi.columns.get_loc('Flag')] = 1
                count = 0
                for itr2 in range(Busi.shape[0]) :
                    edge2 = Busi.iloc[itr2]['edge_id']
                    source2 = Busi.iloc[itr2]['sourceid']
                    dst2 = Busi.iloc[itr2]['dstid']

                    if(edge1 != edge2 and Busi.iloc[itr2]['Flag'] != 1 ):
                        if (Adjacency_df.iloc[int(source1)][int(source2)] == "TRUE"):
                            count = count + 1
                            source_arr.append(Busi.iloc[itr2]['long_lat_node_source'])
                            target_arr.append(Busi.iloc[itr2]['long_lat_node_dest'])
                            Busi.iloc[itr2, Busi.columns.get_loc('Flag')] = 1
                            edge_list.append(edge2)
                            #Remove the used ones
                            if(count  == MAX_ADD_PICKUPS) :
                                break
            source_arr.extend(target_arr)
            route_bus_i.extend(source_arr)
            
        arr_list = []    
        arr_list.append(findPlaces(route_bus_i[0],HOD))
        a_last = route_bus_i[0]


        ##Remove two points in the route < 1.5 km apart)
        for i in range(len(route_bus_i)):
            a_curr = route_bus_i[i]
            if(distance.vincenty(a_curr, a_last).km >1.5):
                # arr_list.append(a_curr)
                arr_list.append(findPlaces(a_curr,HOD))
                print findPlaces(a_curr,HOD)
                a_last = a_curr

                

        route_bus_i = arr_list
        LIST_OF_BUS_ROUTES[cluster] = (route_bus_i)

    return(LIST_OF_BUS_ROUTES)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
valid_users = ['nikhil.soraba@gatech.edu', 'gszalkowski3@gatech.edu', 'swagatadutta093@gmail.com', 'vidhyaviji92@gmail.com']

app = Flask(__name__)
app.config.from_object('config')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/home.html')


@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.name.data not in valid_users or form.password.data != 'team24':
            error = 'Invalid Credentials. Please try again.'
        else:
            # return redirect(url_for('home'))

            # Login and validate the user.
            # user should be an instance of your `User` class

            user = User(form.name.data)
            user.set_authenticated()
            login_user(user)

            flask.flash('Logged in successfully.')

            return flask.redirect(flask.url_for('viz'))
    return flask.render_template('forms/login.html', form=form, error=error)

@app.route('/dashboard')
# @login_required
def viz():
   return flask.render_template('pages/dashboard.html')

@app.route('/data/<int:noBuses>/<int:time>')
def data(noBuses,time):
    json_data = black_box_route_finder(noBuses,5,12,0.75,time, 1.5, adjacency_df)
    return json.dumps(json_data)

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    # print findPlaces([-84.3963,33.7756],1100)
    app.run()
