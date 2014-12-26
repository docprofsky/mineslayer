import sys

import logging
import time
import math
from math import atan2, degrees

import socketIO_client
import random

from functools import partial
import datetime


class ninjanodeClient:

    """
    Contains all the stuff needed for socketIO and a few random other things
    """

    # logging.basicConfig(level=logging.DEBUG)    #ENABLE THIS AT YOUR OWN
    # RISK!!! FLOODS THE CONSOLE WITH ALL TRANSMITTED/RECIEVED PACKETS!

    # Set to true to enable automatic reconnection after a disconnect
    reconnect = True
    # stores wether the bot is enabled or not. This will set the default state
    # when it first logs on
    attack = True
    updates = True  # if this is true, then we say statistics ingame

    # This is true if this is the first time connecting to the server
    firstConnect = False
    projectiles = {}  # dict storing all data about projectiles


    def __init__(self, name):
        # list that stores a log of all the chat events that have happened.
        self.chatLog = []
        pnbData = {}  # dict storing planet data
        playerDat = {'d': 0}  # dict storing all data about players

        self.sio = socketIO_client.SocketIO(
            'ninjanode.tn42.com', 80, self.EventHandler)
        self.sio.timeout_in_seconds = 0.001
        self.ShipInfo = {'status': "create",
                         'name': name,
                         'style': "c"}

    def on_chat(self, data):  # when new data arrives from the chat system
        chatLog.append(data)  # add that data to the que

    def on_shipstat(self, data):  # recieved info on ships
        for k in data.keys():  # iterate through keys in recv'd data

            if self.playerDat.has_key(k):
                # if the player is already in the system, only overwrite
                # the changes
                self.playerDat[k].update(data[k])
            else:
                self.playerDat[k] = data[k]  # otherwise, overwrite it all!
            # If the player needs tobe removed from memory
            if data[k]['status'] == 'destroy':
                self.playerDat.pop(k)

    def on_projstat(self, data):  # updates on projectiles status
        for k in data.keys():
            # if the projectile is being created
            if data[k]['status'] == 'create':
                if projectiles.has_key(k):
                    # if the projectile is already in the system, only
                    # overwrite the changes
                    projectiles[k].update(data[k])
                else:
                    # otherwise, overwrite it all!
                    projectiles[k] = data[k]
            else:
                projectiles.pop(k)  # If we're not creating it, destroy it!

    def on_projpos(self, data):  # on position update of projectiles
        for k in data.keys():  # write new data to the dict
            projectiles[k].update(data[k])

    # This is only called once, on login, it gives data on PNBITS
    def on_pnbitsstat(self, data):
        self.pnbData = data  # just copy the data

    def getClosest(self, coord, projectiles):
        """
        returns closest coordinate to a coordinate (coord) from the list of coordinates (projectiles)
        """
        dist = lambda s, d: (s[0] - d[0]) ** 2 + (s[1] - d[
            1]) ** 2  # a little function which calculates the distance between two coordinates
        pos = []  # clear the local list of positions
        for k in projectiles.keys():
            if projectiles[k].has_key('cssClass'):  # if this is a planet
                # add the coordinates in a (0,0) fashion
                pos.append(
                    (200 - int(-projectiles[k]['pos']['x'] / 50), 200 - int(-projectiles[k]['pos']['y'] / 50)))
            elif projectiles[k]['weaponID'] == 1:  # or if this is a mine
                # add the coordinates in a (0,0) fashion
                pos.append(
                    (200 - int(-projectiles[k]['pos']['x'] / 50), 200 - int(-projectiles[k]['pos']['y'] / 50)))
        try:
            return min(pos, key=partial(dist, coord))
        except ValueError:
            return coord

    def GetName(self, key):
        try:
            return playerDat[key]['name']
        except:
            return ''

    def GetKey(self, name):
        try:
            for k in playerDat.keys():
                if playerDat[k]['name'] == name:
                    return k
        except BaseException as er:
            return ''

    def Connect(self):
        self.sio.emit('shipstat', self.ShipInfo)
        self.sio.wait(0.001)
        self.firstConnect = True

    def MoveForward(self, state):
        self.sio.emit('key', {'s': int(state), 'c': "u"})
        self.sio.wait(0.001)

    def MoveBackward(self, state):
        self.sio.emit('key', {'s': int(state), 'c': "d"})
        self.sio.wait(0.001)

    def MoveLeft(self, state):
        self.sio.emit('key', {'s': int(state), 'c': "l"})
        self.sio.wait(0.001)

    def MoveRight(self, state):
        self.sio.emit('key', {'s': int(state), 'c': "r"})
        self.sio.wait(0.001)

    def DropMine(self):
        self.sio.emit('key', {'s': 1, 'c': "s"})
        self.sio.wait(0.001)
        self.sio.emit('key', {'s': 0, 'c': "s"})
        self.sio.wait(0.001)

    def Fire(self):
        self.sio.emit('key', {'s': 1, 'c': "f"})
        self.sio.wait(0.001)
        self.sio.emit('key', {'s': 0, 'c': "f"})
        self.sio.wait(0.001)

    def MoveDegrees(self, deg, state):
        self.sio.emit('key', {'c': 'm',
                              's': state,
                              'd': deg})
        self.sio.wait(0.001)

    def ChatSend(self, msg):
        self.sio.emit('chat', {'msg': str(msg)})
        self.sio.wait(0.001)

    class EventHandler(socketIO_client.BaseNamespace):

        """
        Handles events from socketIO
        """

        def on_connect(self):
            # When we connect to the server. Simply print a debug message to
            # console
            print "connected."

        def on_disconnect(self):
            print "DISCONNECTED!"  # When we get forcefully disconnected.
            if reconnect:  # if we want to reconnect, try it
                client.Connect()

        # wheb we recieve new information about player positions
        def on_pos(self, data):
            # iterate through all the keys in the rcieved data
            for k in data.keys():
                if self.playerDat.has_key(k):
                    # if the player is already in the system, only overwrite
                    # the changes
                    self.playerDat[k]['pos'].update(data[k])
                else:
                    # otherwise, overwrite it all!
                    self.playerDat[k]['pos'] = data[k]

        def on_chat(self, data):  # when new data arrives from the chat system
            chatLog.append(data)  # add that data to the que

        def on_shipstat(self, data):  # recieved info on ships
            global playerDat  # globalize all the things!

            for k in data.keys():  # iterate through keys in recv'd data

                if playerDat.has_key(k):
                    # if the player is already in the system, only overwrite
                    # the changes
                    playerDat[k].update(data[k])
                else:
                    playerDat[k] = data[k]  # otherwise, overwrite it all!
                # If the player needs tobe removed from memory
                if data[k]['status'] == 'destroy':
                    playerDat.pop(k)

        def on_projstat(self, data):  # updates on projectiles status
            for k in data.keys():
                # if the projectile is being created
                if data[k]['status'] == 'create':
                    if projectiles.has_key(k):
                        # if the projectile is already in the system, only
                        # overwrite the changes
                        projectiles[k].update(data[k])
                    else:
                        # otherwise, overwrite it all!
                        projectiles[k] = data[k]
                else:
                    projectiles.pop(k)  # If we're not creating it, destroy it!

        def on_projpos(self, data):  # on position update of projectiles
            for k in data.keys():  # write new data to the dict
                projectiles[k].update(data[k])

        # This is only called once, on login, it gives data on PNBITS
        def on_pnbitsstat(self, data):
            global pnbData
            pnbData = data  # just copy the data into a global variable
