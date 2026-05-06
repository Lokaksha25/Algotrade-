"""
AlgoTrade Engine — AVL Tree Order Book
Self-balancing BST for simulated limit order book.

DAA Paradigm: Balanced BST (AVL Tree)
Brute-force: O(n) insert/delete in sorted list  |  AVL: O(log n) all operations
Supports insert, delete, best bid/ask lookup with LL/RR/LR/RL rotations.
"""


class AVLNode:
    """Single node in the AVL tree."""
    __slots__ = ["price", "quantity", "side", "height", "left", "right"]

    def __init__(self, price: float, quantity: int = 1, side: str = "bid"):
        self.price = price
        self.quantity = quantity
        self.side = side
        self.height = 1
        self.left = None
        self.right = None


class AVLTree:
    """
    AVL Tree (self-balancing BST) for order book simulation.
    
    All operations: O(log n)
      - insert: add order at price level
      - delete: remove order at price level
      - find_min: best ask (lowest sell price)
      - find_max: best bid (highest buy price)
      - search: find order at specific price
    
    Maintains balance factor ∈ {-1, 0, 1} via rotations:
      - LL (Right Rotation), RR (Left Rotation)
      - LR (Left-Right), RL (Right-Left)
    """

    def __init__(self):
        self.root = None
        self.size = 0

    def _height(self, node: AVLNode) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: AVLNode) -> int:
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node: AVLNode):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    # ── Rotations ──────────────────────────────────────────────────────

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """LL case — Right rotation."""
        x = y.left
        t2 = x.right
        x.right = y
        y.left = t2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """RR case — Left rotation."""
        y = x.right
        t2 = y.left
        y.left = x
        x.right = t2
        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node: AVLNode, price: float) -> AVLNode:
        """Rebalance node after insert/delete."""
        bf = self._balance_factor(node)

        # LL case
        if bf > 1 and price < node.left.price:
            return self._rotate_right(node)
        # RR case
        if bf < -1 and price > node.right.price:
            return self._rotate_left(node)
        # LR case
        if bf > 1 and price > node.left.price:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        # RL case
        if bf < -1 and price < node.right.price:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ── Insert O(log n) ───────────────────────────────────────────────

    def insert(self, price: float, quantity: int = 1, side: str = "bid"):
        """Insert order at price level. O(log n)."""
        self.root = self._insert(self.root, price, quantity, side)
        self.size += 1

    def _insert(self, node: AVLNode, price: float, quantity: int, side: str) -> AVLNode:
        if not node:
            return AVLNode(price, quantity, side)

        if price < node.price:
            node.left = self._insert(node.left, price, quantity, side)
        elif price > node.price:
            node.right = self._insert(node.right, price, quantity, side)
        else:
            node.quantity += quantity  # Same price level — aggregate
            return node

        self._update_height(node)
        return self._rebalance(node, price)

    # ── Delete O(log n) ───────────────────────────────────────────────

    def delete(self, price: float):
        """Delete order at price level. O(log n)."""
        self.root = self._delete(self.root, price)
        self.size = max(0, self.size - 1)

    def _delete(self, node: AVLNode, price: float) -> AVLNode:
        if not node:
            return None

        if price < node.price:
            node.left = self._delete(node.left, price)
        elif price > node.price:
            node.right = self._delete(node.right, price)
        else:
            # Node found — standard BST delete
            if not node.left:
                return node.right
            elif not node.right:
                return node.left

            # Two children: find inorder successor (min of right subtree)
            successor = self._find_min_node(node.right)
            node.price = successor.price
            node.quantity = successor.quantity
            node.side = successor.side
            node.right = self._delete(node.right, successor.price)

        self._update_height(node)
        bf = self._balance_factor(node)

        # Rebalance after deletion
        if bf > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node)
        if bf > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if bf < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node)
        if bf < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ── Queries O(log n) ──────────────────────────────────────────────

    def _find_min_node(self, node: AVLNode) -> AVLNode:
        while node.left:
            node = node.left
        return node

    def _find_max_node(self, node: AVLNode) -> AVLNode:
        while node.right:
            node = node.right
        return node

    def find_min(self) -> float:
        """Find minimum price (best ask). O(log n)."""
        if not self.root:
            return None
        return self._find_min_node(self.root).price

    def find_max(self) -> float:
        """Find maximum price (best bid). O(log n)."""
        if not self.root:
            return None
        return self._find_max_node(self.root).price

    def search(self, price: float) -> AVLNode:
        """Search for a price level. O(log n)."""
        node = self.root
        while node:
            if price == node.price:
                return node
            elif price < node.price:
                node = node.left
            else:
                node = node.right
        return None

    def inorder(self) -> list[dict]:
        """Return all orders sorted by price. O(n)."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: AVLNode, result: list):
        if node:
            self._inorder(node.left, result)
            result.append({"price": node.price, "quantity": node.quantity, "side": node.side})
            self._inorder(node.right, result)

    def is_balanced(self) -> bool:
        """Verify AVL balance invariant for all nodes."""
        return self._check_balanced(self.root)

    def _check_balanced(self, node: AVLNode) -> bool:
        if not node:
            return True
        bf = self._balance_factor(node)
        if abs(bf) > 1:
            return False
        return self._check_balanced(node.left) and self._check_balanced(node.right)


# ═══════════════════════════════════════════════════════════════════════════════
# BRUTE-FORCE BASELINE — Sorted List O(n) insert
# ═══════════════════════════════════════════════════════════════════════════════

class SortedListOrderBook:
    """Brute-force order book using sorted list. Insert: O(n), lookup: O(1)."""

    def __init__(self):
        self.orders = []  # Kept sorted by price

    def insert(self, price: float, quantity: int = 1, side: str = "bid"):
        """Insert in sorted position — O(n) due to shifting."""
        import bisect
        bisect.insort(self.orders, (price, quantity, side))

    def delete(self, price: float):
        """Delete by price — O(n) search + shift."""
        for i, (p, q, s) in enumerate(self.orders):
            if p == price:
                self.orders.pop(i)
                return
    
    def find_min(self) -> float:
        return self.orders[0][0] if self.orders else None

    def find_max(self) -> float:
        return self.orders[-1][0] if self.orders else None

    def __len__(self):
        return len(self.orders)
