"""
Provide a factory function to build hash function strategies.

Create concrete hash function instances based on validated request data.
Raise HTTP exceptions when required configuration parameters are missing
or when the requested hash type is not supported.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>

This file is part of ComputerScience2 project.

ComputerScience2 is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

ComputerScience2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with ComputerScience2. If not, see <https://www.gnu.org/licenses/>.
"""

from fastapi import HTTPException

from app.services.search.hash.hash_function import (
	FoldingHash,
	ModHash,
	SquareHash,
	TruncationHash,
)

from .schemas import HashFunctionRequest


def build_hash_function(request: HashFunctionRequest):
	"""
	Build and return a hash function instance from request configuration.

	Select the appropriate hash function implementation according to the
	provided type. Validate required parameters for specific strategies
	and raise an HTTP 400 error if configuration is invalid.

	Args:
		request: Contain hash function configuration parameters.

	Returns:
		HashFunction: Concrete hash function implementation.

	Raises:
		HTTPException: If required parameters are missing or the hash
			function type is not supported.

	"""
	if request.type == 'mod':
		return ModHash()

	if request.type == 'square':
		return SquareHash()

	if request.type == 'truncation':
		if not request.positions:
			raise HTTPException(status_code=400, detail='Se requieren posiciones')
		return TruncationHash(request.positions)

	if request.type == 'folding':
		if not request.group_size:
			raise HTTPException(status_code=400, detail='Se requiere group_size')
		return FoldingHash(request.group_size, request.operation or 'sum')

	raise HTTPException(status_code=400, detail='Tipo de hash no válido')
