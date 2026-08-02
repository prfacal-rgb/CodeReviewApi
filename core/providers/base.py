from abc import ABC, abstractmethod
from typing import Generator


class BaseProvider(ABC):
    """
    Interfaz común para todos los proveedores de IA.

    Cada provider concreto implementa complete() y stream().
    Los que soportan visión también implementan complete_with_image().

    Equivalente al patrón Strategy: el comportamiento (qué API llamar)
    queda separado de la lógica de negocio (cómo armar el prompt).
    """

    @abstractmethod
    def complete(
        self,
        system: str,
        user: str,
        model: str,
        max_tokens: int,
    ) -> str:
        """Genera una respuesta completa (bloqueante)."""
        ...

    @abstractmethod
    def stream(
        self,
        system: str,
        user: str,
        model: str,
        max_tokens: int,
    ) -> Generator[str, None, None]:
        """Genera la respuesta en chunks (streaming)."""
        ...

    def supports_vision(self) -> bool:
        """Indica si el provider acepta input de imagen."""
        return False

    def complete_with_image(
        self,
        system: str,
        image_base64: str,
        mime_type: str,
        model: str,
        max_tokens: int,
    ) -> str:
        """
        Genera una respuesta a partir de una imagen.
        Solo disponible en providers con supports_vision() == True.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} no soporta visión. "
            "Elegí Anthropic o Google AI Studio."
        )
