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
