import hashlib
import json
from indy import anoncreds, ledger, pool, wallet, did
from indy-sdk.wrappers.python.tests.conftest import did_trustee

# Set up variables for connecting to the ledger
POOL_NAME = 'pool1'
POOL_GENESIS_txn_path = '/path/to/pool/genesis/file'
WALLET_NAME = 'wallet1'
WALLET_KEY = 'wallet_key'

async def give_consent(user_id, data_type, recipient_id):
    # Connect to the ledger and wallet
    await pool.set_protocol_version(2)
    pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
    wallet_handle = await wallet.open_wallet(WALLET_NAME, None, WALLET_KEY)

    # Create a DID for the user
    (user_did, user_key) = await did.create_and_store_my_did(wallet_handle, "{}")

    # Create the consent record and write it to the ledger
    consent = {
        "user_id": user_id,
        "data_type": data_type,
        "recipient_id": recipient_id
    }
    consent_json = json.dumps(consent)
    consent_hash = hashlib.sha256(consent_json.encode('utf-8')).hexdigest()
    consent_request = await ledger.build_nym_request(user_did, user_did, user_key, None, 'TRUST_ANCHOR')
    consent_response = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user_did, consent_request)

    # Close the connection to the ledger and wallet
    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)

async def revoke_consent(user_id, data_type, recipient_id):
    # Connect to the ledger and wallet
    await pool.set_protocol_version(2)
    pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
    wallet_handle = await wallet.open_wallet(WALLET_NAME, None, WALLET_KEY)

    # Create a DID for the user
    (user_did, user_key) = await did.create_and_store_my_did(wallet_handle, "{}")

    # Get the consent record from the ledger
    consent_filter = {
        "user_id": user_id,
        "data_type": data_type,
        "recipient_id": recipient_id
    }
    consent_filter_json = json.dumps(consent_filter)
    consent_filter_hash = hashlib.sha256(consent_filter_json.encode('utf-8')).hexdigest()
    consent_request = await ledger.build_get_txn_request(user_did, None, consent_filter_hash)
    consent_response = await ledger.submit_request(pool_handle, consent_request)

    # Remove the consent record from the ledger
    (consent_txn_json, _) = await ledger.parse_response(ledger_type, consent_response)
    consent_txn = json.loads(consent_txn_json)
    consent_request = await ledger.build_txn_author_agreement_request(user_did, None, consent_txn['seqNo'], 'REVOKE')
    consent_response = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user_did, consent_request)

    # Close the connection to the ledger and wallet
    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)

async def check_consent(user_id, data_type, recipient_id):
    # Connect to the ledger and wallet
    await pool.set_protocol_version(2)
    pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
    wallet_handle = await wallet.open_wallet(WALLET_NAME, None, WALLET_KEY)

    # Get the consent record from the ledger
    consent_filter = {
        "user_id": user_id,
        "data_type": data_type,
        "recipient_id": recipient_id
    }
    consent_request = await ledger.build_get_txn_request(did_trustee, consent_filter["seqNo"])
    consent_response = await ledger.submit_request(pool_handle, consent_request)
    
    # Check if the consent record exists on the ledger
    if consent_response:
        consent_data = json.loads(consent_response)
        if consent_data["result"]["data"]:
            return True
        else:
            return False
    else:
        return False
