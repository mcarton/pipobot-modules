from sqlalchemy import BigInteger, Column, String

from pipobot.lib.bdd import Base


class LastTweets(Base):
    __tablename__ = 'last_tweets'
    user = Column(String(15), primary_key=True)
    last = Column(BigInteger)


class Tweets(Base):
    __tablename__ = 'tweets'
    id = Column(BigInteger, primary_key=True)
