const crypto = require('crypto');
const { IndyError } = require('indy-sdk');
const indy = require('indy-sdk');
const did_trustee = require('./did_trustee');
// Set up variables for connecting to the ledger
const POOL_NAME = 'pool1';
const POOL_GENESIS_txn_path = '/path/to/pool/genesis/file';
const WALLET_NAME = 'wallet1';
const WALLET_KEY = 'wallet_key';

async function give_consent(user_id, data_type, recipient_id) {
  // Connect to the ledger and wallet
  await pool.set_protocol_version(2);
  const pool_handle = await pool.open_pool_ledger(POOL_NAME, null);
  const wallet_handle = await wallet.open_wallet(WALLET_NAME, null, WALLET_KEY);

  // Create a DID for the user
  const [user_did, user_key] = await did.create_and_store_my_did(wallet_handle, "{}");

  // Create the consent record and write it to the ledger
  const consent = {
    "user_id": user_id,
    "data_type": data_type,
    "recipient_id": recipient_id
  };
  const consent_json = JSON.stringify(consent);
  const consent_hash = hashlib.sha256(consent_json.encode('utf-8')).hexdigest();
  const consent_request = await ledger.build_nym_request(user_did, user_did, user_key, null, 'TRUST_ANCHOR');
  const consent_response = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user_did, consent_request);

  // Close the connection to the ledger and wallet
  await wallet.close_wallet(wallet_handle);
  await pool.close_pool_ledger(pool_handle);
}

async function revoke_consent(user_id, data_type, recipient_id) {
  // Connect to the ledger and wallet
  await pool.set_protocol_version(2);
  const pool_handle = await pool.open_pool_ledger(POOL_NAME, null);
  const wallet_handle = await wallet.open_wallet(WALLET_NAME, null, WALLET_KEY);

  // Create a DID for the user
  const [user_did, user_key] = await did.create_and_store_my_did(wallet_handle, "{}");

  // Get the consent record from the ledger
  const consent_filter = {
    "user_id": user_id,
    "data_type": data_type,
    "recipient_id": recipient_id
  };
  const consent_filter_json = JSON.stringify(consent_filter);
  const consent_filter_hash = hashlib.sha256(consent_filter_json.encode('utf-8')).hexdigest();
   consent_request = await ledger.build_get_txn_request(user_did, null, consent_filter_hash);
   consent_response = await ledger.submit_request(pool_handle, consent_request);

  // Remove the consent record from the ledger
  const [consent_txn_json, _] = await ledger.parse_response(ledger_type, consent_response);
  const consent_txn = JSON.parse(consent_txn_json);
  const consent_request = await ledger.build_txn_author_agreement_request(user_did, null, consent_txn['seqNo'], 'REVOKE');
  const consent_response = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user_did, consent_request);

  // Close the connection to the ledger and wallet
  await wallet.close_wallet(wallet_handle);
  await pool.close_pool_ledger(pool_handle);
}

async function check_consent(user_id, data_type, recipient_id) {
  // Connect to the ledger and wallet
  await pool.setProtocolVersion(2);
  const pool_handle = await pool.openPoolLedger(POOL_NAME, null);
  const wallet_handle = await wallet.openWallet(WALLET_NAME, null, WALLET_KEY);

  try {
    // Get the DID for the trustee
    const trustee_did = await did_trustee.get_trustee_did();

    // Get the consent record from the ledger
    const consent_filter = {
      "user_id": user_id,
      "data_type": data_type,
      "recipient_id": recipient_id
    };
    const consent_filter_json = JSON.stringify(consent_filter);
    const consent_filter_hash = sha256(consent_filter_json);
    const consent_request = await ledger.buildGetTxnRequest(trustee_did, null, consent_filter_hash);
    const consent_response = await ledger.submitRequest(pool_handle, consent_request);

    // Check if the consent record exists on the ledger
    if (consent_response) {
      const consent_data = JSON.parse(consent_response);
      if (consent_data["result"]["data"]) {
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  } finally {
    // Close the connection to the ledger and wallet
    await wallet.closeWallet(wallet_handle);
    await pool.closePoolLedger(pool_handle);
  }
}
