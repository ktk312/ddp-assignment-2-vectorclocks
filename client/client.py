import requests
import threading
import time

# BASE_URL = "https://rpc-server-assignment-production.up.railway.app"
BASE_URL = "http://localhost:8080"


# ==========================
# Vector Clock Implementation
# ==========================
class VectorClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.clock = {node_id: 0}

    def increment(self):
        """Increment this node’s clock."""
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1

    def update(self, other_clock):
        """Merge another vector clock (dict or VectorClock)."""
        # Accept both dicts and VectorClock instances
        if isinstance(other_clock, VectorClock):
            other_clock = other_clock.clock
        for node, time in other_clock.items():
            self.clock[node] = max(self.clock.get(node, 0), time)

    def compare(self, other_clock):
        """Compare with another VectorClock or dict."""
        # Accept both dicts and VectorClock instances
        if isinstance(other_clock, VectorClock):
            other_clock = other_clock.clock

        less, greater = False, False
        all_nodes = set(self.clock.keys()).union(other_clock.keys())

        for node in all_nodes:
            local = self.clock.get(node, 0)
            remote = other_clock.get(node, 0)
            if local < remote:
                less = True
            elif local > remote:
                greater = True

        if less and not greater:
            return "happens-before"
        elif greater and not less:
            return "happens-after"
        elif greater and less:
            return "concurrent"
        return "equal"

    def __repr__(self):
        return str(self.clock)

# ==========================
# RPC Client Functions
# ==========================
class RPCClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.clock = VectorClock(client_id)

    def call_rpc(self, endpoint, x, y):
        """Send a request to the server and handle vector clock updates."""
        self.clock.increment()
        payload = {"x": x, "y": y, "vector_clock": self.clock.clock}

        try:
            response = requests.post(f"{BASE_URL}/{endpoint}", json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Merge clocks
            if "server_clock" in data:
                self.clock.update(data["server_clock"])

            print(f"[{self.client_id}] /{endpoint}({x},{y}) -> result={data.get('result')}")
            print(f"[{self.client_id}] Updated clock: {self.clock}\n")
            return data
        except requests.exceptions.Timeout:
            print(f"[{self.client_id}] ERROR: Request to /{endpoint} timed out.\n")
            return {"error": "Request timed out"}


# ==========================
# Test Scenarios
# ==========================
def sequential_scenario():
    """Scenario 1: Sequential calls (causal relation)."""
    print("\n--- Sequential (Causal) Scenario ---")
    clientA = RPCClient("clientA")
    clientB = RPCClient("clientB")

    resA = clientA.call_rpc("add", 5, 10)
    resB = clientB.call_rpc("multiply", 2, 3)

    relation = clientA.clock.compare(clientB.clock)
    print(f"Relation between A and B: {relation}\n")


def concurrent_scenario():
    """Scenario 2: Concurrent requests."""
    print("\n--- Concurrent Scenario ---")
    clientA = RPCClient("clientA")
    clientB = RPCClient("clientB")

    def taskA():
        clientA.call_rpc("add", 10, 20)

    def taskB():
        clientB.call_rpc("multiply", 3, 7)

    t1 = threading.Thread(target=taskA)
    t2 = threading.Thread(target=taskB)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    relation = clientA.clock.compare(clientB.clock)
    print(f"Relation between A and B: {relation}\n")


def interleaved_scenario():
    """Scenario 3: Interleaved causal + concurrent events."""
    print("\n--- Interleaved Scenario ---")
    clientA = RPCClient("clientA")
    clientB = RPCClient("clientB")

    # A performs operation
    clientA.call_rpc("add", 1, 2)

    # B performs operation after some delay (causal)
    time.sleep(1)
    clientB.call_rpc("multiply", 3, 4)

    # Both act concurrently
    t1 = threading.Thread(target=lambda: clientA.call_rpc("add", 10, 10))
    t2 = threading.Thread(target=lambda: clientB.call_rpc("add", 5, 5))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    relation = clientA.clock.compare(clientB.clock)
    print(f"Final relation between A and B: {relation}\n")


if __name__ == "__main__":
    sequential_scenario()
    concurrent_scenario()
    interleaved_scenario()
