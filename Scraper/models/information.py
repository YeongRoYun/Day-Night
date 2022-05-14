class Information:
    def __init__(self, siteName=None, cafeName=None, cafeTypes=None, cafeLocation=None, cafePreference=None, cafeKeywords=[],cafeReviews=None):
        self.siteName = siteName
        self.cafeName = cafeName
        self.cafeTypes = cafeTypes
        self.cafeLocation = cafeLocation
        self.cafeKeywords = cafeKeywords
        self.cafeReviews = cafeReviews
        self.cafePreference = cafePreference

class Review:
    def __init__(self, content=None, keywords=[], preference=None):
        self.content = content
        self.keywords = keywords
        self.preference = preference

    def __eq__(self, other):
        if not isinstance(other, Review):
            return NotImplemented
        return self.content == other.content and self.keywords == other.keywords
    def __hash__(self):
        return hash((self.content, self.keywords))