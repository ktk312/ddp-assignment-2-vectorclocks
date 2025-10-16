# vector_clock.py
class VectorClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.clock = {node_id: 0}

    def increment(self):
        """Increment this node's counter."""
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1

    def update(self, other_clock: dict):
        """Merge another vector clock by taking the max of each node’s count."""
        for node, time in other_clock.items():
            self.clock[node] = max(self.clock.get(node, 0), time)

    def compare(self, other_clock):
        """Compare this vector clock with another VectorClock or dict."""
        # Handle both dict and VectorClock inputs
        try:
            other_clock_dict = other_clock.clock  # if it's a VectorClock instance
        except AttributeError:
            other_clock_dict = other_clock  # assume it's already a dict

        less, greater = False, False
        all_nodes = set(self.clock.keys()).union(other_clock_dict.keys())
        for node in all_nodes:
            local = self.clock.get(node, 0)
            remote = other_clock_dict.get(node, 0)
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


    def get_clock(self):
        """Return the current clock dictionary."""
        return self.clock

    def __repr__(self):
        return str(self.clock)
