import os,csv
from booksdb import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
database = scoped_session(sessionmaker(bind=engine))

def main():
    Base.metadata.create_all(bind=engine)
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)
    for isbn,title,author,year in reader:
        book = Books(isbn=isbn,title=title,author=author,year=int(year))
        database.add(book)
    database.commit()
    database.close()

if __name__ == "__main__":
    main()

