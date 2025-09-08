from typing import Optional, List

class LinearSearchService:
    def __init__(self):
        self.data: List[Optional[str]] = []
        self.size = 0
        self.digits = 0
        self.initialized = False
        print("LinearSearchService initialized")

    def create(self, size: int, digits: int):
        if size <= 0:
            raise ValueError("Size must be positive")
        if digits <= 0:
            raise ValueError("Digits must be positive")
            
        self.size = size
        self.digits = digits
        self.data = [None] * size
        self.initialized = True
        print(f"Structure created: size={size}, digits={digits}")

    def insert(self, value: str) -> int:
        if not self.initialized:
            raise ValueError("Structure not initialized. Call create() first.")
            
        # Validar que el valor tenga el número correcto de dígitos
        if len(value) != self.digits:
            raise ValueError(f"Value must have exactly {self.digits} digits")
            
        # Validar que el valor sea numérico
        if not value.isdigit():
            raise ValueError("Value must be numeric")
            
        # Verificar si el valor ya existe
        if value in self.data:
            print(f"Value {value} already exists in data: {self.data}")
            raise ValueError(f"Value {value} already exists")
            
        try:
            index = self.data.index(None)
        except ValueError as exc:
            raise ValueError("No empty space available") from exc
            
        self.data[index] = value
        print(f"Value {value} inserted at position {index + 1}")
        return index + 1  # posición en 1-based

    def search(self, value: str) -> List[int]:
        if not self.initialized:
            return []
            
        # Validar que el valor tenga el número correcto de dígitos
        if len(value) != self.digits:
            return []
            
        # Validar que el valor sea numérico
        if not value.isdigit():
            return []
            
        return [i + 1 for i, v in enumerate(self.data) if v == value]

    def delete(self, value: str) -> List[int]:
        if not self.initialized:
            return []
            
        # Validar que el valor tenga el número correcto de dígitos
        if len(value) != self.digits:
            return []
            
        # Validar que el valor sea numérico
        if not value.isdigit():
            return []
            
        positions = []
        for i, v in enumerate(self.data):
            if v == value:
                self.data[i] = None
                positions.append(i + 1)
                
        print(f"Value {value} deleted from positions: {positions}")
        return positions
