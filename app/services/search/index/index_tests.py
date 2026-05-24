"""Tests :)."""

from app.services.search.index.multilevel_index import (
	MultilevelSecondaryIndexService,
)

service = MultilevelSecondaryIndexService()

service.configure(
	r=500000,
	block_size=4096,
	record_length=120,
	index_record_length=15,
)

result = service.calculate()

print(result)
