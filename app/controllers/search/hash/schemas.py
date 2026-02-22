"""Define request models for configuring hash functions and collision strategies.

Provide structured validation for hash table configuration parameters
received from external clients (e.g., API requests). Use Pydantic models
to ensure type safety and optional parameter handling depending on the
selected hashing or collision resolution strategy.

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

from typing import List, Optional

from pydantic import BaseModel


class HashFunctionRequest(BaseModel):
	"""
	Represent hash function configuration parameters.

	Store the required and optional settings used to construct a hash
	function instance. Some fields are only required depending on the
	selected hash function type.

	Attributes:
	    type: Specify the hash function type. Supported values:
	        "mod", "square", "truncation", or "folding".
	    positions: Indicate digit positions used by the truncation method.
	    group_size: Define group size used by the folding method.
	    operation: Define folding operation ("sum" or "mul").

	"""

	type: str
	positions: Optional[List[int]] = None
	group_size: Optional[int] = None
	operation: Optional[str] = None


class CollisionStrategyRequest(BaseModel):
	"""
	Represent collision resolution strategy configuration parameters.

	Store the required and optional settings used to configure how
	collisions are resolved in a hash table.

	Attributes:
	    type: Specify the collision strategy. Supported values:
	        "linear", "quadratic", "double", or "chaining".
	    second_hash_type: Specify the secondary hash function type
	        required when using double hashing.

	"""

	type: str
	second_hash_type: Optional[str] = None
