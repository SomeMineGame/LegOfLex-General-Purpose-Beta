from nbtlib.tag import Byte, Short, Int, Long, Float, Double, String, List, Compound

async def nbt_to_json(nbt_obj):
    if isinstance(nbt_obj, Compound):
        return {k: await nbt_to_json(v) for k, v in nbt_obj.items()}
    elif isinstance(nbt_obj, List):
        return [await nbt_to_json(v) for v in nbt_obj]
    elif hasattr(nbt_obj, 'value'):
        return await nbt_to_json(nbt_obj.value)
    else:
        return nbt_obj


async def json_to_nbt(obj):
    if isinstance(obj, dict):
        return Compound({k: await json_to_nbt(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return List([await json_to_nbt(i) for i in obj])
    elif isinstance(obj, bool):
        return Byte(1 if obj else 0)
    elif isinstance(obj, int):
        return Int(obj)
    elif isinstance(obj, float):
        return Double(obj)
    elif isinstance(obj, str):
        return String(obj)
    else:
        raise TypeError(f"Unsupported type for NBT conversion: {type(obj)}")
