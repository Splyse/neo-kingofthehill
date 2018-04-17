# neo-kingofthehill
A King of the Hill smart contract example using Test Utility Token (TUT) on Neo TestNet.

The game is entirely self-contained inside the smart contract, there's no web or middleware code. All you need to do to play the game is send an amount of TUT greater than the current bounty to the contract address, `AK1nGHaL184ffGJkbs977VtafiP5hzXQ9j`

When a new king takes over, the contract sends the old king back all his tokens automatically, all in the same transaction.

You can call the currentKing operation to get the scripthash of the current reigning king, and currentBounty to know the amount to knock him off of the throne. The game scripthash is 2d838efcda02e9b6bc42ce21ce34acad14b58923. So in neo-python, an invoke might look like:

```
testinvoke 2d838efcda02e9b6bc42ce21ce34acad14b58923 currentBounty []
```
returning the bounty in Fixed8 format (i.e. divide by 100000000 to get the correct number of TUT tokens)

The contract owner can reset the game at any time, refunding all the tokens to the last king

Additionally, an optional 'name' parameter can be passed as a fourth argument to the NEP-5 transfer() operation, and the Notify() message that is broadcast will include the new king's name for posterity. The game contract receives a notification through dynamic invoke any time it receives tokens, and that argument will be passed from the token contract to the game contract.

In neo-python, to play with a 20-token transfer might look something like: 
```
testinvoke ae27c2db78887cfb8960b2d87d31d9cdfdca4e82 transfer ['Adr3XjZ5QDzVJrWvzmsTTchpLRRGSzgS5A',
'AK1nGHaL184ffGJkbs977VtafiP5hzXQ9j',2000000000,'Prince Humperdink']
```

which will have the contract broadcast a `new_king` notification containing the optional name value name. But the name argument is optional, a regular transfer of tokens from Neon wallet or neo-python's `wallet tkn_send` command will still work if you don't care about the name notification message.
