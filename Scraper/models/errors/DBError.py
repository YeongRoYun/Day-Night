class DBError(Exception):
    def __init__(self, *args):
        super.__init__(args)
