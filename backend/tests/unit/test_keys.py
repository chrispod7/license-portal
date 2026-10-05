from app import keys

SECRET = "test-secret"


def test_generated_key_has_expected_shape():
    key = keys.generate_key("acme", SECRET)
    parts = key.split("-")
    assert parts[0] == "ACME"
    assert len(parts) == 5
    assert all(len(p) == 5 for p in parts[1:])
    assert all(c in keys.ALPHABET for p in parts[1:] for c in p)


def test_generated_key_is_well_formed():
    assert keys.is_well_formed(keys.generate_key("ACME", SECRET), SECRET)


def test_keys_are_unique():
    assert len({keys.generate_key("ACME", SECRET) for _ in range(1000)}) == 1000


def test_lowercase_and_whitespace_are_tolerated():
    key = keys.generate_key("ACME", SECRET)
    assert keys.is_well_formed(f"  {key.lower()}  ", SECRET)


def test_tampered_key_fails_checksum():
    key = keys.generate_key("ACME", SECRET)
    # Flip one character in the random body.
    i = 5
    swapped = "1" if key[i] != "1" else "2"
    tampered = key[:i] + swapped + key[i + 1 :]
    assert not keys.is_well_formed(tampered, SECRET)


def test_key_signed_with_other_secret_is_rejected():
    assert not keys.is_well_formed(keys.generate_key("ACME", "other"), SECRET)


def test_changing_sku_invalidates_key():
    key = keys.generate_key("ACME", SECRET)
    assert not keys.is_well_formed("OTHER" + key[4:], SECRET)


def test_garbage_is_rejected():
    for bad in ["", "hello", "ACME-11111-22222-33333", "ACME-IIIII-22222-33333-44444"]:
        assert not keys.is_well_formed(bad, SECRET)
