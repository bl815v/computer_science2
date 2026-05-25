"""Base abstract service for search structures with fixed-size numeric keys.

Define the BaseSearchService abstract class, which provides common
behavior for search-based data structures that store fixed-length
numeric string keys. It includes validation logic, insertion, deletion,
automatic sorting, and structural initialization. Concrete search strategies
must implement the `search` method to define how keys are located within
the internal structure.

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

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.services.search.persistence import build_snapshot, validate_snapshot


class BaseSearchService(ABC):
	"""Abstract base class for fixed-size search structures.

	This class provides shared functionality for managing a search
	structure that stores numeric string keys of fixed length. It handles
	structure initialization, validation, insertion, deletion, and
	automatic ordering of elements.

	Attributes:
		data (List[Optional[str]]): Internal storage for the keys.
			Empty positions are represented by None.
		size (int): Maximum number of elements the structure can store.
		digits (int): Required length of each numeric key.
		initialized (bool): Indicates whether the structure has been
			initialized using the create method.

	"""

	snapshot_type = 'base_search'

	def __init__(self) -> None:
		"""Initialize an empty, unconfigured search structure."""
		self.data: List[Optional[str]] = []
		self.size = 0
		self.digits = 0
		self.initialized = False

	def create(self, size: int, digits: int) -> None:
		"""Initialize the search structure with a fixed size and key length.

		Args:
			size (int): Maximum number of elements the structure can store.
			digits (int): Required number of digits for each key.

		Raises:
			ValueError: If size or digits is not a positive integer.

		"""
		if size <= 0:
			raise ValueError('El tamaño de la estructura debe ser un entero positivo')

		if digits <= 0:
			raise ValueError('La cantidad de dígitos debe ser un entero positivo')

		self.size = size
		self.digits = digits
		self.data = [None] * size
		self.initialized = True

	def _validate_structure(self) -> None:
		"""Validate that the structure has been initialized.

		Raises:
			ValueError: If the structure has not been initialized.

		"""
		if not self.initialized:
			raise ValueError('Estructura no inicializada')

	def _validate_value(self, value: str) -> None:
		"""Validate that a key meets the required format constraints.

		Args:
			value (str): The key to validate.

		Raises:
			ValueError: If the key does not have the required number
				of digits or contains non-numeric characters.

		"""
		if len(value) != self.digits:
			raise ValueError(f'La clave debe tener exactamente {self.digits} digitos')

		if not value.isdigit():
			raise ValueError('La clave debe ser un valor numérico')

	def insert(self, value: str) -> int:
		"""Insert a new key into the structure.

		The key is placed in the first available position and the
		structure is automatically sorted after insertion.

		Args:
			value (str): The numeric key to insert.

		Returns:
			int: The 1-based position where the key was initially inserted.

		Raises:
			ValueError: If the structure is not initialized, the key
				is invalid, already exists, or there is no available space.

		"""
		self._validate_structure()
		self._validate_value(value)

		if value in self.data:
			raise ValueError(f'La clave {value} ya existe en la estructura')

		try:
			index = self.data.index(None)
		except ValueError as exc:
			raise ValueError('No hay espacio disponible en la estructura') from exc

		self.data[index] = value
		self.sort()

		return index + 1

	def delete(self, value: str) -> List[int]:
		"""Delete all occurrences of a key from the structure.

		Args:
			value (str): The numeric key to delete.

		Returns:
			List[int]: A list of 1-based positions where the key
				was found and removed. Returns an empty list if
				the key is not present.

		Raises:
			ValueError: If the structure is not initialized.

		"""
		self._validate_structure()

		positions = self.search(value)

		if not positions:
			return []

		for pos in positions:
			self.data[pos - 1] = None

		self.sort()
		return positions

	def sort(self) -> None:
		"""Sort the structure while preserving empty positions at the end.

		Non-null values are sorted in ascending order and all None
		values are moved to the end of the internal list.

		Raises:
			ValueError: If the structure is not initialized.

		"""
		self._validate_structure()

		self.data = sorted(v for v in self.data if v is not None) + [None] * self.data.count(None)

	def reset(self) -> None:
		"""Reset the structure to its initial unconfigured state.

		Clear all stored data and restore the default configuration.
		Subclasses can override this method if they need to reset
		additional attributes.

		"""
		self.data = []
		self.size = 0
		self.digits = 0
		self.initialized = False

	def save_state(self) -> Dict[str, Any]:
		"""
		Generate a versioned snapshot of the current service state.

		This method builds a complete serialized representation of
		the structure using the global snapshot system. It combines:

			- Configuration metadata (size, digits, initialization state).
			- Internal data state (deep copy of stored values).

		The resulting snapshot is safe to persist and later restore
		using `load_state`.

		Returns:
			Dict[str, Any]:
				A JSON-serializable snapshot containing:
					- type: Snapshot type identifier.
					- config: Structural configuration.
					- state: Internal data representation.
					- versioning metadata (handled by build_snapshot).

		"""
		return build_snapshot(
			self.snapshot_type,
			self._snapshot_config(),
			self._snapshot_state(),
		)

	def load_state(self, snapshot: Dict[str, Any]) -> None:
		"""
		Restore the service from a previously exported snapshot.

		This method validates that the provided snapshot matches
		the expected structure type and delegates reconstruction
		of internal state to `_restore_snapshot`.

		The restoration process ensures:

			- Snapshot type compatibility is verified.
			- Configuration is applied before state reconstruction.
			- Internal structure is fully rebuilt in a consistent way.

		Args:
			snapshot (Dict[str, Any]):
				Previously generated snapshot created by `save_state`.

		Raises:
			SnapshotError:
				If the snapshot is invalid or does not match
				the expected structure type.

		"""
		payload = validate_snapshot(snapshot, self.snapshot_type)
		self._restore_snapshot(payload['config'], payload['state'])

	def _snapshot_config(self) -> Dict[str, Any]:
		"""
		Return the configuration block used in exported snapshots.

		This includes the structural parameters required to
		reconstruct the service state independently of runtime data.

		Returns:
			Dict[str, Any]:
				Configuration dictionary containing:
					- size: Maximum capacity of the structure.
					- digits: Required key length.
					- initialized: Whether the structure was active.

		"""
		return {
			'size': self.size,
			'digits': self.digits,
			'initialized': self.initialized,
		}

	def _snapshot_state(self) -> Dict[str, Any]:
		"""
		Return the internal state used in exported snapshots.

		This method captures a deep copy of the stored data to ensure
		immutability of the snapshot and avoid shared references.

		Returns:
			Dict[str, Any]:
				State dictionary containing:
					- data: Copy of the internal storage array.

		"""
		return {
			'data': deepcopy(self.data),
		}

	def _restore_snapshot(self, config: Dict[str, Any], state: Dict[str, Any]) -> None:
		"""
		Restore the base service state from a snapshot.

		This method reconstructs the internal structure using
		the provided configuration and state blocks. It is
		intended to be extended by subclasses to restore
		additional attributes.

		The restoration process:

			1. Rebuilds structural parameters (size, digits).
			2. Restores initialization flag.
			3. Restores stored data.

		Args:
			config (Dict[str, Any]):
				Configuration block from snapshot.

			state (Dict[str, Any]):
				State block containing stored data.

		"""
		self.size = int(config.get('size', 0))
		self.digits = int(config.get('digits', 0))
		self.initialized = bool(config.get('initialized', False))
		self.data = deepcopy(state.get('data', []))

	@abstractmethod
	def search(self, value: str) -> List[int]:
		"""Search for a key in the structure.

		This method must be implemented by subclasses to define
		the specific search strategy (e.g., linear search, binary search).

		Args:
			value (str): The numeric key to search for.

		Returns:
			List[int]: A list of 1-based positions where the key
				is found. Returns an empty list if the key is not present.

		"""
		pass
