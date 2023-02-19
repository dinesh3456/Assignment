import hashlib
import json
from indy import anoncreds, ledger, pool, wallet, did
from indy-sdk.wrappers.python.tests.conftest import did_trustee

POOL_NAME = 'pool1'
POOL_GENESIS_txn_path = '/path/to/pool/genesis/file'
WALLET_NAME = 'wallet1'
WALLET_KEY = 'wallet_key'

async def give_consent(user_id, data_type, recipient_id):

    await pool.set_protocol_version(2)
    pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
    wallet_handle = await wallet.open_wallet(WALLET_NAME, None, WALLET_KEY) 
    (user_did, user_key) = await did.create_and_store_my_did(wallet_handle, "{}")

    consent = {
        "user_id": user_id,
        "data_type": data_type,
        "recipient_id": recipient_id
    }
    consent_json = json.dumps(consent)
    consent_hash = hashlib.sha256(consent_json.encode('utf-8')).hexdigest()
    consent_request = await ledger.build_nym_request(user_did, user_did, user_key, None, 'TRUST_ANCHOR')
    consent_response = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user_did, consent_request)
    
    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)

async def revoke_consent(user_id, data_type, recipient_id):
 
    await pool.set_protocol_version(2)
    pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
    wallet_handle = await wallet.open_wallet(WALLET_NAME, None, WALLET_KEY)
    (user_did, user_key) = await did.create_and_store_my_did(wallet_handle, "{}")

    consent_filter = {
        "user_id": user_id,
        "data_type": data_type,
        "recipient_id": recipient_id
    }
    consent_filter_json = json.dumps(consent_filter)
    consent_filter_hash = hashlib.sha256(consent_filter_json.encode('utf-8')).hexdigest()
    consent_request = await ledger.build_get_txn_request(user_did, None, consent_filter_hash)
    consent_response = await ledger.submit_request(pool_handle, consent_request)

    (consent_txn_json, _) = await ledger.parse_response(ledger_type, consent_response)
    consent_txn = json.loads(consent_txn_json)
    consent_request = await ledger.build_txn_author_agreement_request(user_did, None, consent_txn['seqNo'], 'REVOKE')
    consent_response = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user_did, consent_request)

    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)

async def check_consent(user_id, data_type, recipient_id):
 
    await pool.set_protocol_version(2)
    pool_handle = await pool.open_pool_ledger(POOL_NAME, None)
    wallet_handle = await wallet.open_wallet(WALLET_NAME, None, WALLET_KEY)

   
    consent_filter = {
        "user_id": user_id,
        "data_type": data_type,
        "recipient_id": recipient_id
    }
    consent_request = await ledger.build_get_txn_request(did_trustee, consent_filter["seqNo"])
    consent_response = await ledger.submit_request(pool_handle, consent_request)
    

    if consent_response:
        consent_data = json.loads(consent_response)
        if consent_data["result"]["data"]:
            return True
        else:
            return False
    else:
        return False
