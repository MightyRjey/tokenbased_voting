from brownie import accounts, network, config, ElectionToken, Election, interface, exceptions
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, FORKED_LOCAL_ENVIRONMENTS
from scripts.deploy_election import approve_erc20
from web3 import Web3
import pytest
import time

def test_can_get_token():
    # Test won't be deployed on mainnet or testnets because it is a unit test
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS and FORKED_LOCAL_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    # Deploying the token
    ET = ElectionToken.deploy(Web3.toWei(100, "ether"), {"from": account})
    # Deploying the election contract
    election = Election.deploy(ET.address, {"from": account})
    election.playGame(8459, account.address, {"from": accounts[1]})
    election.playGame(8459, account.address, {"from": accounts[2]})
    election.playGame(8459, account.address, {"from": accounts[2]})
    # Approving 1 ET to be transfered to winner of our minigame
    approve_erc20(Web3.toWei(3,"ether"), election.address, ET.address, account)
    election.getToken(account.address,{"from": accounts[1]})
    election.getToken(account.address,{"from": accounts[2]})
    ETInterface = interface.IERC20(ET.address)
    # Testing to see if the account has received the token
    assert ETInterface.balanceOf(accounts[1].address) == Web3.toWei(1, "ether")
    assert ETInterface.balanceOf(accounts[2].address) == Web3.toWei(2, "ether")


def test_cannot_get_token_with_wrong_answer():
    # Test won't be deployed on mainnet or testnets because it is a unit test
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS and FORKED_LOCAL_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    # Deploying the token
    ET = ElectionToken.deploy(Web3.toWei(100, "ether"), {"from": account})
    # Deploying the election contract
    election = Election.deploy(ET.address, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        election.playGame(8458, account.address, {"from": account})

def test_votes_counted_correctly():
    # Test won't be deployed on mainnet or testnets because it is a unit test
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS and FORKED_LOCAL_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    # Deploying the token
    ET = ElectionToken.deploy(Web3.toWei(100, "ether"), {"from": account})
    # Deploying the election contract
    election = Election.deploy(ET.address, {"from": account})
    election.playGame(8459, account.address, {"from": accounts[1]})
    election.playGame(8459, account.address, {"from": accounts[2]})
    election.playGame(8459, account.address, {"from": accounts[2]})
    # Approving 1 ET to be transfered to winner of our minigame
    approve_erc20(Web3.toWei(3,"ether"), election.address, ET.address, account)
    election.getToken(account.address,{"from": accounts[1]})
    election.getToken(account.address,{"from": accounts[2]})
    election.startElection(3,3,{"from": account})
    approve_erc20(Web3.toWei(0.5,"ether"), election.address, ET.address, accounts[1])
    election.vote(0,{"from": accounts[1]})
    approve_erc20(Web3.toWei(0.5,"ether"), election.address, ET.address, accounts[2])
    election.vote(1,{"from": accounts[2]})
    approve_erc20(Web3.toWei(0.5,"ether"), election.address, ET.address, account)
    election.vote(2,{"from": account})
    time.sleep(3)
    tx = election.endElection({"from": account})
    tx.wait(1)
    assert tx.events[0]["_index"] == 2
    assert tx.events[0]["_voteNumber"] == 96500000000000000000

def test_cannot_vote_incorrectly():
    # Test won't be deployed on mainnet or testnets because it is a unit test
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS and FORKED_LOCAL_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    # Deploying the token
    ET = ElectionToken.deploy(Web3.toWei(100, "ether"), {"from": account})
    # Deploying the election contract
    election = Election.deploy(ET.address, {"from": account})
    # Starting the election with 3 candidates
    election.startElection(3,3,{"from": account})
    approve_erc20(Web3.toWei(0.5,"ether"), election.address, ET.address, account)
    # Voting for a 4th candidate which does not exist and should raise an error
    with pytest.raises(exceptions.VirtualMachineError):
        election.vote(3,{"from": account})

