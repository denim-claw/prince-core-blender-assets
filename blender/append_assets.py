"""Append one named reusable collection from a native Blender library.
Run inside Blender 4.5+. Collections in the Prince Core Kit were verified at origin.
"""
import bpy

def append_collection(library_path, collection_name, destination=None, link=False):
    """Append/link a collection into the current scene and return it.

    `link=False` embeds the collection and its dependencies; `link=True` keeps a
    library link to the source .blend. A destination Collection is optional.
    """
    with bpy.data.libraries.load(library_path, link=link) as (src, dst):
        if collection_name not in src.collections:
            raise KeyError(f'{collection_name!r} not found in {library_path}')
        dst.collections = [collection_name]
    collection = dst.collections[0]
    if collection is None:
        raise RuntimeError(f'Failed to load {collection_name!r}')
    parent = destination or bpy.context.scene.collection
    parent.children.link(collection)
    return collection

# Example in Blender Python console:
# from pathlib import Path
# kit = Path('/path/to/this-repository/blender')
# c = append_collection(str(kit / 'prince-core-people.blend'), 'White Ruler')
# c = append_collection(str(kit / 'prince-core-props.blend'), 'Net')
