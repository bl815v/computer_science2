
from app.services.search.hash.collision_chained import ChainedHashTable, NestedArrayHashTable
from app.services.search.hash.collision_simple import (
    DoubleHashResolver,
    LinearResolver,
    QuadraticResolver,
)
from app.services.search.hash.hash_function import FoldingHash, ModHash, SquareHash, TruncationHash
from app.services.search.hash.hash_table import HashTable

funcion = ModHash()

tabla = HashTable(funcion)
tabla.create(size=10, digits=4)
#tabla.set_chaining()

pos = tabla.insert('1234')

found = tabla.search('1234')

removed = tabla.delete('1234')

pos = tabla.insert('3099')
print(pos)
pos = tabla.insert('4099')
print(pos)
pos = tabla.insert('5099')
print(pos)
pos = tabla.insert('6099')
print(pos)
print(tabla)
