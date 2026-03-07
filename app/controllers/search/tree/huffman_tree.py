"""Huffman tree API router.

Expose FastAPI endpoints for creating and interacting with a
Huffman tree structure. The API allows users to:

- Build a Huffman tree from an input text.
- Search for characters inside the tree.
- Retrieve the generated Huffman codes.
- Retrieve the Huffman frequency table.
- Retrieve the step-by-step construction process.
- Generate visualizations of the tree.
- Generate visualizations highlighting searched characters.

The module uses an adapter service (`HuffmanSearchService`) to integrate the
`HuffmanTree` implementation with the project's `BaseSearchService` interface.

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

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.search.base_search import BaseSearchService
from app.services.search.tree.huffman_tree import HuffmanTree

router = APIRouter(prefix='/huffman', tags=['Huffman Tree'])


class HuffmanCreateRequest(BaseModel):
	"""Request body for Huffman tree creation.

	Attributes:
		text (str): Input text used to build the Huffman tree.

	"""

	text: str


class HuffmanSearchService(BaseSearchService):
	"""Adapter service that integrates HuffmanTree with BaseSearchService.

	This class acts as a bridge between the Huffman tree implementation and the
	generic search service interface used across the project.

	Attributes:
		tree (HuffmanTree | None): Huffman tree instance.
		initialized (bool): Indicates whether the tree has been created.
		size (int): Number of unique characters in the tree.
		digits (int): Fixed value used for compatibility with BaseSearchService.
		data (dict): Dictionary containing Huffman codes for characters.

	"""

	def __init__(self):
		"""Initialize an empty Huffman search service."""
		self.tree: HuffmanTree | None = None
		self.initialized = False
		self.size = 0
		self.digits = 1
		self.data = {}

	def create(self, text: str):
		"""Create a Huffman tree from the given text.

		Args:
			text (str): Input text used to build the tree.

		"""
		self.tree = HuffmanTree(text)
		self.initialized = True
		self.size = self.tree.size
		self.data = self.tree.data

	def search(self, value: str):
		"""Search for a character in the Huffman tree.

		Args:
			value (str): Character to search.

		Returns:
			list: List containing the position(s) of the character in the tree.

		"""
		if self.tree is None:
			return []
		return self.tree.search(value)


service = HuffmanSearchService()


@router.post('/create')
async def create_huffman(request: HuffmanCreateRequest):
	"""Create a Huffman tree from the provided text.

	Args:
		request (HuffmanCreateRequest): Request containing the input text.

	Returns:
		dict: Information about the created Huffman tree including:
			- message: Confirmation message.
			- text: Original input text.
			- frequencies: Character frequency dictionary.
			- codes: Huffman code mapping.

	"""
	try:
		service.create(request.text)

		return {
			'message': 'Huffman tree created',
			'text': request.text,
			'frequencies': service.tree.freq_dict,
			'codes': service.tree.letter_to_code,
		}

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/search/{letter}')
async def search_letter(letter: str):
	"""Search for a character in the Huffman tree.

	Args:
		letter (str): Character to search.

	Returns:
		dict: Search result containing:
			- message: Status message.
			- position: List with character position(s).

	"""
	if not service.initialized:
		return {'message': 'Tree not initialized', 'position': []}

	result = service.search(letter)

	if result:
		return {
			'message': f"Character '{letter}' found",
			'position': result,
		}

	return {
		'message': f"Character '{letter}' not found",
		'position': [],
	}


@router.get('/codes')
async def get_codes():
	"""Return the Huffman codes generated for each character.

	Returns:
		dict: Dictionary mapping characters to their Huffman codes.

	"""
	if not service.initialized:
		return {'message': 'Tree not initialized'}

	return service.tree.letter_to_code


@router.get('/table')
async def get_table():
	"""Return the Huffman frequency table.

	Returns:
		dict | list: Representation of the frequency table.

	"""
	if not service.initialized:
		return {'message': 'Tree not initialized'}

	return service.tree.show_table()


@router.get('/steps')
async def get_steps():
	"""Return the step-by-step Huffman tree construction.

	Returns:
		list: List of steps used to build the Huffman tree.

	"""
	if not service.initialized:
		return {'message': 'Tree not initialized'}

	return service.tree.show_steps()


@router.get('/plot')
async def plot_tree():
	"""Generate and return a visualization of the Huffman tree.

	Returns:
		FileResponse: PNG image containing the tree visualization.

	Raises:
		HTTPException: If the tree has not been initialized.

	"""
	if not service.initialized:
		raise HTTPException(status_code=400, detail='Tree not initialized')

	filename = 'huffman.png'
	service.tree.plot(filename)

	return FileResponse(filename, media_type='image/png')


@router.get('/search-plot/{letter}')
async def search_plot(letter: str):
	"""Generate a visualization highlighting a searched character.

	Args:
		letter (str): Character to highlight.

	Returns:
		FileResponse: PNG image of the highlighted tree.

	Raises:
		HTTPException: If the tree has not been initialized.

	"""
	if not service.initialized:
		raise HTTPException(status_code=400, detail='Tree not initialized')

	filename = 'highlight.png'
	service.tree.search_plot(letter, filename)

	return FileResponse(filename, media_type='image/png')
