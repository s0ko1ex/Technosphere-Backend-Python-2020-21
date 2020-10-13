from typing import Optional


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int = 10) -> None:
        self.capacity = capacity
        self.table: dict = {}
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None

    def get(self, key: str) -> Optional[str]:
        if key in self.table:
            cur = self.table[key]

            if cur == self.tail and cur.prev is not None:
                cur.prev.next = None
                self.tail = cur.prev

                cur.next = self.head
                cur.prev = None
                self.head.prev = cur

                self.head = cur
            elif cur != self.head:
                cur.prev.next = cur.next

                if cur.next is not None:
                    cur.next.prev = cur.prev

                cur.next = self.head
                cur.prev = None
                self.head.prev = cur

                self.head = cur

            return self.head.key
        else:
            return None

    def set(self, key: str, value: str) -> None:
        if key in self.table:
            self.get(key)
            self.head.value = value
        else:
            if len(self.table) == self.capacity:
                if self.tail:
                    if self.tail.prev:
                        self.tail.prev.next = None
                    else:
                        self.head = None

                    cur = self.tail
                    self.tail = cur.prev

                    self.table.pop(cur.key)
                    del cur

            cur = Node(key, value)
            self.table[key] = cur
            cur.next = self.head

            if self.head is not None:
                self.head.prev = cur
            elif self.head is None:
                self.tail = cur

            self.head = cur

    def delete(self, key: str) -> None:
        if key == self.head.key:
            cur = self.head
            self.head = cur.next

            if self.head is not None:
                self.head.prev = None

            if self.head == self.tail:
                self.tail = None
            del cur
        elif key == self.tail.key:
            cur = self.tail
            self.tail = cur.prev

            if self.tail is not None:
                self.tail.next = None

            if self.head == self.tail:
                self.head = None

            del cur
        elif key in self.table:
            cur = self.table[key]
            prev_node, next_node = cur.prev, cur.next
            prev_node.next = next_node
            next_node.prev = prev_node
            del cur
        else:
            raise KeyError

        self.table.pop(key)


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.set('1', '1')
    cache.set('2', '2')
    cache.set('3', '3')
    print(cache.get('1'))
