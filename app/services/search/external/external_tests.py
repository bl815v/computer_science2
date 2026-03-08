from app.services.search.external.binary_external import BinaryExternalSearch


def main():
	search = BinaryExternalSearch()

	print('Inicializando estructura con tamaño 27 y dígitos 2...')
	search.create(27, 2)

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

	print('\n--- Insertando valores ---')
	for v in valores:
		pos = search.insert(str(v).zfill(2))
		print(f'Insertado {v:02d} en posición inicial {pos}')

	print('\n--- Estado final de los bloques ---')
	for i, bloque in enumerate(search.blocks):
		print(f'Bloque {i}: {bloque}')

	print('\n--- Búsquedas detalladas ---')
	busquedas = [16, 42, 70, 99]
	for val in busquedas:
		v_str = str(val).zfill(2)
		resultados = search.search(v_str)
		if resultados:
			for r in resultados:
				print(
					f'Valor {v_str} encontrado: '
					f'bloque {r["block_index"]}, '
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
			print(f'Eliminado {v_str} de posición(es) global(es) {eliminados}')
		else:
			print(f'Valor {v_str} no encontrado para eliminar')

	print('\n--- Estado después de eliminaciones ---')
	for i, bloque in enumerate(search.blocks):
		print(f'Bloque {i}: {bloque}')

	print('\n--- Verificación de eliminados ---')
	for val in eliminar:
		v_str = str(val).zfill(2)
		if search.search(v_str):
			print(f'Error: {v_str} todavía presente')
		else:
			print(f'{v_str} correctamente eliminado')


if __name__ == '__main__':
	main()
