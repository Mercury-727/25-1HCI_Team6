from flask import Flask
from db import InMemoryDB

class DoziFlask(Flask):
    db: InMemoryDB

