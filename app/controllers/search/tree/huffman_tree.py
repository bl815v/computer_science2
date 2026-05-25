"""
Expose API endpoints for Huffman tree operations.

This module defines all FastAPI routes required to interact with
the Huffman tree search service. The router allows clients to:

    - Create a Huffman tree from a text input.
    - Search characters inside the tree.
    - Retrieve generated Huffman codes.
    - Retrieve the frequency table.
    - Retrieve the construction steps of the algorithm.
    - Generate and download visual representations of the tree.
    - Generate highlighted search visualizations.

The implementation delegates all Huffman logic to
`HuffmanSearchService`.

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

from app.controllers.search.snapshot import SnapshotRequest
from app.services.search.tree.huffman_tree import HuffmanSearchService

router = APIRouter(prefix='/huffman', tags=['Huffman Tree'])


class HuffmanCreateRequest(BaseModel):
	"""Represent request body for Huffman tree creation.

	Attributes:
	    text (str):
	        Input text used to generate the Huffman tree.

	"""

	text: str


service = HuffmanSearchService()


@router.post('/create')
async def create_huffman(request: HuffmanCreateRequest):
	"""Create a Huffman tree from the provided text.

	The endpoint generates the Huffman tree, computes character
	frequencies, assigns binary codes, and stores all internal
	structures inside the service instance.

	Args:
	    request (HuffmanCreateRequest):
	        Request containing the source text.

	Returns:
	    dict:
	        Dictionary containing the generated Huffman data.

	Raises:
	    HTTPException:
	        If an unexpected error occurs during tree creation.

	"""
	try:
		return service.create(request.text)

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get('/search/{letter}')
async def search_letter(letter: str):
	"""Search for a character inside the Huffman tree.

	The search returns the Huffman code and positional information
	associated with the specified character.

	Args:
	    letter (str):
	        Character to search in the Huffman tree.

	Returns:
	    dict:
	        Search result containing:

	            - message:
	                Human-readable operation result.

	            - position:
	                Huffman search information or an empty list
	                if the character does not exist.

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
	"""Retrieve all generated Huffman codes.

	Returns:
	    dict:
	        Mapping between characters and their Huffman codes.

	        Returns a message if the tree has not been initialized.

	"""
	if not service.initialized:
		return {'message': 'Tree not initialized'}

	return service.get_codes()


@router.get('/table')
async def get_table():
	"""Retrieve the Huffman frequency table.

	The table contains each character together with its
	frequency inside the original input text.

	Returns:
	    dict:
	        Frequency table information.

	        Returns a message if the tree has not been initialized.

	"""
	if not service.initialized:
		return {'message': 'Tree not initialized'}

	return service.get_table()


@router.get('/steps')
async def get_steps():
	"""Retrieve the Huffman tree construction steps.

	The returned data describes the iterative process used
	to combine nodes and generate the final Huffman tree.

	Returns:
	    dict:
	        Step-by-step Huffman construction information.

	        Returns a message if the tree has not been initialized.

	"""
	if not service.initialized:
		return {'message': 'Tree not initialized'}

	return service.get_steps()


@router.get('/plot')
async def plot_tree():
	"""Generate and return a Huffman tree visualization.

	The generated image represents the complete Huffman tree
	structure, including node relationships and binary branches.

	Returns:
	    FileResponse:
	        PNG image containing the generated tree visualization.

	Raises:
	    HTTPException:
	        If the Huffman tree has not been initialized.

	"""
	if not service.initialized:
		raise HTTPException(status_code=400, detail='Tree not initialized')

	filename = 'huffman.png'
	service.generate_plot(filename)

	return FileResponse(filename, media_type='image/png')


@router.get('/search-plot/{letter}')
async def search_plot(letter: str):
	"""Generate a highlighted Huffman tree visualization.

	The generated image highlights the traversal path associated
	with the specified character inside the Huffman tree.

	Args:
	    letter (str):
	        Character to highlight in the visualization.

	Returns:
	    FileResponse:
	        PNG image containing the highlighted Huffman tree.

	Raises:
	    HTTPException:
	        If the Huffman tree has not been initialized.

	"""
	if not service.initialized:
		raise HTTPException(status_code=400, detail='Tree not initialized')

	filename = 'highlight.png'
	service.generate_search_plot(letter, filename)

	return FileResponse(filename, media_type='image/png')


@router.post('/export')
async def export_huffman():
	"""
	Export the current Huffman tree snapshot.

	This endpoint serializes the current Huffman tree state
	into a portable snapshot representation that can later
	be restored through the import endpoint.

	The exported snapshot includes:

	    - Original input text.
	    - Character frequencies.
	    - Generated Huffman codes.
	    - Internal tree structure.
	    - Service configuration and metadata.

	Returns:
	    dict:
	        Serialized snapshot containing the current
	        Huffman tree state and configuration.

	"""
	return service.save_state()


@router.post('/import')
async def import_huffman(request: SnapshotRequest):
	"""
	Restore the Huffman tree from a snapshot.

	This endpoint reconstructs the Huffman tree using
	a previously exported snapshot and restores all
	internal structures, generated codes, and metadata.

	After restoration, the Huffman service becomes fully
	operational and supports all search, visualization,
	and inspection endpoints.

	Args:
	    request (SnapshotRequest):
	        Request containing the serialized Huffman
	        snapshot data.

	Returns:
	    dict:
	        Serialized representation of the restored
	        Huffman tree state.

	Raises:
	    HTTPException:
	        If the provided snapshot is invalid,
	        incomplete, or incompatible with the
	        Huffman service structure.

	"""
	try:
		service.load_state(request.snapshot)
		return service.save_state()
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
