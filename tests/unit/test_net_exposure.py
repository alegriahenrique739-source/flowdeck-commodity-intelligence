from decimal import Decimal

from backend.app.services.positions import (
    FuturesExposureBucket,
    PhysicalExposureBucket,
    build_net_exposure,
)


def test_physical_only_exposure_is_preserved() -> None:
    result = build_net_exposure(
        [_physical_bucket("BRENT", "WTI", "2026-09", "CRUDE_BOOK", "500")],
        [],
    )

    bucket = result.buckets[0]

    assert bucket.hedge_index == "WTI"
    assert bucket.exposure_month == "2026-09"
    assert bucket.book == "CRUDE_BOOK"
    assert bucket.physical_exposure_bbl == Decimal("500")
    assert bucket.paper_exposure_bbl == Decimal("0")
    assert bucket.net_exposure_bbl == Decimal("500")
    assert bucket.label == "WTI 2026-09 / CRUDE_BOOK"


def test_futures_only_exposure_is_preserved() -> None:
    result = build_net_exposure([], [_futures_bucket("BRENT", "2026-10", "HEDGE", "-250")])

    bucket = result.buckets[0]

    assert bucket.hedge_index == "BRENT"
    assert bucket.physical_exposure_bbl == Decimal("0")
    assert bucket.paper_exposure_bbl == Decimal("-250")
    assert bucket.net_exposure_bbl == Decimal("-250")


def test_long_physical_plus_short_futures_nets_correctly() -> None:
    result = build_net_exposure(
        [_physical_bucket("BRENT", "BRENT", "2026-09", "CRUDE_BOOK", "1000")],
        [_futures_bucket("BRENT", "2026-09", "CRUDE_BOOK", "-400")],
    )

    assert result.buckets[0].net_exposure_bbl == Decimal("600")


def test_short_physical_plus_long_futures_nets_correctly() -> None:
    result = build_net_exposure(
        [_physical_bucket("WTI", "WTI", "2026-09", "CRUDE_BOOK", "-1000")],
        [_futures_bucket("WTI", "2026-09", "CRUDE_BOOK", "300")],
    )

    assert result.buckets[0].net_exposure_bbl == Decimal("-700")


def test_same_month_and_book_net_together() -> None:
    result = build_net_exposure(
        [_physical_bucket("BRENT", "BRENT", "2026-09", "CRUDE_BOOK", "1000")],
        [_futures_bucket("BRENT", "2026-09", "CRUDE_BOOK", "-1000")],
    )

    assert len(result.buckets) == 1
    assert result.buckets[0].net_exposure_bbl == Decimal("0")


def test_different_months_do_not_net_together() -> None:
    result = build_net_exposure(
        [_physical_bucket("BRENT", "BRENT", "2026-09", "CRUDE_BOOK", "1000")],
        [_futures_bucket("BRENT", "2026-10", "CRUDE_BOOK", "-1000")],
    )

    assert len(result.buckets) == 2
    assert {bucket.exposure_month for bucket in result.buckets} == {
        "2026-09",
        "2026-10",
    }


def test_different_books_do_not_net_together() -> None:
    result = build_net_exposure(
        [_physical_bucket("BRENT", "BRENT", "2026-09", "PHYSICAL", "1000")],
        [_futures_bucket("BRENT", "2026-09", "HEDGE", "-1000")],
    )

    assert len(result.buckets) == 2
    assert {bucket.book for bucket in result.buckets} == {"HEDGE", "PHYSICAL"}


def test_brent_and_wti_do_not_net_together() -> None:
    result = build_net_exposure(
        [_physical_bucket("BRENT", "BRENT", "2026-09", "CRUDE_BOOK", "1000")],
        [_futures_bucket("WTI", "2026-09", "CRUDE_BOOK", "-1000")],
    )

    assert len(result.buckets) == 2
    assert {bucket.hedge_index for bucket in result.buckets} == {"BRENT", "WTI"}


def test_absolute_net_and_gross_component_exposure_are_distinct() -> None:
    result = build_net_exposure(
        [_physical_bucket("BRENT", "BRENT", "2026-09", "CRUDE_BOOK", "600000")],
        [_futures_bucket("BRENT", "2026-09", "CRUDE_BOOK", "-500000")],
    )

    bucket = result.buckets[0]

    assert bucket.net_exposure_bbl == Decimal("100000")
    assert bucket.absolute_net_exposure_bbl == Decimal("100000")
    assert bucket.gross_component_exposure_bbl == Decimal("1100000")


def test_long_and_short_metrics_are_correct() -> None:
    result = build_net_exposure(
        [
            _physical_bucket("BRENT", "BRENT", "2026-09", "CRUDE_BOOK", "1000"),
            _physical_bucket("WTI", "WTI", "2026-09", "CRUDE_BOOK", "-1000"),
        ],
        [
            _futures_bucket("BRENT", "2026-09", "CRUDE_BOOK", "-400"),
            _futures_bucket("WTI", "2026-09", "CRUDE_BOOK", "300"),
        ],
    )

    brent = _bucket_for(result.buckets, "BRENT", "2026-09", "CRUDE_BOOK")
    wti = _bucket_for(result.buckets, "WTI", "2026-09", "CRUDE_BOOK")

    assert brent.long_exposure_bbl == Decimal("600")
    assert brent.short_exposure_bbl == Decimal("0")
    assert wti.long_exposure_bbl == Decimal("0")
    assert wti.short_exposure_bbl == Decimal("-700")


def test_portfolio_summary_metrics_are_correct() -> None:
    result = build_net_exposure(
        [
            _physical_bucket("BRENT", "BRENT", "2026-09", "CRUDE_BOOK", "1000"),
            _physical_bucket("WTI", "WTI", "2026-09", "CRUDE_BOOK", "-1000"),
        ],
        [
            _futures_bucket("BRENT", "2026-09", "CRUDE_BOOK", "-400"),
            _futures_bucket("WTI", "2026-09", "CRUDE_BOOK", "300"),
            _futures_bucket("BRENT", "2026-10", "HEDGE", "200"),
        ],
    )

    summary = result.summary

    assert summary.total_physical_exposure_bbl == Decimal("0")
    assert summary.total_paper_exposure_bbl == Decimal("100")
    assert summary.total_net_exposure_bbl == Decimal("100")
    assert summary.total_absolute_net_exposure_bbl == Decimal("1500")
    assert summary.total_gross_component_exposure_bbl == Decimal("2900")
    assert summary.total_long_exposure_bbl == Decimal("800")
    assert summary.total_short_exposure_bbl == Decimal("-700")
    assert summary.number_of_exposure_buckets == 3
    assert summary.largest_long_bucket is not None
    assert summary.largest_long_bucket.label == "BRENT 2026-09 / CRUDE_BOOK"
    assert summary.largest_long_bucket.net_exposure_bbl == Decimal("600")
    assert summary.largest_short_bucket is not None
    assert summary.largest_short_bucket.label == "WTI 2026-09 / CRUDE_BOOK"
    assert summary.largest_short_bucket.net_exposure_bbl == Decimal("-700")


def test_empty_inputs_return_controlled_empty_result() -> None:
    result = build_net_exposure([], [])

    assert result.buckets == ()
    assert result.summary.total_physical_exposure_bbl == Decimal("0")
    assert result.summary.total_paper_exposure_bbl == Decimal("0")
    assert result.summary.total_net_exposure_bbl == Decimal("0")
    assert result.summary.total_absolute_net_exposure_bbl == Decimal("0")
    assert result.summary.total_gross_component_exposure_bbl == Decimal("0")
    assert result.summary.total_long_exposure_bbl == Decimal("0")
    assert result.summary.total_short_exposure_bbl == Decimal("0")
    assert result.summary.number_of_exposure_buckets == 0
    assert result.summary.largest_long_bucket is None
    assert result.summary.largest_short_bucket is None


def _physical_bucket(
    commodity: str,
    pricing_index: str,
    pricing_month: str,
    book: str,
    net_exposure: str,
) -> PhysicalExposureBucket:
    signed_exposure = Decimal(net_exposure)
    long_exposure = signed_exposure if signed_exposure > 0 else Decimal("0")
    short_exposure = signed_exposure if signed_exposure < 0 else Decimal("0")
    return PhysicalExposureBucket(
        commodity=commodity,
        pricing_index=pricing_index,
        pricing_month=pricing_month,
        book=book,
        gross_physical_exposure_bbl=abs(signed_exposure),
        net_physical_exposure_bbl=signed_exposure,
        long_physical_exposure_bbl=long_exposure,
        short_physical_exposure_bbl=short_exposure,
    )


def _futures_bucket(
    commodity: str, contract_month: str, book: str, net_exposure: str
) -> FuturesExposureBucket:
    signed_exposure = Decimal(net_exposure)
    long_exposure = signed_exposure if signed_exposure > 0 else Decimal("0")
    short_exposure = signed_exposure if signed_exposure < 0 else Decimal("0")
    return FuturesExposureBucket(
        commodity=commodity,
        contract_month=contract_month,
        book=book,
        gross_exposure_bbl=abs(signed_exposure),
        net_exposure_bbl=signed_exposure,
        long_exposure_bbl=long_exposure,
        short_exposure_bbl=short_exposure,
    )


def _bucket_for(buckets, hedge_index: str, exposure_month: str, book: str):
    return next(
        bucket
        for bucket in buckets
        if bucket.hedge_index == hedge_index
        and bucket.exposure_month == exposure_month
        and bucket.book == book
    )
