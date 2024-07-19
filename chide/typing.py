from typing import TypeAlias, Any, Callable, Type, Hashable

#: A dictionary of attributes that can be used to create a sample object
Attrs: TypeAlias = dict[str, Any]

#: A callable for uniquely identifying a sample object in a :class:`~chide.Set`
Identifier: TypeAlias = Callable[[Type[Any], Attrs], Hashable | None]
