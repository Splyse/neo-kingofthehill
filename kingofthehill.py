"""
TUT King of the Hill Example
===================================

Author: Joe Stewart
Email: hal0x2328@splyse.tech

Date: Apr 9 2018

This code demonstrates sending and receiving of Testnet Utility Tokens
(TUT) by a smart contract. The contract is triggered by sending some
TUT to the contract's address from any wallet that supports NEP-5 
tokens. No other off-chain code is required to play the game - it is 
a dApp that exists solely as a smart contract that can push supported
NEP-5 tokens to different players based on events that happen in the
game. Game watchers only need a wallet capable of receiving blockchain 
notifications (e.g. neo-python or neo-gui-developer).

The TUT contract's transfer() operation will dynamically execute this 
contract's onTokenTransfer() operation, which will run the main code
of the demo. The called contract can reject the transfer by returning 
False from onTokenTransfer().

When a contract wants to send tokens that it holds to another contract
or user, the TUT contract will invoke the tokenVerification() operation
which will return True if the transfer should be allowed.

King of the Hill is a simple game where a user sends tokens to contract
and if the amount exceeds the current bounty, the sender will become 
"king of the hill". If there is an existing king, that king will be 
replaced and the tokens they paid to the contract will be refunded.

Eventually one king will remain as ruler of all until the owner resets
the game by sending a low bounty that will become the new starting point


"""
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash
from boa.interop.Neo.Blockchain import GetHeight
from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.App import RegisterAppCall
from boa.interop.Neo.Storage import *

ctx = GetContext()

TUT_Scripthash = b"\x82N\xca\xfd\xcd\xd91}\xd8\xb2`\x89\xfb|\x88x\xdb\xc2\'\xae"
OWNER = b'\xdc\xcbK\xc2\xeb4TV\xe0\x15\xf9>|\t\xad\xfa\xcc\xea\x1ez'
KOTH_KEY = b'TheKing'
INCREMENT = 1000000000

KingNotify = RegisterAction('new_king', 'address', 'next_bounty', 'king_name')
TUT_Contract = RegisterAppCall('ae27c2db78887cfb8960b2d87d31d9cdfdca4e82', 'operation', 'args')

def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():
        if CheckWitness(OWNER):
            return True

        return False

    elif trigger == Application():

        if operation == 'currentKing':
            return Get(ctx, KOTH_KEY)

        if operation == 'currentBounty':
            myhash = GetExecutingScriptHash()
            currentBalance = TUT_Contract('balanceOf', [myhash])
            current_bounty = currentBalance + INCREMENT
            return current_bounty


        chash = GetCallingScriptHash()
        if chash != TUT_Scripthash:
            print('Token type not accepted by this contract')
            return False

        elif operation == 'onTokenTransfer':
            print('onTokenTransfer() called')

            return handle_token_received(ctx, args)
            
    return False


def handle_token_received(ctx, args):
  
    arglen = len(args)

    if arglen < 3:
        print('arg length incorrect')
        return False

    t_from = args[0]
    t_to = args[1]
    t_amount = args[2]

    king_name = None

    if arglen == 4:
        king_name = args[3]  # optional 4th argument passed by transfer()

    if len(t_from) != 20:
        return False

    if len(t_to) != 20:
        return False

    myhash = GetExecutingScriptHash()

    if t_to != myhash:
        return False

    currentBalance = TUT_Contract('balanceOf', [myhash])
    current_bounty = currentBalance + INCREMENT
            
    # contract owner can reset the game at will by sending low bounty

    if t_amount < current_bounty:
        if CheckWitness(OWNER):
            print('Game reset by contract owner!')
        else:
            print('Not enough to become king!')
            return False

    last_king = Get(ctx, KOTH_KEY)
    next_bounty = t_amount + INCREMENT

    if len(last_king) == 0:
        print('The first king has arrived!')
        Put(ctx, KOTH_KEY, t_from)
        KingNotify(t_from, next_bounty, king_name)
        return True

    # transfer all existing token balance to the previous king
    transferred = TUT_Contract('transfer', [myhash, last_king, currentBalance])

    if transferred:
        Put(ctx, KOTH_KEY, t_from)
        KingNotify(t_from, next_bounty, king_name)
        return True
    else:
        print('Transfer of treasury to previous king failed!')

    return False

