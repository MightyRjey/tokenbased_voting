from brownie import accounts, interface, network, config, Election, ElectionToken
from scripts.helpful_scripts import get_account
from web3 import Web3
import time

def approve_erc20(amount, spender, erc20_address, account):
    # ABI
    # Address
    print("Approving ERC20 token ...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    amount_approved = Web3.fromWei(amount, "ether")
    print(f"Approved {amount_approved} ET!")
    return tx

def main():
    deploy()

# Variables in this function can be parameterized but they are hard coded for the sake of showcasing
def deploy():
    account = get_account()
    # Deploying the token
    ET = ElectionToken.deploy(Web3.toWei(100, "ether"), {"from": account})
    print("Election Token Deployed!")
    # Deploying the election contract
    election = Election.deploy(ET.address, {"from": account})
    print("Election contract deployed!")
    election.playGame(8459, account.address, {"from": accounts[1]})
    print(f"Congrats, {accounts[1].address} gets 1 ET!")
    election.playGame(8459, account.address, {"from": accounts[2]})
    election.playGame(8459, account.address, {"from": accounts[2]})
    print(f"Congrats, {accounts[2].address} gets 2 ET!")
    get_token(accounts[1], account, election, ET, Web3.toWei(1, "ether"))
    print(f"Withdrew 1 ET for {accounts[1].address}")
    get_token(accounts[2], account, election, ET, Web3.toWei(2, "ether"))
    print(f"Withdrew 2 ET for {accounts[2].address}")
    election.startElection(3,3,{"from": account})
    vote(Web3.toWei(0.5, "ether"), election, ET.address, accounts[1], 0)
    print(f"{accounts[1].address} voted for candidate 0")
    vote(Web3.toWei(0.5, "ether"), election, ET.address, accounts[2], 1)
    print(f"{accounts[2].address} voted for candidate 1")
    vote(Web3.toWei(0.5, "ether"), election, ET.address, account, 2)
    print(f"{account.address} voted for candidate 2")
    time.sleep(3)
    tx = election.endElection({"from": account})
    tx.wait(1)
    winner = tx.events[0]["_index"]
    winnerVotes = tx.events[0]["_voteNumber"]
    print(f"The winner of the election is: {winner}")
    print(f"Numbers of vote for the winner: {winnerVotes}")

def get_token(account, sender, election, ET, amount):
    approve_erc20(Web3.toWei(amount,"ether"), election.address, ET.address, sender)
    election.getToken(sender.address,{"from": account})

def vote(amount, spender, erc20_address, account, vote):
    approve_erc20(amount, spender.address, erc20_address, account)
    spender.vote(vote, {"from": account})
