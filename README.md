# Gazelle Database

Akseli Palén
Infant Cognition Laboratory
University of Tampere

## Install

    $ virtualenv gazelledb
    $ cd gazelledb
    $ source bin/activate
    (env)$ pip install Flask
    (env)$ pip install pymongo
    (env)$ pip install numpy

## Run

    $ cd project/root/path
    $ mongod --dbpath data/mongodb

    (env)$ python gazelledb/server.py

Optionally you can also open Mongo console:

    $ mongo
