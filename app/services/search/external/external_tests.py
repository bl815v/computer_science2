from app.services.search.external.hash_external import BaseConversionHash, HashExternalSearch
from app.services.search.hash.hash_function import FoldingHash, ModHash, SquareHash, TruncationHash


def demo_hash_external():
	"""Demostración de HashExternalSearch con diferentes funciones hash."""

	# ============================================
	# Ejemplo 1: ModHash con buckets de capacidad 3
	# ============================================
	print('=== HashExternalSearch con ModHash ===')
	hash_mod = ModHash()
	search = HashExternalSearch(hash_mod)

	search.create(10, 2)

	valores = [
		19,
		16,
		22,
		25,
		28,
		31,
		35,
		37,
		39,
		42,
		40,
		44,
		46,
		48,
		49,
		51,
		53,
		55,
		57,
		59,
		61,
		63,
		65,
		68,
		70,
		75,
		72,
	]

	print('\n--- Insertando 27 valores (algunos provocarán overflow) ---')
	for v in valores:
		try:
			pos = search.insert(str(v).zfill(2))
			print(f'Insertado {v:02d} en posición global {pos}')
		except ValueError as e:
			print(f'Error al insertar {v:02d}: {e}')

	print('\n--- Estado de los buckets principales (hasta 3 por bucket) ---')
	for i, bloque in enumerate(search.blocks):
		print(f'Bucket {i}: {bloque}')

	print('\n--- Listas de overflow ---')
	for i, ov in enumerate(search.overflow):
		if ov:
			print(f'Overflow[{i}]: {ov}')

	print('\n--- Búsquedas detalladas ---')
	busquedas = [16, 42, 70, 99]
	for val in busquedas:
		v_str = str(val).zfill(2)
		resultados = search.search(v_str)
		if resultados:
			for r in resultados:
				print(
					f'Valor {v_str} encontrado: '
					f'bucket {r["block_index"]}, '
					f'posición interna {r["block_position"]}, '
					f'posición global {r["global_position"]}'
				)
		else:
			print(f'Valor {v_str} no encontrado')

	print('\n--- Eliminaciones ---')
	eliminar = [40, 55, 99]
	for val in eliminar:
		v_str = str(val).zfill(2)
		eliminados = search.delete(v_str)
		if eliminados:
			print(f'Eliminado {v_str} de posición global {eliminados[0]}')
		else:
			print(f'Valor {v_str} no encontrado para eliminar')

	print('\n--- Estado después de eliminaciones (buckets principales) ---')
	for i, bloque in enumerate(search.blocks):
		print(f'Bucket {i}: {bloque}')
	print('--- Overflow después de eliminaciones ---')
	for i, ov in enumerate(search.overflow):
		if ov:
			print(f'Overflow[{i}]: {ov}')

	print('\n--- Verificación de eliminados ---')
	for val in eliminar:
		v_str = str(val).zfill(2)
		if search.search(v_str):
			print(f'Error: {v_str} todavía presente')
		else:
			print(f'{v_str} correctamente eliminado')

	# ============================================
	# Ejemplo 2: SquareHash
	# ============================================
	print('\n\n=== HashExternalSearch con SquareHash ===')
	hash_square = SquareHash()
	search2 = HashExternalSearch(hash_square)
	search2.create(8, 2)

	valores2 = [15, 23, 42, 57, 68, 71, 84, 99, 12, 34, 56, 78]
	print('\n--- Insertando valores ---')
	for v in valores2:
		pos = search2.insert(str(v).zfill(2))
		print(f'Insertado {v:02d} en posición global {pos}')

	print('\n--- Buckets principales ---')
	for i, bloque in enumerate(search2.blocks):
		print(f'Bucket {i}: {bloque}')
	print('--- Overflow ---')
	for i, ov in enumerate(search2.overflow):
		if ov:
			print(f'Overflow[{i}]: {ov}')

	# ============================================
	# Ejemplo 3: TruncationHash
	# ============================================
	print('\n\n=== HashExternalSearch con TruncationHash (posiciones [1,2]) ===')

	hash_trunc = TruncationHash([1, 2])
	search3 = HashExternalSearch(hash_trunc)
	search3.create(5, 2)

	valores3 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 11, 22, 33]
	print('\n--- Insertando valores ---')
	for v in valores3:
		pos = search3.insert(str(v).zfill(2))
		print(f'Insertado {v:02d} en posición global {pos}')

	print('\n--- Buckets principales ---')
	for i, bloque in enumerate(search3.blocks):
		print(f'Bucket {i}: {bloque}')
	print('--- Overflow ---')
	for i, ov in enumerate(search3.overflow):
		if ov:
			print(f'Overflow[{i}]: {ov}')

	# ============================================
	# Ejemplo 4: FoldingHash (suma)
	# ============================================
	print('\n\n=== HashExternalSearch con FoldingHash (group_size=1, suma) ===')
	hash_fold = FoldingHash(group_size=1, operation='sum')
	search4 = HashExternalSearch(hash_fold)
	search4.create(10, 2)

	valores4 = [13, 26, 39, 42, 55, 68, 71, 84, 97, 11, 24, 37]
	print('\n--- Insertando valores ---')
	for v in valores4:
		pos = search4.insert(str(v).zfill(2))
		print(f'Insertado {v:02d} en posición global {pos}')

	print('\n--- Buckets principales ---')
	for i, bloque in enumerate(search4.blocks):
		print(f'Bucket {i}: {bloque}')
	print('--- Overflow ---')
	for i, ov in enumerate(search4.overflow):
		if ov:
			print(f'Overflow[{i}]: {ov}')

		# ============================================
	# Ejemplo 5: BaseConversionHash (base 7)
	# ============================================
	print('\n\n=== HashExternalSearch con BaseConversionHash (base 7) ===')
	hash_base7 = BaseConversionHash(7)
	search5 = HashExternalSearch(hash_base7)
	search5.create(27, 4)

	clave_ejemplo = "7259"
	pos = search5.insert(clave_ejemplo)
	print(f'Insertado {clave_ejemplo} en posición global {pos}')

	valores5 = ["1234", "5678", "9012", "3456"]
	for v in valores5:
		pos = search5.insert(v)
		print(f'Insertado {v} en posición global {pos}')

	print('\n--- Buckets principales ---')
	for i, bloque in enumerate(search5.blocks):
		print(f'Bucket {i}: {bloque}')
	print('--- Overflow ---')
	for i, ov in enumerate(search5.overflow):
		if ov:
			print(f'Overflow[{i}]: {ov}')

	res = search5.search("7259")
	if res:
		print(f'\n7259 encontrado en: global {res[0]["global_position"]}, bloque {res[0]["block_index"]}, posición {res[0]["block_position"]}')

if __name__ == '__main__':
	demo_hash_external()
