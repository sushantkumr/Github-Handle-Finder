from lib.models.db import Base
from sqlalchemy import Column, String, Integer


class SearchResults(Base):
    __tablename__ = 'search_results'

    id = Column(Integer, primary_key=True)
    searcher_github_id = Column(Integer)
    avatar_url = Column(String(255))
    username = Column(String(255))
    html_url = Column(String(255)) # Different cause keyword
    github_id = Column(Integer)

    def __init__(self, searcher_github_id, avatar_url, username, html_url, github_id):
        self.searcher_github_id = searcher_github_id
        self.avatar_url = avatar_url
        self.username = username
        self.html_url = html_url
        self.github_id = github_id

    def __repr__(self):
        return '<SearchResults %r>' % (self.username)
