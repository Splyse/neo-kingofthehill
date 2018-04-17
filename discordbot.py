#!/usr/bin/env python3

"""
MIT License

Copyright 2018 Splyse Inc.

"""

import os
import sys
import signal
import logging
import functools
import asyncio
import binascii
from threading import Thread
from asgiref.sync import *

from neo.contrib.smartcontract import SmartContract
from neo.Network.NodeLeader import NodeLeader
from twisted.internet import reactor, task
from neo.Core.Blockchain import Blockchain, Events
from neo.SmartContract.StateReader import StateReader
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Settings import settings
from neocore.Cryptography.Crypto import Crypto
from neocore.UInt160 import UInt160

import discord

client = discord.Client()

DISCORD_TOKEN=''
CHANNEL_ID=''
smart_contract = SmartContract('2d838efcda02e9b6bc42ce21ce34acad14b58923')

@smart_contract.on_notify
def sc_notify(event):
    if len(event.event_payload):
        #print("***** got new notify payload {}".format(event.event_payload[0]))
        if event.event_payload[0].decode("utf-8") == 'new_king':
            address = event.event_payload[1]
            bounty = int(event.event_payload[2])
            newKingMessage = ''
            if len(event.event_payload[3]) > 0:
                name = event.event_payload[3].decode("utf-8", "ignore")
                newKingMessage = '{} is now king. Next bounty is {} TUT'.format(name, bounty / 100000000)
            else:
                newKingMessage = '{} is now king. Next bounty is {} TUT'.format(Crypto.ToAddress(UInt160(data=address)), bounty / 100000000)

            print(newKingMessage)
            send_message_sync(newKingMessage)


@async_to_sync
async def send_message_sync(message):
    client.wait_until_ready()
    if not client.is_closed:
        channel = discord.Object(id=CHANNEL_ID)
        await client.send_message(channel, message)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def do_quit():
    print('Shutting down.')
    Blockchain.Default().Dispose()
    reactor.stop()
    NodeLeader.Instance().Shutdown()
    sys.exit(0)


def signal_handler(signal, frame):
    do_quit()


def neo_loop():
    settings.setup_testnet()
    blockchain = LevelDBBlockchain(settings.chain_leveldb_path)
    Blockchain.RegisterBlockchain(blockchain)
    print("PersistBlocks task starting")
    dbloop = task.LoopingCall(Blockchain.Default().PersistBlocks)
    dbloop.start(.01)

    print("Node task starting")
    NodeLeader.Instance().Start()
    
    print("Entering main reactor loop")
    reactor.run(installSignalHandlers=False)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)

    print("Starting Neo thread")
    t = Thread(target=neo_loop)
    t.start()

    client.run(DISCORD_TOKEN)
    loop.run_forever()


if __name__ == "__main__":
    main()
