class NimHandler:
    def __init__(self):
        try:
            import nim
            self.handler = nim.FileHandler()
            self.available = True
        except ImportError:
            self.available = False 