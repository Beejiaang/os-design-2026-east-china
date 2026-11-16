"""A's integration probe; B owns the production data workload and correctness tests."""
import hashlib

digest = b"osdesign-cpu-probe-v1"
for _ in range(1500000):
    digest = hashlib.sha256(digest).digest()
print(digest.hex())
