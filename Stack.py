class Stack:
    def __init__(self):
        self.len = 0
        self.load = []

    def __repr__(self):
        tmp = map(str, self.load)
        return ", ".join(tmp)
    def push(self, item):
        self.load.append(item)
        self.len += 1

    def pop(self):
        self.len -= 1
        return self.load.pop()

    def peek(self):
        return self.load[self.len-1]

