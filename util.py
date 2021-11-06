class Queue:
    """An implementation of a FIFO Queue."""
    def __init__(self):
        self.list = []

    def push(self,item):
        """Enqueue item to the left of queue"""
        self.list.insert(0,item)

    def pop(self):
        """Dequeue and return the rightmost item of queue"""
        return self.list.pop()

    def isEmpty(self):
        """Returns true if the queue is empty"""
        return len(self.list) == 0
    
    def size(self):
        """Returns size of queue"""
        return len(self.list)
    
    def printQueue(self):
        """Prints out the queue items"""
        print(self.list)
