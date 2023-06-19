import collections

# Watermark tuple definition
ID_WMi_tuple = collections.namedtuple("ID_WMi_tuple", ["Wi", "Li", "ni", "mi"])

#  Algorithm constants
WStart = 100  # watermark starting position in the embedding vector
P = 256  # EA matrix size
alpha = 0.1  # embedding coefficient
Delta = 4  # Cxy maximum search window

# Redis db used for caching
REDIS_URL = "redis://:UCeaD3KjeQx6f7X22wX2zwd@redis:16379/0"