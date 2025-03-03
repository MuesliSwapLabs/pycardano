"""A script that sends loyalty rewards (based on certain rules) to a pool's delegators in one transaction
An example transaction generated by this script on mainnet:
https://cardanoscan.io/transaction/c1b58dd4f2f4ee8656cc7962eefa8552877c4aa23d0699c02b885363d592a961
"""

from blockfrost import ApiUrls, BlockFrostApi

from pycardano import *

# ======= Modify variables below ========

network = Network.MAINNET

BLOCK_FROST_PROJECT_ID = "your_project_id"

POOL_ID = "your_pool_id"

POOL_TICKER = "your_pool_ticker"

# An address where any changes will be returned to
CHANGE_ADDRESS = "your_change_address"

# If you want to exclude any address (e.g. your own address), include those in the variable below
EXCLUDE_ADDRESSES = []

# The payment key used to generate sender address
PAYMENT_KEY_PATH = "payment.skey"

# ======= Modify variables above ========


# Read keys to memory
# Assume there is a payment.skey file sitting in current directory
psk = PaymentSigningKey.load(PAYMENT_KEY_PATH)
pvk = PaymentVerificationKey.from_signing_key(psk)

# Derive an address from payment verification key
input_address = Address(pvk.hash(), network=network)
print(
    f"ADA will be distributed from this address: {input_address}, make sure there are enough ADA in it."
)

# Create a BlockFrost chain context
context = BlockFrostChainContext(BLOCK_FROST_PROJECT_ID, base_url=ApiUrls.mainnet.value)

api = BlockFrostApi(BLOCK_FROST_PROJECT_ID, ApiUrls.mainnet.value)

delegators = api.pool_delegators(POOL_ID, gather_pages=True)

to_send_50 = []
to_send_10 = []

for delegator in delegators:
    if delegator.address not in EXCLUDE_ADDRESSES:
        if int(delegator.live_stake) >= 100000000000:
            to_send_50.append(delegator)
        elif int(delegator.live_stake) >= 10000000000:
            to_send_10.append(delegator)

builder = TransactionBuilder(context)

builder.add_input_address(input_address)

# ======= Business logic starts ========

# Send 50 ADA to delegators with 100K+ ADA
for d in to_send_50:
    to_send_addr = api.account_addresses(d.address)[0].address
    builder.add_output(TransactionOutput.from_primitive([to_send_addr, 50000000]))

# Send 10 ADA to delegators with 10K+ ADA
for d in to_send_10:
    to_send_addr = api.account_addresses(d.address)[0].address
    builder.add_output(TransactionOutput.from_primitive([to_send_addr, 10000000]))

# ======= Business logic ends ========

auxiliary_data = AuxiliaryData(
    AlonzoMetadata(
        metadata=Metadata(
            {
                674: {
                    "Title": f"Loyalty rewards for stake pool [{POOL_TICKER}] delegators",
                    "Rules": {"100K+": "50 ADA", "10K+": "10 ADA"},
                    "Notes": "Created with https://github.com/Python-Cardano/pycardano.",
                }
            }
        )
    )
)

builder.auxiliary_data = auxiliary_data

# Create final signed transaction
signed_tx = builder.build_and_sign(
    [psk], change_address=Address.from_primitive(CHANGE_ADDRESS)
)

# Submit signed transaction to the network
print(signed_tx)

print("#### Transaction id ####")
print(signed_tx.id)
context.submit_tx(signed_tx)
print("Transaction successfully submitted!")
