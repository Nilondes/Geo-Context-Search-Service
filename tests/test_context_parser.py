from app.services.context_parser import parse_context


def test_buy_cat_food_at_champion():
    txt = "Купить корм кошке в Чемпионе"
    parsed = parse_context(txt)
    assert parsed.category == "зоомагазин"
    assert parsed.brand is not None
    assert "чемпион" in parsed.brand.lower()


def test_go_to_titan_arena():
    txt = "Заехать в Титан-Арену"
    parsed = parse_context(txt)
    # may detect as brand or category 'арена'
    assert parsed.brand is not None or parsed.category == "арена"
    if parsed.brand:
        assert "титан" in parsed.brand.lower()


def test_buy_medicine_on_troitsky():
    txt = "Купить лекарства в аптеке на Троицком"
    parsed = parse_context(txt)
    assert parsed.category == "аптека"
    assert parsed.street is not None
    assert "троицк" in parsed.street.lower()


def test_order_cake():
    txt = "Заказать торт"
    parsed = parse_context(txt)
    assert parsed.category == "кондитерская"


def test_buy_groceries_in_magnit():
    txt = "Купить продукты в Магните"
    parsed = parse_context(txt)
    assert parsed.category == "продукты"
    assert parsed.brand is not None
    assert "магнит" in parsed.brand.lower()


def test_buy_cake_on_voskresenskaya():
    txt = "Заказать торт на Воскресенской"
    parsed = parse_context(txt)
    assert parsed.category == "кондитерская"
    assert parsed.street is not None
    assert "воскресен" in parsed.street.lower()


def test_go_to_titan_arena_without_dash():
    txt = "Заехать в Титан Арену"
    parsed = parse_context(txt)
    assert parsed.brand is not None or parsed.category == "арена"
