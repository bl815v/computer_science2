from app.services.search.external.dynamic_hash import DynamicHashExternalSearch
from app.services.search.hash.hash_function import ModHash

hash_func = ModHash()

dyn_hash = DynamicHashExternalSearch(
	hash_func=hash_func, initial_num_buckets=3, bucket_size=2, expansion_policy='partial'
)

dyn_hash.create(digits=2)

elements = ['30', '25', '18', '33', '40', '55', '17', '38', '23', '11', '10', '13', '72']

for element in elements:
	dyn_hash.insert(element)
	print(f'Insertado: {element}')
	print(f'Bloques: {dyn_hash.blocks}')
	print(f'Overflow: {dyn_hash.overflow}\n')

print('--- Eliminando elementos ---\n')
for element in ['18', '33', '40', '55']:
	dyn_hash.delete(element)
	print(f'Eliminado: {element}')
	print(f'Bloques: {dyn_hash.blocks}')
	print(f'Overflow: {dyn_hash.overflow}\n')
