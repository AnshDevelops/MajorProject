def add_trait(state, char, key, val):
    if char not in state["characters"] or not key:
        return state
    state.setdefault("traits", {}).setdefault(char, {})[key] = val
    return state


def delete_trait(state, char, key):
    try:
        del state["traits"][char][key]
        if not state["traits"][char]:
            del state["traits"][char]
    except KeyError:
        pass
    return state


def character_traits(state, char):
    return state.get("traits", {}).get(char, {})
