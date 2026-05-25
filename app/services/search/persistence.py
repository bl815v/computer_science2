"""Shared JSON snapshot helpers for search structures.

Provide validation, envelope building, and tree/hash serialization
utilities used by the search services and controller import/export
endpoints.

Author: Juan Esteban Bedoya <jebedoyal@udistrital.edu.co>

This file is part of ComputerScience2 project.

ComputerScience2 is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

ComputerScience2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with ComputerScience2. If not, see <https://www.gnu.org/licenses/>.
"""

from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, Optional

SNAPSHOT_VERSION = 1
DELETED_MARKER = {'__deleted__': True}


class SnapshotError(ValueError):
	"""Raised when a snapshot is invalid, incompatible or corrupted."""


def build_snapshot(
	snapshot_type: str, config: Dict[str, Any], state: Dict[str, Any]
) -> Dict[str, Any]:
	"""
	Build a versioned snapshot envelope for persistence.

	This is the main entry point for exporting a structure state.

	A snapshot always follows this format:

	    {
	        "type": str,
	        "version": int,
	        "config": dict,
	        "state": dict
	    }

	Args:
	    snapshot_type (str):
	        Identifier of the structure (e.g., "huffman_tree").
	    config (Dict[str, Any]):
	        Structural configuration (size, encoding, parameters).
	    state (Dict[str, Any]):
	        Full runtime state (tree, data, metadata).

	Returns:
	    Dict[str, Any]:
	        Deep-copied snapshot ready for JSON serialization.

	"""
	return {
		'type': snapshot_type,
		'version': SNAPSHOT_VERSION,
		'config': deepcopy(config),
		'state': deepcopy(state),
	}


def validate_snapshot(snapshot: Any, expected_type: str) -> Dict[str, Any]:
	"""
	Validate and normalize a snapshot before restoration.

	This function ensures:
	    - Snapshot structure is correct.
	    - Type matches expected structure.
	    - Version is supported.
	    - Config and state are valid dictionaries.

	Args:
	    snapshot (Any):
	        Raw snapshot input (usually from JSON).
	    expected_type (str):
	        Expected structure type identifier.

	Returns:
	    Dict[str, Any]:
	        Normalized snapshot payload with guaranteed fields.

	Raises:
	    SnapshotError:
	        If snapshot is malformed, incompatible, or corrupted.

	"""
	if not isinstance(snapshot, dict):
		raise SnapshotError('Snapshot must be a JSON object')

	actual_type = snapshot.get('type')
	if actual_type != expected_type:
		raise SnapshotError(f'Snapshot type mismatch: expected {expected_type}, got {actual_type}')

	version = snapshot.get('version')
	if version != SNAPSHOT_VERSION:
		raise SnapshotError(f'Unsupported snapshot version: {version}')

	config = snapshot.get('config')
	state = snapshot.get('state')
	if not isinstance(config, dict) or not isinstance(state, dict):
		raise SnapshotError('Snapshot is corrupt: config and state must be objects')

	return {
		'type': actual_type,
		'version': version,
		'config': config,
		'state': state,
	}


def serialize_list(values: Iterable[Any]) -> list[Any]:
	"""
	Create a JSON-safe deep copy of a list-like structure.

	Used to ensure no references are preserved when exporting state.
	"""
	return deepcopy(list(values))


def serialize_binary_node(
	node: Any,
	extra_fields: Optional[Iterable[str]] = None,
) -> Optional[Dict[str, Any]]:
	"""
	Serialize a binary tree node into a JSON-compatible structure.

	This function recursively traverses a binary tree and converts it into
	a dictionary representation suitable for snapshots.

	Each node includes:
	    - letter (leaf value)
	    - binary (encoded value)
	    - index (internal identifier)
	    - left subtree
	    - right subtree
	    - optional extra metadata fields

	Args:
	    node (Any):
	        Binary tree node.
	    extra_fields (Optional[Iterable[str]]):
	        Additional attributes to include in snapshot.

	Returns:
	    Optional[Dict[str, Any]]:
	        Serialized node or None if node is empty.

	"""
	if node is None:
		return None

	payload: Dict[str, Any] = {
		'letter': getattr(node, 'letter', None),
		'binary': getattr(node, 'binary', None),
		'index': getattr(node, 'index', None),
		'left': serialize_binary_node(getattr(node, 'left', None), extra_fields),
		'right': serialize_binary_node(getattr(node, 'right', None), extra_fields),
	}

	for field in extra_fields or ():
		if hasattr(node, field):
			payload[field] = deepcopy(getattr(node, field))

	return payload


def deserialize_binary_node(
	node_data: Optional[Dict[str, Any]],
	node_factory: Callable[[Dict[str, Any]], Any],
) -> Any:
	"""
	Rebuild a binary tree from a serialized snapshot.

	This function restores the recursive structure by:
	    - Creating nodes via factory function.
	    - Reconstructing left and right children.

	Args:
	    node_data (Optional[Dict[str, Any]]):
	        Serialized node representation.
	    node_factory (Callable):
	        Function that creates a node from a dictionary.

	Returns:
	    Reconstructed tree node or None.

	"""
	if node_data is None:
		return None

	node = node_factory(node_data)
	node.left = deserialize_binary_node(node_data.get('left'), node_factory)
	node.right = deserialize_binary_node(node_data.get('right'), node_factory)
	return node


def hash_function_to_snapshot(hash_func: Any) -> Dict[str, Any]:
	"""
	Convert a hash function instance into a snapshot format.

	This allows persistence of:
	    - hashing strategy type
	    - configuration parameters

	Supported types:
	    - ModHash
	    - SquareHash
	    - TruncationHash
	    - FoldingHash
	    - BaseConversionHash
	"""
	from app.services.search.hash.hash_function import (
		FoldingHash,
		ModHash,
		SquareHash,
		TruncationHash,
	)

	if isinstance(hash_func, ModHash):
		return {'type': 'mod'}

	if isinstance(hash_func, SquareHash):
		return {'type': 'square'}

	if isinstance(hash_func, TruncationHash):
		return {'type': 'truncation', 'positions': deepcopy(hash_func.positions)}

	if isinstance(hash_func, FoldingHash):
		return {
			'type': 'folding',
			'group_size': hash_func.group_size,
			'operation': hash_func.operation,
		}

	from app.services.search.external.hash_external import BaseConversionHash

	if isinstance(hash_func, BaseConversionHash):
		return {'type': 'base_conversion', 'base': hash_func.base}

	raise SnapshotError(f'Unsupported hash function type: {type(hash_func).__name__}')


def hash_function_from_snapshot(hash_data: Dict[str, Any]):
	"""
	Reconstruct a hash function from snapshot data.

	Ensures that the original hashing strategy and parameters
	are fully restored.

	Raises:
	    SnapshotError if type is unknown or configuration is invalid.


	"""
	from app.services.search.hash.hash_function import (
		FoldingHash,
		ModHash,
		SquareHash,
		TruncationHash,
	)

	if not isinstance(hash_data, dict):
		raise SnapshotError('Hash function snapshot must be an object')

	hash_type = hash_data.get('type')
	if hash_type == 'mod':
		return ModHash()
	if hash_type == 'square':
		return SquareHash()
	if hash_type == 'truncation':
		positions = hash_data.get('positions')
		if not isinstance(positions, list) or not positions:
			raise SnapshotError('Truncation hash snapshot requires positions')
		return TruncationHash(positions)
	if hash_type == 'folding':
		group_size = hash_data.get('group_size')
		if not isinstance(group_size, int) or group_size <= 0:
			raise SnapshotError('Folding hash snapshot requires a positive group_size')
		return FoldingHash(group_size, hash_data.get('operation') or 'sum')
	if hash_type == 'base_conversion':
		from app.services.search.external.hash_external import BaseConversionHash

		base = hash_data.get('base')
		if not isinstance(base, int) or base <= 0:
			raise SnapshotError('Base conversion hash snapshot requires a positive base')
		return BaseConversionHash(base)

	raise SnapshotError(f'Unsupported hash function type: {hash_type}')


def collision_resolver_to_snapshot(resolver: Any) -> Optional[Dict[str, Any]]:
	"""
	Serialize a collision resolver for hash tables.

	Used when exporting hash-based structures that require:
	    - collision resolution strategy
	    - secondary hash function (if applicable)

	Supported resolvers:
	    - Linear probing
	    - Quadratic probing
	    - Double hashing
	"""
	if resolver is None:
		return None

	from app.services.search.hash.collision_simple import (
		DoubleHashResolver,
		LinearResolver,
		QuadraticResolver,
	)

	if isinstance(resolver, LinearResolver):
		return {'type': 'linear'}

	if isinstance(resolver, QuadraticResolver):
		return {'type': 'quadratic'}

	if isinstance(resolver, DoubleHashResolver):
		return {
			'type': 'double',
			'second_hash': hash_function_to_snapshot(resolver.second_hash),
		}

	raise SnapshotError(f'Unsupported collision resolver type: {type(resolver).__name__}')


def collision_resolver_from_snapshot(resolver_data: Optional[Dict[str, Any]], hash_func: Any):
	"""
	Reconstruct a collision resolver from snapshot data.

	This restores the probing strategy used in hash tables,
	including any secondary hash function if required.

	Raises:
	    SnapshotError if resolver type is unsupported.

	"""
	from app.services.search.hash.collision_simple import (
		DoubleHashResolver,
		LinearResolver,
		QuadraticResolver,
	)

	if resolver_data is None:
		return None
	if not isinstance(resolver_data, dict):
		raise SnapshotError('Collision resolver snapshot must be an object')

	resolver_type = resolver_data.get('type')
	if resolver_type == 'linear':
		return LinearResolver()
	if resolver_type == 'quadratic':
		return QuadraticResolver()
	if resolver_type == 'double':
		second_hash_data = resolver_data.get('second_hash')
		second_hash = hash_function_from_snapshot(second_hash_data)
		return DoubleHashResolver(second_hash)

	raise SnapshotError(f'Unsupported collision resolver type: {resolver_type}')
