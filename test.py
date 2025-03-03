from pycardano.backend.blockfrost import BlockFrostChainContext
from pycardano import Network

context = BlockFrostChainContext("preprodb2HjJe69kficC8NpRd1YUATw1bAQdGZe", network=Network.TESTNET)
context.protocol_param